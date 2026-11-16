# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


CALL_STATUSES = [
    ('will_return', 'Đã liên hệ - Sẽ ghé lại'),
    ('no_need', 'Đã liên hệ - Không có nhu cầu'),
    ('moved_to_other_shop', 'Đã liên hệ - Đã chuyển quán khác'),
    ('negative_feedback', 'Đã liên hệ - Phản hồi tiêu cực'),
    ('no_answer', 'Không bắt máy'),
    ('wrong_number', 'Sai số / không liên lạc được'),
    ('callback_2', 'Đã gọi - Hẹn gọi lại lần 2'),
    ('sent_offer', 'Đã gửi ưu đãi quay lại'),
    ('follow_up', 'Đã chăm sóc - Theo dõi tiếp'),
]


class MingCareHistory(models.Model):
    _name = 'ming.care.history'
    _description = 'Lịch sử chăm sóc khách hàng'
    _inherit = ['mail.thread']
    _order = 'call_datetime desc'

    partner_id = fields.Many2one('res.partner', required=True, index=True, string='Khách hàng')
    branch_id = fields.Many2one(related='partner_id.ming_branch_id', store=True, index=True, string='Chi nhánh')
    task_id = fields.Many2one('ming.care.task', index=True, string='Công việc liên quan')
    call_datetime = fields.Datetime(default=fields.Datetime.now, required=True, string='Thời điểm chăm sóc')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True, string='Người thực hiện')
    role = fields.Selection([('staff', 'Nhân viên CSKH'), ('manager', 'Quản lý')], default='staff', string='Vai trò')
    user_role_snapshot = fields.Selection(
        [('staff', 'Nhân viên CSKH'), ('manager', 'Quản lý')],
        readonly=True,
        string='Vai trò tại thời điểm ghi nhận',
    )
    pipeline_state_snapshot = fields.Selection(
        [
            ('pending', 'Chưa xử lý'),
            ('in_progress', 'Đang xử lý'),
            ('done', 'Đã hoàn tất'),
            ('cancelled', 'Đã hủy'),
        ],
        readonly=True,
        string='Trạng thái công việc lúc ghi nhận',
    )
    call_status = fields.Selection(CALL_STATUSES, required=True, index=True, string='Kết quả chăm sóc')
    lost_reason = fields.Selection(
        [
            ('price', 'Giá'),
            ('location', 'Vị trí'),
            ('quality', 'Chất lượng'),
            ('service', 'Thái độ phục vụ'),
            ('space', 'Không gian'),
            ('moved', 'Chuyển nơi ở/làm việc'),
            ('other_shop', 'Chuyển quán khác'),
            ('unknown', 'Không rõ'),
            ('other', 'Khác'),
        ],
        string='Lý do mất khách',
    )
    note = fields.Text(string='Ghi chú')
    follow_up_date = fields.Date(string='Ngày hẹn gọi lại')
    manager_action_type = fields.Selection(
        [
            ('complaint_done', 'Đã xử lý khiếu nại'),
            ('voucher', 'Đã tặng voucher bù'),
            ('direct_meeting', 'Đã gặp trực tiếp'),
            ('other', 'Khác'),
        ],
        string='Hướng xử lý của quản lý',
    )

    def name_get(self):
        result = []
        status_labels = dict(self._fields['call_status'].selection)
        for rec in self:
            partner_name = rec.partner_id.display_name or 'Khách hàng'
            status_name = status_labels.get(rec.call_status, rec.call_status or 'CSKH')
            call_date = fields.Datetime.to_string(rec.call_datetime)[:16] if rec.call_datetime else ''
            result.append((rec.id, '%s - %s%s' % (partner_name, status_name, (' - %s' % call_date) if call_date else '')))
        return result

    def _role_for_user(self, user):
        return (
            'manager'
            if user.has_group('ming_customer_care.group_ming_branch_manager')
            or user.has_group('ming_customer_care.group_ming_founder_admin')
            else 'staff'
        )

    def _ensure_follow_up_task(self, record):
        Task = self.env['ming.care.task'].sudo()
        existing = Task.search(
            [
                ('partner_id', '=', record.partner_id.id),
                ('task_type', '=', 'follow_up'),
                ('pipeline_status', 'in', ('pending', 'in_progress')),
            ],
            order='due_date asc, create_date asc, id asc',
            limit=1,
        )
        if existing:
            return existing
        assigned_user = record.task_id.assigned_user_id or record.branch_id.manager_id or record.user_id
        return Task.create(
            {
                'name': 'Hẹn gọi lại: %s' % record.partner_id.display_name,
                'partner_id': record.partner_id.id,
                'assigned_user_id': assigned_user.id if assigned_user else False,
                'task_type': 'follow_up',
                'priority': '2' if record.partner_id.ming_is_vip else '1',
                'due_date': record.follow_up_date,
                'created_by_system': True,
                'source_reason': 'Tạo từ lịch sử hẹn gọi lại %s' % record.id,
            }
        )

    def _ensure_negative_feedback_task(self, record):
        Task = self.env['ming.care.task'].sudo()
        existing = Task.search(
            [
                ('partner_id', '=', record.partner_id.id),
                ('task_type', '=', 'negative_feedback'),
                ('pipeline_status', 'in', ('pending', 'in_progress')),
            ],
            order='create_date asc, id asc',
            limit=1,
        )
        if existing:
            return existing
        manager = record.branch_id.manager_id
        return Task.create(
            {
                'name': 'Quản lý xử lý phản hồi tiêu cực: %s' % record.partner_id.display_name,
                'partner_id': record.partner_id.id,
                'assigned_user_id': manager.id if manager else False,
                'task_type': 'negative_feedback',
                'priority': '3',
                'due_date': fields.Date.context_today(record),
                'created_by_system': True,
                'source_reason': 'Tạo từ phản hồi tiêu cực trong lịch sử CSKH %s' % record.id,
            }
        )

    def _post_care_note(self, record):
        status_label = dict(self._fields['call_status'].selection).get(record.call_status, record.call_status)
        body = _('Kết quả chăm sóc: %s') % status_label
        if record.note:
            body += '<br/>%s' % record.note
        record.partner_id.message_post(body=body, subtype_xmlid='mail.mt_note')
        if record.task_id:
            record.task_id.message_post(body=body, subtype_xmlid='mail.mt_note')

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals = []
        for values in vals_list:
            vals = dict(values)
            if vals.get('call_status') == 'callback_2' and not vals.get('follow_up_date'):
                raise UserError(_('Khi chọn "Hẹn gọi lại lần 2", bắt buộc nhập ngày hẹn gọi lại.'))
            task = self.env['ming.care.task'].browse(vals.get('task_id')).exists()
            user = self.env['res.users'].browse(vals.get('user_id') or self.env.user.id)
            vals.setdefault('role', self._role_for_user(user))
            vals.setdefault('user_role_snapshot', vals['role'])
            if task:
                vals.setdefault('pipeline_state_snapshot', task.pipeline_status)
            prepared_vals.append(vals)

        records = super().create(prepared_vals)
        for rec in records:
            rec.partner_id.write({'ming_has_been_called': True})
            if rec.call_status == 'sent_offer' or rec.manager_action_type == 'voucher':
                rec.partner_id.write({'ming_received_voucher': True})
            if rec.task_id:
                rec.task_id.latest_history_id = rec.id
                if rec.call_status in (
                    'will_return',
                    'no_need',
                    'moved_to_other_shop',
                    'negative_feedback',
                    'wrong_number',
                    'sent_offer',
                    'follow_up',
                    'callback_2',
                ):
                    rec.task_id.action_done()
            if rec.call_status == 'wrong_number':
                rec.partner_id.ming_invalid_phone = True
            if rec.call_status == 'callback_2' and rec.follow_up_date:
                self._ensure_follow_up_task(rec)
            if rec.call_status == 'negative_feedback':
                self._ensure_negative_feedback_task(rec)
            self._post_care_note(rec)
        return records
