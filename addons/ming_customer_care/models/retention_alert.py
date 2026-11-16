# -*- coding: utf-8 -*-
from odoo import fields, models


class MingRetentionAlert(models.Model):
    _name = 'ming.retention.alert'
    _description = 'Cảnh báo giữ chân'
    _inherit = ['mail.thread']
    _order = 'trigger_date desc, alert_level desc'

    name = fields.Char(required=True, default='Cảnh báo giữ chân', string='Tên cảnh báo')
    partner_id = fields.Many2one('res.partner', required=True, index=True, string='Khách hàng')
    branch_id = fields.Many2one(related='partner_id.ming_branch_id', store=True, index=True, string='Chi nhánh')
    alert_level = fields.Selection(
        [('1', 'Cảnh báo lần 1'), ('2', 'Cảnh báo lần 2'), ('3', 'Cảnh báo lần 3'), ('winback', 'Mời khách quay lại')],
        required=True,
        index=True,
        string='Mức cảnh báo',
    )
    alert_type = fields.Selection(
        [('at_risk', 'Khách có nguy cơ'), ('vip_at_risk', 'VIP có nguy cơ'), ('lost', 'Khách đã mất'), ('follow_up', 'Hẹn gọi lại')],
        required=True,
        index=True,
        string='Loại cảnh báo',
    )
    trigger_date = fields.Date(default=fields.Date.context_today, required=True, index=True, string='Ngày kích hoạt')
    trigger_reason = fields.Char(string='Lý do kích hoạt')
    care_task_id = fields.Many2one('ming.care.task', string='Công việc liên quan')
    status = fields.Selection(
        [('pending', 'Chờ xử lý'), ('sent', 'Đã ghi log'), ('handled', 'Đã xử lý'), ('converted', 'Đã quay lại'), ('cancelled', 'Đã hủy')],
        default='pending',
        index=True,
        tracking=True,
        string='Trạng thái',
    )
    next_alert_date = fields.Date(string='Ngày cảnh báo tiếp theo')
    converted_at = fields.Datetime(string='Thời điểm quay lại')
    sms_sent = fields.Boolean(default=False, string='Đã tạo log SMS')
    email_sent = fields.Boolean(default=False, string='Đã tạo log email')
    lark_sent = fields.Boolean(default=False, string='Đã tạo log Lark')

    def _render_template(self, template):
        self.ensure_one()
        branch_name = self.branch_id.name if self.branch_id else 'Chưa gán chi nhánh'
        return (
            (template or '')
            .replace('{ten_khach}', self.partner_id.name or '')
            .replace('{ten_chi_nhanh}', branch_name)
            .replace('{tong_chi_tieu}', '{:,.0f}'.format(self.partner_id.ming_total_spent or 0))
            .replace('{so_ngay_vang}', str(self.partner_id.ming_days_absent or 0))
        )

    def _config(self):
        Config = self.env['ming.segment.config'].sudo()
        branch = self[:1].branch_id
        if branch:
            config = Config.search(
                [('active', '=', True), ('branch_id', '=', branch.id)],
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

    def action_send_sms(self):
        cfg = self._config()
        templates = {
            '1': cfg.sms_template_level_1 if cfg else False,
            '2': cfg.sms_template_level_2 if cfg else False,
            '3': cfg.sms_template_level_3 if cfg else False,
            'winback': cfg.sms_template_winback if cfg else False,
        }
        templates.update(
            {
                '1': templates['1'] or 'Ming Coffee nhớ {ten_khach} rồi ạ. Mời anh/chị ghé lại quán trong tuần này nhé.',
                '2': templates['2'] or 'Ming Coffee gửi ưu đãi quay lại cho {ten_khach} tại {ten_chi_nhanh}.',
                '3': templates['3'] or 'Ming Coffee rất mong được phục vụ {ten_khach} tốt hơn. Quản lý {ten_chi_nhanh} sẽ liên hệ hỗ trợ.',
                'winback': templates['winback'] or 'Ming Coffee gửi lời mời quay lại dành riêng cho {ten_khach}.',
            }
        )
        for rec in self:
            partner = rec.partner_id
            phone = partner.ming_phone_normalized or getattr(partner, 'mobile', False) or partner.phone
            if partner.ming_do_not_contact or partner.ming_invalid_phone or not phone or not partner.ming_allow_sms:
                continue
            log = self.env['ming.message.log'].create(
                {
                    'partner_id': partner.id,
                    'alert_id': rec.id,
                    'channel': 'sms',
                    'recipient': phone,
                    'content': rec._render_template(templates.get(rec.alert_level)),
                }
            )
            log.action_send()
            rec.sms_sent = log.status in ('safe_mode', 'sent')

    def action_send_email(self):
        cfg = self._config()
        for rec in self:
            partner = rec.partner_id
            if partner.ming_do_not_contact or partner.ming_invalid_email or not partner.email or not partner.ming_allow_email:
                continue
            log = self.env['ming.message.log'].create(
                {
                    'partner_id': partner.id,
                    'alert_id': rec.id,
                    'channel': 'email',
                    'recipient': partner.email,
                    'subject': (cfg.email_template_subject if cfg else False) or 'Ming Coffee mời anh/chị quay lại',
                    'content': rec._render_template(
                        (cfg.email_template_body if cfg else False)
                        or 'Ming Coffee gửi lời mời quay lại dành riêng cho {ten_khach}.'
                    ),
                }
            )
            log.action_send()
            rec.email_sent = log.status in ('safe_mode', 'sent')

    def action_send_lark(self):
        cfg = self._config()
        for rec in self:
            webhook = rec.branch_id.lark_webhook_url
            if not webhook:
                self.env['ming.message.log'].create(
                    {
                        'partner_id': rec.partner_id.id,
                        'alert_id': rec.id,
                        'channel': 'lark',
                        'recipient': False,
                        'content': 'Thiếu webhook Lark.',
                        'status': 'failed',
                        'error_message': 'Chi nhánh chưa cấu hình webhook Lark.',
                    }
                )
                continue
            log = self.env['ming.message.log'].create(
                {
                    'partner_id': rec.partner_id.id,
                    'alert_id': rec.id,
                    'channel': 'lark',
                    'recipient': webhook,
                    'content': rec._render_template(
                        cfg.lark_template_alert
                        or '[CẢNH BÁO] {ten_khach} - {ten_chi_nhanh}. Tổng chi tiêu: {tong_chi_tieu}. Số ngày vắng: {so_ngay_vang}.'
                    ),
                }
            )
            log.action_send()
            rec.lark_sent = log.status in ('safe_mode', 'sent')

    def action_mark_converted(self):
        self.write({'status': 'converted', 'converted_at': fields.Datetime.now()})
        for alert in self:
            alert.partner_id.write(
                {
                    'ming_has_returned': True,
                    'ming_returned_at': fields.Date.context_today(alert.partner_id),
                }
            )
