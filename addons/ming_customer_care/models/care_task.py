# -*- coding: utf-8 -*-
from odoo import fields, models


class MingCareTask(models.Model):
    _name = 'ming.care.task'
    _description = 'C\u00f4ng vi\u1ec7c ch\u0103m s\u00f3c kh\u00e1ch h\u00e0ng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'is_vip desc, total_spent desc, priority desc, due_date asc'

    name = fields.Char(required=True, default='C\u00f4ng vi\u1ec7c CSKH', tracking=True, string='T\u00ean c\u00f4ng vi\u1ec7c')
    partner_id = fields.Many2one('res.partner', required=True, index=True, tracking=True, string='Kh\u00e1ch h\u00e0ng')
    branch_id = fields.Many2one(related='partner_id.ming_branch_id', store=True, index=True, string='Chi nh\u00e1nh')
    customer_phone = fields.Char(
        related='partner_id.phone',
        store=True,
        readonly=True,
        index=True,
        string='S\u1ed1 \u0111i\u1ec7n tho\u1ea1i',
    )
    customer_code = fields.Char(
        related='partner_id.ming_pos_customer_code',
        store=True,
        readonly=True,
        index=True,
        string='M\u00e3 kh\u00e1ch h\u00e0ng',
    )
    last_transaction_date = fields.Date(
        related='partner_id.ming_last_transaction_date',
        store=True,
        readonly=True,
        index=True,
        string='Ng\u00e0y giao d\u1ecbch cu\u1ed1i',
    )
    assigned_user_id = fields.Many2one('res.users', string='Nh\u00e2n vi\u00ean ph\u1ee5 tr\u00e1ch', tracking=True)
    task_type = fields.Selection(
        [
            ('at_risk', 'Kh\u00e1ch c\u00f3 nguy c\u01a1'),
            ('follow_up', 'H\u1eb9n g\u1ecdi l\u1ea1i'),
            ('vip_alert', 'VIP c\u00f3 nguy c\u01a1'),
            ('winback', 'M\u1eddi quay l\u1ea1i'),
            ('negative_feedback', 'Ph\u1ea3n h\u1ed3i ti\u00eau c\u1ef1c'),
            ('manual', 'T\u1ea1o th\u1ee7 c\u00f4ng'),
        ],
        default='at_risk',
        index=True,
        tracking=True,
        string='Lo\u1ea1i c\u00f4ng vi\u1ec7c',
    )
    priority = fields.Selection(
        [('0', 'Th\u1ea5p'), ('1', 'B\u00ecnh th\u01b0\u1eddng'), ('2', 'Cao'), ('3', 'R\u1ea5t cao')],
        default='1',
        index=True,
        tracking=True,
        string='M\u1ee9c \u01b0u ti\u00ean',
    )
    due_date = fields.Date(default=fields.Date.context_today, index=True, tracking=True, string='Ng\u00e0y c\u1ea7n g\u1ecdi')
    pipeline_status = fields.Selection(
        [('pending', 'Ch\u01b0a x\u1eed l\u00fd'), ('in_progress', '\u0110ang x\u1eed l\u00fd'), ('done', '\u0110\u00e3 ho\u00e0n t\u1ea5t'), ('cancelled', '\u0110\u00e3 h\u1ee7y')],
        default='pending',
        index=True,
        tracking=True,
        string='Tr\u1ea1ng th\u00e1i x\u1eed l\u00fd',
    )
    days_absent = fields.Integer(index=True, string='S\u1ed1 ng\u00e0y v\u1eafng')
    alert_level = fields.Selection(
        [('1', 'C\u1ea3nh b\u00e1o l\u1ea7n 1'), ('2', 'C\u1ea3nh b\u00e1o l\u1ea7n 2'), ('3', 'C\u1ea3nh b\u00e1o l\u1ea7n 3'), ('winback', 'M\u1eddi quay l\u1ea1i')],
        index=True,
        string='M\u1ee9c c\u1ea3nh b\u00e1o',
    )
    is_vip = fields.Boolean(index=True, string='Kh\u00e1ch VIP')
    total_spent = fields.Monetary(currency_field='currency_id', string='T\u1ed5ng chi ti\u00eau')
    currency_id = fields.Many2one(related='company_id.currency_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    latest_history_id = fields.Many2one('ming.care.history', string='K\u1ebft qu\u1ea3 ch\u0103m s\u00f3c g\u1ea7n nh\u1ea5t')
    call_result = fields.Selection(
        related='latest_history_id.call_status',
        store=True,
        readonly=True,
        string='K\u1ebft qu\u1ea3 ch\u0103m s\u00f3c',
    )
    created_by_system = fields.Boolean(default=False, copy=False, string='Do h\u1ec7 th\u1ed1ng t\u1ea1o')
    source_reason = fields.Char(string='Ngu\u1ed3n t\u1ea1o vi\u1ec7c')
    source_key = fields.Char(index=True, copy=False, string='Kh\u00f3a d\u00f2ng ngu\u1ed3n')
    import_job_id = fields.Many2one('ming.import.job', copy=False, string='\u0110\u1ee3t nh\u1eadp li\u1ec7u')
    completed_at = fields.Datetime(string='Th\u1eddi \u0111i\u1ec3m ho\u00e0n t\u1ea5t')

    def action_start(self):
        self.write({'pipeline_status': 'in_progress', 'assigned_user_id': self.env.user.id})

    def action_done(self):
        self.write({'pipeline_status': 'done', 'completed_at': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'pipeline_status': 'cancelled'})

    def action_log_call_result(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ghi nh\u1eadn k\u1ebft qu\u1ea3 g\u1ecdi',
            'res_model': 'ming.care.history.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_task_id': self.id},
        }

    def action_schedule_callback(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'H\u1eb9n g\u1ecdi l\u1ea1i',
            'res_model': 'ming.care.history.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_task_id': self.id, 'default_call_status': 'callback_2'},
        }

    def _open_send_message_wizard(self, channel):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gửi SMS' if channel == 'sms' else 'Gửi Email',
            'res_model': 'ming.send.message.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_channel': channel,
            },
        }

    def action_send_sms(self):
        return self._open_send_message_wizard('sms')

    def action_send_email(self):
        return self._open_send_message_wizard('email')
