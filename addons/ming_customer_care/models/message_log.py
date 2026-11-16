# -*- coding: utf-8 -*-
from odoo import _, fields, models


class MingMessageLog(models.Model):
    _name = 'ming.message.log'
    _description = 'Nhật ký gửi tin chăm sóc khách hàng'
    _order = 'create_date desc'

    partner_id = fields.Many2one('res.partner', index=True, string='Khách hàng')
    branch_id = fields.Many2one(
        'ming.branch',
        related='partner_id.ming_branch_id',
        store=True,
        index=True,
        readonly=True,
        string='Chi nhánh',
    )
    alert_id = fields.Many2one('ming.retention.alert', index=True, string='Cảnh báo liên quan')
    channel = fields.Selection([('sms', 'SMS'), ('email', 'Email'), ('lark', 'Lark')], required=True, index=True, string='Kênh gửi')
    recipient = fields.Char(string='Người nhận')
    subject = fields.Char(string='Tiêu đề')
    content = fields.Text(required=True, string='Nội dung')
    status = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('safe_mode', 'Chế độ an toàn'),
            ('blocked_test_mode', 'Chặn do test mode'),
            ('blocked_consent', 'Chặn do consent'),
            ('blocked_budget', 'Chặn do ngân sách'),
            ('pending', 'Đang gửi'),
            ('sent', 'Đã gửi'),
            ('failed', 'Thất bại'),
            ('rejected', 'Từ chối'),
            ('provider_error', 'Lỗi nhà cung cấp'),
            ('skipped', 'Bỏ qua'),
        ],
        default='draft',
        index=True,
        string='Trạng thái',
    )
    safe_mode = fields.Boolean(default=True, index=True, string='Chế độ an toàn')
    test_mode = fields.Boolean(default=True, index=True, string='Chế độ kiểm thử')
    provider = fields.Char(string='Nhà cung cấp')
    provider_message_id = fields.Char(string='Mã tin từ nhà cung cấp')
    error_message = fields.Text(string='Lỗi / ghi chú')
    estimated_cost = fields.Float(string='Chi phí ước tính')
    actual_cost = fields.Float(string='Chi phí thực tế')
    currency = fields.Char(default='VND', string='Tiền tệ')
    sent_at = fields.Datetime(string='Thời điểm gửi')
    created_by = fields.Many2one('res.users', default=lambda self: self.env.user, string='Người tạo')
    related_task_id = fields.Many2one('ming.care.task', index=True, string='Công việc liên quan')
    related_history_id = fields.Many2one('ming.care.history', index=True, string='Lịch sử CSKH liên quan')
    related_model = fields.Char(string='Model liên quan')
    related_res_id = fields.Integer(string='ID liên quan')
    raw_response = fields.Text(string='Phản hồi kỹ thuật')

    def name_get(self):
        result = []
        channel_labels = dict(self._fields['channel'].selection)
        for log in self:
            partner_name = log.partner_id.display_name or log.recipient or _('Không xác định')
            result.append((log.id, '%s - %s' % (channel_labels.get(log.channel, log.channel), partner_name)))
        return result

    def action_send(self):
        for log in self:
            if not log.partner_id:
                log.write({'status': 'failed', 'error_message': 'Thiếu khách hàng để gửi lại.'})
                continue
            self.env['ming.message.service'].send_message(
                log.partner_id,
                log.channel,
                log.content,
                subject=log.subject,
                task=log.related_task_id,
                history=log.related_history_id,
                alert=log.alert_id,
                recipient=log.recipient,
                confirmed_cost=True,
                existing_log=log,
            )
        return self
