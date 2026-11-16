# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class MingCareHistoryWizard(models.TransientModel):
    _name = 'ming.care.history.wizard'
    _description = 'Ghi nhận kết quả CSKH'

    task_id = fields.Many2one('ming.care.task', required=True, string='Công việc')
    partner_id = fields.Many2one(related='task_id.partner_id', readonly=True, string='Khách hàng')
    branch_id = fields.Many2one(related='task_id.branch_id', readonly=True, string='Chi nhánh')
    call_status = fields.Selection(
        selection=lambda self: self.env['ming.care.history']._fields['call_status'].selection,
        required=True,
        string='Kết quả chăm sóc',
    )
    lost_reason = fields.Selection(selection=lambda self: self.env['ming.care.history']._fields['lost_reason'].selection, string='Lý do mất khách')
    note = fields.Text(string='Ghi chú chăm sóc')
    follow_up_date = fields.Date(string='Ngày hẹn gọi lại')
    manager_action_type = fields.Selection(
        selection=lambda self: self.env['ming.care.history']._fields['manager_action_type'].selection,
        string='Hướng xử lý của quản lý',
    )

    def action_save_history(self):
        self.ensure_one()
        if self.call_status == 'callback_2' and not self.follow_up_date:
            raise UserError(_('Khi chọn "Hẹn gọi lại lần 2", bắt buộc nhập ngày hẹn gọi lại.'))
        role = 'manager' if (
            self.env.user.has_group('ming_customer_care.group_ming_branch_manager')
            or self.env.user.has_group('ming_customer_care.group_ming_founder_admin')
        ) else 'staff'
        self.env['ming.care.history'].create(
            {
                'partner_id': self.partner_id.id,
                'task_id': self.task_id.id,
                'role': role,
                'call_status': self.call_status,
                'lost_reason': self.lost_reason,
                'note': self.note,
                'follow_up_date': self.follow_up_date,
                'manager_action_type': self.manager_action_type,
            }
        )
        return {'type': 'ir.actions.act_window_close'}
