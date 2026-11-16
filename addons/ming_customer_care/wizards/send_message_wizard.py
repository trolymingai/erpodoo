# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MingSendMessageWizard(models.TransientModel):
    _name = 'ming.send.message.wizard'
    _description = 'Soạn SMS/Email chăm sóc khách hàng'

    partner_id = fields.Many2one('res.partner', required=True, string='Khách hàng')
    task_id = fields.Many2one('ming.care.task', string='Công việc CSKH')
    channel = fields.Selection([('sms', 'SMS'), ('email', 'Email')], required=True, default='sms', string='Kênh gửi')
    template_key = fields.Selection(
        [
            ('return_invite', 'Mời khách quay lại'),
            ('vip_offer', 'Ưu đãi khách VIP'),
            ('callback_reminder', 'Nhắc hẹn gọi lại'),
            ('thank_you', 'Cảm ơn khách hàng'),
            ('feedback', 'Xin phản hồi trải nghiệm'),
            ('custom', 'Tự soạn'),
        ],
        default='return_invite',
        string='Mẫu nội dung',
    )
    subject = fields.Char(string='Tiêu đề email')
    body = fields.Text(required=True, string='Nội dung')
    recipient = fields.Char(compute='_compute_preview', string='Người nhận')
    consent_status = fields.Char(compute='_compute_preview', string='Trạng thái consent')
    safe_mode = fields.Boolean(compute='_compute_preview', string='Chế độ an toàn')
    test_mode = fields.Boolean(compute='_compute_preview', string='Chế độ kiểm thử')
    estimated_cost = fields.Float(compute='_compute_preview', string='Chi phí ước tính')
    currency = fields.Char(compute='_compute_preview', string='Tiền tệ')
    cost_note = fields.Text(compute='_compute_preview', string='Ghi chú chi phí')

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        partner_id = self.env.context.get('default_partner_id')
        task_id = self.env.context.get('default_task_id')
        channel = self.env.context.get('default_channel') or values.get('channel') or 'sms'
        if task_id and not partner_id:
            task = self.env['ming.care.task'].browse(task_id)
            partner_id = task.partner_id.id
        values.update({'partner_id': partner_id, 'task_id': task_id, 'channel': channel})
        body, subject = self._template_content(values.get('template_key') or 'return_invite', channel, partner_id)
        values.setdefault('body', body)
        values.setdefault('subject', subject)
        return values

    def _template_content(self, template_key, channel, partner_id=False):
        partner = self.env['res.partner'].browse(partner_id) if partner_id else self.env['res.partner']
        name = partner.name or '{{ customer_name }}'
        sms_templates = {
            'return_invite': 'Chào {{ customer_name }}, Ming Coffee & More cảm ơn anh/chị đã đồng hành. Khi tiện, anh/chị ghé Ming để bên em được phục vụ mình tốt hơn nhé.',
            'vip_offer': 'Chào {{ customer_name }}, Ming Coffee & More gửi lời cảm ơn anh/chị khách VIP. Bên em luôn sẵn sàng hỗ trợ khi anh/chị ghé lại.',
            'callback_reminder': 'Chào {{ customer_name }}, Ming Coffee & More nhắc lịch hẹn gọi lại với anh/chị. Bên em sẽ liên hệ theo đúng lịch đã hẹn.',
        }
        email_templates = {
            'thank_you': ('Cảm ơn anh/chị đã đồng hành cùng Ming', 'Chào {{ customer_name }},\n\nMing Coffee & More cảm ơn anh/chị đã đồng hành. Bên em rất mong tiếp tục được phục vụ anh/chị trong thời gian tới.'),
            'return_invite': ('Ming Coffee & More mời anh/chị quay lại', 'Chào {{ customer_name }},\n\nMing Coffee & More rất mong được gặp lại anh/chị. Khi thuận tiện, anh/chị ghé Ming để bên em được chăm sóc mình tốt hơn nhé.'),
            'feedback': ('Ming Coffee & More xin phản hồi trải nghiệm', 'Chào {{ customer_name }},\n\nMing Coffee & More mong nhận được phản hồi của anh/chị để cải thiện chất lượng phục vụ.'),
        }
        if channel == 'email':
            subject, body = email_templates.get(template_key, email_templates['return_invite'])
            return body.replace('{{ customer_name }}', name), subject
        return sms_templates.get(template_key, sms_templates['return_invite']).replace('{{ customer_name }}', name), False

    @api.onchange('template_key', 'channel', 'partner_id')
    def _onchange_template_key(self):
        for wizard in self:
            if wizard.template_key == 'custom':
                continue
            body, subject = wizard._template_content(wizard.template_key, wizard.channel, wizard.partner_id.id)
            wizard.body = body
            wizard.subject = subject

    @api.depends('partner_id', 'channel')
    def _compute_preview(self):
        for wizard in self:
            config = self.env['ming.message.service']._get_config(partner=wizard.partner_id)
            wizard.safe_mode = config.safe_mode if config else True
            wizard.test_mode = config.test_mode if config else True
            cost = self.env['ming.message.cost'].estimate(
                wizard.channel or 'sms',
                recipient_count=1,
                config=config,
                partner=wizard.partner_id,
            )
            wizard.estimated_cost = cost['estimated_cost']
            wizard.currency = cost['currency']
            if wizard.channel == 'email':
                wizard.recipient = wizard.partner_id.email or ''
                consent = 'Cho phép Email' if wizard.partner_id.ming_allow_email else 'Không cho phép Email'
            else:
                mobile = wizard.partner_id.mobile if 'mobile' in wizard.partner_id._fields else ''
                wizard.recipient = wizard.partner_id.ming_phone_normalized or wizard.partner_id.phone or mobile or ''
                consent = 'Cho phép SMS' if wizard.partner_id.ming_allow_sms else 'Không cho phép SMS'
            if wizard.partner_id.ming_do_not_contact:
                consent = 'Không liên hệ'
            wizard.consent_status = consent
            if wizard.safe_mode:
                wizard.cost_note = 'Chế độ an toàn đang bật. Hệ thống chỉ ghi nhật ký, không phát sinh chi phí gửi thật.'
            elif cost['missing_cost']:
                wizard.cost_note = 'Chưa cấu hình chi phí gửi tin. Vui lòng nhập đơn giá SMS/Email trước khi gửi thật.'
            elif cost['over_budget']:
                wizard.cost_note = 'Chi phí dự kiến vượt ngân sách gửi tin trong ngày.'
            else:
                wizard.cost_note = 'Chi phí ước tính: %.0f %s.' % (cost['estimated_cost'], cost['currency'])

    def _open_log(self, log):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nhật ký gửi tin',
            'res_model': 'ming.message.log',
            'res_id': log.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_send(self):
        self.ensure_one()
        config = self.env['ming.message.service']._get_config(partner=self.partner_id)
        safe_mode = config.safe_mode if config else True
        if config and config.require_cost_confirmation and not safe_mode:
            cost = self.env['ming.message.cost'].estimate(
                self.channel,
                recipient_count=1,
                config=config,
                partner=self.partner_id,
            )
            return {
                'type': 'ir.actions.act_window',
                'name': 'Xác nhận chi phí gửi tin',
                'res_model': 'ming.message.cost.confirm.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_send_wizard_id': self.id,
                    'default_channel': self.channel,
                    'default_recipient_count': 1,
                    'default_unit_cost': cost['unit_cost'],
                    'default_monthly_cost': cost['monthly_cost'],
                    'default_estimated_cost': cost['estimated_cost'],
                    'default_remaining_budget': cost['remaining_budget'],
                    'default_currency': cost['currency'],
                    'default_warning_message': self.cost_note,
                },
            }
        log = self.env['ming.message.service'].send_message(
            self.partner_id,
            self.channel,
            self.body,
            subject=self.subject,
            task=self.task_id,
            confirmed_cost=False,
        )
        return self._open_log(log)

    def action_send_confirmed(self):
        self.ensure_one()
        log = self.env['ming.message.service'].send_message(
            self.partner_id,
            self.channel,
            self.body,
            subject=self.subject,
            task=self.task_id,
            confirmed_cost=True,
        )
        return self._open_log(log)
