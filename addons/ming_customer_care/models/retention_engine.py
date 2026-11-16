# -*- coding: utf-8 -*-
from datetime import timedelta
from math import ceil

from odoo import api, fields, models


class MingRetentionEngine(models.AbstractModel):
    _name = 'ming.retention.engine'
    _description = 'Ming Retention Engine'

    _DEFAULTS = {
        'active_days_threshold': 30,
        'lost_days_threshold': 90,
        'vip_percent': 10.0,
        'alert_2_after_days': 7,
        'alert_3_after_days': 14,
        'conversion_window_days': 30,
    }

    @api.model
    def _get_config_for_partner(self, partner):
        Config = self.env['ming.segment.config'].sudo()
        if partner.ming_branch_id:
            branch_config = Config.search(
                [
                    ('active', '=', True),
                    ('branch_id', '=', partner.ming_branch_id.id),
                ],
                order='id desc',
                limit=1,
            )
            if branch_config:
                return branch_config
        return Config.search(
            [
                ('active', '=', True),
                ('branch_id', '=', False),
            ],
            order='id desc',
            limit=1,
        )

    def _config_value(self, config, field_name):
        if config and config[field_name] is not False:
            return config[field_name]
        return self._DEFAULTS[field_name]

    def _vip_ranks(self, partners, configs):
        grouped = {}
        for partner in partners:
            config = configs.get(partner.id)
            key = config.id if config else 0
            grouped.setdefault(key, {'config': config, 'partners': self.env['res.partner']})
            grouped[key]['partners'] |= partner

        ranks = {}
        for values in grouped.values():
            eligible = values['partners'].filtered(lambda partner: (partner.ming_total_spent or 0.0) > 0)
            eligible = eligible.sorted(key=lambda partner: (-float(partner.ming_total_spent or 0.0), partner.id))
            percent = max(0.0, min(100.0, float(self._config_value(values['config'], 'vip_percent'))))
            vip_count = min(len(eligible), int(ceil(len(eligible) * percent / 100.0)))
            for rank, partner in enumerate(eligible, start=1):
                ranks[partner.id] = rank if rank <= vip_count else False
        return ranks

    def _alert_level(self, days_absent, status, config):
        if status == 'lost':
            return 'winback'
        if status != 'at_risk':
            return '0'
        active_days = int(self._config_value(config, 'active_days_threshold'))
        level_2_after = int(self._config_value(config, 'alert_2_after_days'))
        level_3_after = int(self._config_value(config, 'alert_3_after_days'))
        if days_absent <= active_days + level_2_after:
            return '1'
        if days_absent <= active_days + level_2_after + level_3_after:
            return '2'
        return '3'

    def _next_alert_date(self, today, alert_level, config):
        if alert_level == '1':
            return today + timedelta(days=int(self._config_value(config, 'alert_2_after_days')))
        if alert_level == '2':
            return today + timedelta(days=int(self._config_value(config, 'alert_3_after_days')))
        return False

    def _mark_converted_alerts(self, partner, last_transaction_date, config):
        if not last_transaction_date:
            return
        window_days = max(0, int(self._config_value(config, 'conversion_window_days')))
        oldest_trigger = last_transaction_date - timedelta(days=window_days)
        alerts = self.env['ming.retention.alert'].sudo().search(
            [
                ('partner_id', '=', partner.id),
                ('status', 'in', ('pending', 'sent', 'handled')),
                ('trigger_date', '<=', last_transaction_date),
                ('trigger_date', '>=', oldest_trigger),
            ]
        )
        for alert in alerts:
            alert.write({'status': 'converted', 'converted_at': fields.Datetime.now()})
            partner.write(
                {
                    'ming_has_returned': True,
                    'ming_returned_at': fields.Date.context_today(partner),
                }
            )
            if alert.care_task_id and alert.care_task_id.pipeline_status in ('pending', 'in_progress'):
                alert.care_task_id.action_done()

    @api.model
    def cron_run_retention_engine(self):
        today = fields.Date.context_today(self)
        partners = self.env['res.partner'].sudo().search(
            [
                ('active', '=', True),
                ('ming_last_transaction_date', '!=', False),
            ]
        )
        configs = {partner.id: self._get_config_for_partner(partner) for partner in partners}
        vip_ranks = self._vip_ranks(partners, configs)

        for partner in partners:
            config = configs.get(partner.id)
            days = (today - partner.ming_last_transaction_date).days
            old_status = partner.ming_activity_status
            active_days = int(self._config_value(config, 'active_days_threshold'))
            lost_days = int(self._config_value(config, 'lost_days_threshold'))
            status = 'active' if days <= active_days else ('at_risk' if days <= lost_days else 'lost')
            vip_rank = vip_ranks.get(partner.id) or False
            is_vip = bool(vip_rank)
            alert_level = self._alert_level(days, status, config)
            partner.write(
                {
                    'ming_days_absent': days,
                    'ming_activity_status': status,
                    'ming_is_vip': is_vip,
                    'ming_vip_rank': vip_rank,
                    'ming_alert_level': alert_level,
                }
            )
            self._mark_converted_alerts(partner, partner.ming_last_transaction_date, config)
            if status in ('at_risk', 'lost'):
                self._ensure_alert_and_task(partner, alert_level, is_vip, old_status, config)
        return True

    def _ensure_alert_and_task(self, partner, alert_level, is_vip, old_status, config=False):
        today = fields.Date.context_today(self)
        alert_type = (
            'vip_at_risk'
            if is_vip and partner.ming_activity_status == 'at_risk'
            else 'lost'
            if partner.ming_activity_status == 'lost'
            else 'at_risk'
        )
        task_type = (
            'vip_alert'
            if is_vip and partner.ming_activity_status == 'at_risk'
            else 'winback'
            if partner.ming_activity_status == 'lost'
            else 'at_risk'
        )
        alert_model = self.env['ming.retention.alert'].sudo()
        existing = alert_model.search(
            [
                ('partner_id', '=', partner.id),
                ('alert_level', '=', alert_level),
                ('status', 'in', ('pending', 'sent', 'handled')),
            ],
            limit=1,
        )
        task_model = self.env['ming.care.task'].sudo()
        task = task_model.search(
            [
                ('partner_id', '=', partner.id),
                ('task_type', '=', task_type),
                ('pipeline_status', 'in', ('pending', 'in_progress')),
            ],
            order='create_date asc, id asc',
            limit=1,
        )
        if existing and existing.care_task_id:
            return existing
        if existing and task:
            existing.care_task_id = task.id
            return existing
        task_values = {
            'due_date': today,
            'days_absent': partner.ming_days_absent,
            'alert_level': alert_level,
            'is_vip': is_vip,
            'total_spent': partner.ming_total_spent,
            'created_by_system': True,
            'source_reason': 'Tự tạo từ retention engine. Trạng thái cũ: %s' % old_status,
        }
        if task:
            task.write(task_values)
        else:
            task = task_model.create(
                dict(
                    task_values,
                    name='Chăm sóc %s - cảnh báo %s' % (partner.display_name, alert_level),
                    partner_id=partner.id,
                    task_type=task_type,
                    priority='3' if is_vip or alert_level == '3' else '1',
                )
            )

        if existing:
            existing.care_task_id = task.id
            return existing

        alert = alert_model.create(
            {
                'name': 'Cảnh báo %s - %s' % (alert_level, partner.display_name),
                'partner_id': partner.id,
                'alert_level': alert_level,
                'alert_type': alert_type,
                'trigger_date': today,
                'trigger_reason': 'days_absent=%s' % partner.ming_days_absent,
                'care_task_id': task.id,
                'next_alert_date': self._next_alert_date(today, alert_level, config),
            }
        )
        if alert_level in ('1', '2') and (not config or config.send_sms_enabled):
            alert.action_send_sms()
            if alert_level == '2' and (not config or config.send_email_enabled):
                alert.action_send_email()
        if (alert_level == '3' or alert_type == 'vip_at_risk') and (not config or config.send_lark_enabled):
            alert.action_send_lark()
        alert.status = 'sent'
        return alert
