# -*- coding: utf-8 -*-
from odoo import _, fields, models, tools


class MingMessageService(models.AbstractModel):
    _name = 'ming.message.service'
    _description = 'Dịch vụ gửi SMS/Email/Lark Ming'

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

    def _split_whitelist(self, value):
        items = []
        for line in (value or '').replace(',', '\n').splitlines():
            item = line.strip()
            if item:
                items.append(item.lower())
        return items

    def _render_content(self, content, partner):
        text = content or ''
        phone = partner.phone or ''
        return (
            text.replace('{{ customer_name }}', partner.name or '')
            .replace('{{customer_name}}', partner.name or '')
            .replace('{{ phone }}', phone)
            .replace('{{phone}}', phone)
        )

    def _get_partner_phone(self, partner):
        if 'mobile' in partner._fields and partner.mobile:
            return partner.mobile
        return partner.phone or ''

    def _get_recipient(self, channel, partner):
        if channel == 'email':
            return (partner.email or '').strip()
        raw_phone = self._get_partner_phone(partner)
        local_phone, normalized_phone, is_valid = self.env['res.partner']._normalize_vn_phone(raw_phone)
        return normalized_phone or local_phone or (raw_phone or ''), is_valid

    def _log(self, vals, existing_log=False):
        if existing_log:
            existing_log.write(vals)
            return existing_log
        return self.env['ming.message.log'].sudo().create(vals)

    def send_message(
        self,
        partner,
        channel,
        body,
        subject=False,
        task=False,
        history=False,
        alert=False,
        recipient=False,
        confirmed_cost=False,
        existing_log=False,
    ):
        partner.ensure_one()
        config = self._get_config(partner=partner)
        safe_mode = config.safe_mode if config else True
        test_mode = config.test_mode if config else True
        cost_info = self.env['ming.message.cost'].estimate(channel, recipient_count=1, config=config, partner=partner)
        rendered_body = self._render_content(body, partner)
        if channel == 'email':
            resolved_recipient = (recipient or self._get_recipient(channel, partner) or '').strip()
            phone_valid = True
        elif channel == 'sms':
            resolved_recipient, phone_valid = self._get_recipient(channel, partner)
            resolved_recipient = recipient or resolved_recipient
        elif channel == 'lark':
            resolved_recipient = recipient or ''
            phone_valid = True
        else:
            resolved_recipient = recipient or ''
            phone_valid = True

        base_vals = {
            'partner_id': partner.id,
            'alert_id': alert.id if alert else (existing_log.alert_id.id if existing_log and existing_log.alert_id else False),
            'channel': channel,
            'recipient': resolved_recipient,
            'subject': subject,
            'content': rendered_body,
            'safe_mode': safe_mode,
            'test_mode': test_mode,
            'provider': (
                config.sms_provider
                if config and channel == 'sms'
                else 'odoo_mail'
                if channel == 'email'
                else 'lark_webhook'
                if channel == 'lark'
                else False
            ),
            'estimated_cost': cost_info['estimated_cost'],
            'currency': cost_info['currency'],
            'related_task_id': task.id if task else (existing_log.related_task_id.id if existing_log and existing_log.related_task_id else False),
            'related_history_id': history.id if history else (existing_log.related_history_id.id if existing_log and existing_log.related_history_id else False),
            'related_model': task._name if task else partner._name,
            'related_res_id': task.id if task else partner.id,
            'created_by': self.env.user.id,
        }

        if channel not in ('sms', 'email', 'lark'):
            return self._log(dict(base_vals, status='rejected', error_message='Kênh gửi không được hỗ trợ.'), existing_log)
        if channel == 'sms' and config and not config.send_sms_enabled:
            return self._log(
                dict(base_vals, status='rejected', error_message='Kênh SMS đang tắt trong cấu hình chi nhánh.'),
                existing_log,
            )
        if channel == 'email' and config and not config.send_email_enabled:
            return self._log(
                dict(base_vals, status='rejected', error_message='Kênh email đang tắt trong cấu hình chi nhánh.'),
                existing_log,
            )
        if channel == 'lark' and config and not config.send_lark_enabled:
            return self._log(
                dict(base_vals, status='rejected', error_message='Kênh Lark đang tắt trong cấu hình chi nhánh.'),
                existing_log,
            )

        if safe_mode:
            return self._log(
                dict(
                    base_vals,
                    status='safe_mode',
                    sent_at=fields.Datetime.now(),
                    error_message='SAFE_MODE: chỉ ghi log, không gửi thật và không phát sinh chi phí thật.',
                ),
                existing_log,
            )

        if channel == 'sms' and (not config or not config.sms_enabled):
            return self._log(dict(base_vals, status='rejected', error_message='SMS chưa được bật trong cấu hình.'), existing_log)
        if channel == 'email' and (not config or not config.email_enabled):
            return self._log(dict(base_vals, status='rejected', error_message='Email chưa được bật trong cấu hình.'), existing_log)

        if channel == 'sms':
            if not resolved_recipient or not phone_valid:
                partner.sudo().write({'ming_invalid_phone': True})
                return self._log(dict(base_vals, status='failed', error_message='Số điện thoại không hợp lệ.'), existing_log)
            if partner.ming_do_not_contact or not partner.ming_allow_sms:
                return self._log(
                    dict(base_vals, status='blocked_consent', error_message='Khách không cho phép SMS hoặc đang bật không liên hệ.'),
                    existing_log,
                )
            whitelist = self._split_whitelist(config.sms_test_whitelist)
            if test_mode and resolved_recipient.lower() not in whitelist:
                return self._log(
                    dict(
                        base_vals,
                        status='blocked_test_mode',
                        error_message='Chế độ kiểm thử đang bật, số nhận không nằm trong danh sách được phép.',
                    ),
                    existing_log,
                )

        if channel == 'email':
            if not resolved_recipient or not tools.single_email_re.match(resolved_recipient):
                partner.sudo().write({'ming_invalid_email': True})
                return self._log(dict(base_vals, status='failed', error_message='Email không hợp lệ hoặc bị thiếu.'), existing_log)
            if partner.ming_do_not_contact or not partner.ming_allow_email:
                return self._log(
                    dict(base_vals, status='blocked_consent', error_message='Khách không cho phép email hoặc đang bật không liên hệ.'),
                    existing_log,
                )
            whitelist = self._split_whitelist(config.email_test_whitelist)
            if test_mode and resolved_recipient.lower() not in whitelist:
                return self._log(
                    dict(
                        base_vals,
                        status='blocked_test_mode',
                        error_message='Chế độ kiểm thử đang bật, email nhận không nằm trong danh sách được phép.',
                    ),
                    existing_log,
                )

        if channel == 'lark':
            if not resolved_recipient:
                return self._log(
                    dict(base_vals, status='failed', error_message='Chi nhánh chưa cấu hình webhook Lark.'),
                    existing_log,
                )
            test_webhook = config.lark_test_branch_id.lark_webhook_url if config and config.lark_test_branch_id else False
            if test_mode and resolved_recipient != test_webhook:
                return self._log(
                    dict(
                        base_vals,
                        status='blocked_test_mode',
                        error_message='Chế độ kiểm thử chỉ cho phép webhook Lark test đã khai báo.',
                    ),
                    existing_log,
                )
            log = self._log(dict(base_vals, status='pending'), existing_log)
            result = self.env['ming.sms.provider'].send_lark(config, resolved_recipient, rendered_body)
            if result['success']:
                log.write(
                    {
                        'status': 'sent',
                        'sent_at': fields.Datetime.now(),
                        'provider_message_id': result.get('provider_message_id'),
                        'raw_response': result.get('raw_response'),
                    }
                )
            else:
                log.write({'status': 'provider_error', 'error_message': result.get('error_message'), 'raw_response': result.get('raw_response')})
            return log

        if cost_info['missing_cost']:
            return self._log(
                dict(
                    base_vals,
                    status='blocked_budget',
                    error_message='Chưa cấu hình chi phí gửi tin. Vui lòng nhập đơn giá SMS/Email trước khi gửi thật.',
                ),
                existing_log,
            )
        ok_budget, budget_message = self.env['ming.message.cost'].check_budget(
            channel,
            recipient_count=1,
            config=config,
            partner=partner,
        )
        if not ok_budget:
            return self._log(dict(base_vals, status='blocked_budget', error_message=budget_message), existing_log)
        if config.require_cost_confirmation and not confirmed_cost:
            return self._log(dict(base_vals, status='rejected', error_message='Chưa xác nhận chi phí gửi tin.'), existing_log)

        log = self._log(dict(base_vals, status='pending'), existing_log)
        if channel == 'email':
            try:
                self.env['mail.mail'].sudo().create(
                    {
                        'subject': subject or _('Ming Coffee & More'),
                        'body_html': '<p>%s</p>' % rendered_body.replace('\n', '<br/>'),
                        'email_to': resolved_recipient,
                        'email_from': config.default_email_from or config.smtp_sender_email or False,
                        'reply_to': config.default_reply_to or False,
                    }
                ).send()
                log.write({'status': 'sent', 'sent_at': fields.Datetime.now(), 'actual_cost': cost_info['estimated_cost']})
            except Exception as exc:
                log.write({'status': 'failed', 'error_message': str(exc)})
            return log

        result = self.env['ming.sms.provider'].send_sms(config, resolved_recipient, rendered_body)
        if result['success']:
            log.write(
                {
                    'status': 'sent',
                    'sent_at': fields.Datetime.now(),
                    'provider_message_id': result.get('provider_message_id'),
                    'actual_cost': cost_info['estimated_cost'],
                    'raw_response': result.get('raw_response'),
                }
            )
        else:
            log.write({'status': 'provider_error', 'error_message': result.get('error_message'), 'raw_response': result.get('raw_response')})
        return log
