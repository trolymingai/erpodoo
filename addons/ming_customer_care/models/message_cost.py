# -*- coding: utf-8 -*-
from odoo import fields, models


class MingMessageCost(models.AbstractModel):
    _name = 'ming.message.cost'
    _description = 'Tính chi phí gửi tin Ming'

    def _get_config(self, partner=False):
        Config = self.env['ming.segment.config'].sudo()
        if partner and partner.ming_branch_id:
            config = Config.search(
                [('active', '=', True), ('branch_id', '=', partner.ming_branch_id.id)],
                order='id desc',
                limit=1,
            )
            if config:
                return config
        return Config.search(
            [('active', '=', True), ('branch_id', '=', False)],
            order='id desc',
            limit=1,
        )

    def _today_cost(self, channel):
        today = fields.Date.context_today(self)
        logs = self.env['ming.message.log'].sudo().search(
            [
                ('channel', '=', channel),
                ('create_date', '>=', fields.Datetime.to_datetime(today)),
                ('status', 'in', ('pending', 'sent', 'safe_mode')),
            ]
        )
        return sum(log.estimated_cost or 0.0 for log in logs)

    def estimate(self, channel, recipient_count=1, config=False, partner=False):
        config = config or self._get_config(partner=partner)
        currency = (config.message_currency if config else 'VND') or 'VND'
        unit_cost = 0.0
        monthly_cost = 0.0
        daily_budget = 0.0
        max_per_day = 0

        if config:
            if channel == 'sms':
                unit_cost = config.sms_unit_cost or 0.0
                monthly_cost = config.sms_monthly_package_cost or 0.0
                daily_budget = config.daily_sms_budget_limit or 0.0
                max_per_day = config.max_sms_per_day or 0
            elif channel == 'email':
                unit_cost = config.email_unit_cost or 0.0
                monthly_cost = config.email_monthly_package_cost or 0.0
                daily_budget = config.daily_email_budget_limit or 0.0
                max_per_day = config.max_email_per_day or 0

        estimated = unit_cost * recipient_count
        spent_today = self._today_cost(channel)
        remaining_budget = max(daily_budget - spent_today, 0.0) if daily_budget else 0.0
        missing_cost = unit_cost <= 0.0
        over_budget = bool(daily_budget and estimated > remaining_budget)
        sent_today = self.env['ming.message.log'].sudo().search_count(
            [
                ('channel', '=', channel),
                ('create_date', '>=', fields.Datetime.to_datetime(fields.Date.context_today(self))),
                ('status', 'in', ('pending', 'sent', 'safe_mode')),
            ]
        )
        over_daily_count = bool(max_per_day and sent_today + recipient_count > max_per_day)

        return {
            'currency': currency,
            'unit_cost': unit_cost,
            'monthly_cost': monthly_cost,
            'estimated_cost': estimated,
            'daily_budget': daily_budget,
            'spent_today': spent_today,
            'remaining_budget': remaining_budget,
            'missing_cost': missing_cost,
            'over_budget': over_budget,
            'over_daily_count': over_daily_count,
        }

    def check_budget(self, channel, recipient_count=1, config=False, partner=False):
        info = self.estimate(channel, recipient_count=recipient_count, config=config, partner=partner)
        if info['over_budget']:
            return False, 'Chi phí dự kiến vượt ngân sách gửi tin trong ngày.'
        if info['over_daily_count']:
            return False, 'Số lượng gửi dự kiến vượt giới hạn gửi trong ngày.'
        return True, False
