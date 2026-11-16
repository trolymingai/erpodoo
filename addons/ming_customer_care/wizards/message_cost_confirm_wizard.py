# -*- coding: utf-8 -*-
from odoo import fields, models


class MingMessageCostConfirmWizard(models.TransientModel):
    _name = 'ming.message.cost.confirm.wizard'
    _description = 'Xác nhận chi phí gửi tin'

    send_wizard_id = fields.Many2one('ming.send.message.wizard', required=True, string='Wizard gửi tin')
    channel = fields.Selection([('sms', 'SMS'), ('email', 'Email')], string='Kênh gửi')
    recipient_count = fields.Integer(default=1, string='Số lượng người nhận')
    unit_cost = fields.Float(string='Đơn giá')
    monthly_cost = fields.Float(string='Phí gói tháng')
    estimated_cost = fields.Float(string='Chi phí ước tính')
    remaining_budget = fields.Float(string='Ngân sách còn lại trong ngày')
    currency = fields.Char(default='VND', string='Tiền tệ')
    warning_message = fields.Text(string='Cảnh báo')

    def action_confirm_send(self):
        self.ensure_one()
        return self.send_wizard_id.action_send_confirmed()
