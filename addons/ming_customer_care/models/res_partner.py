# -*- coding: utf-8 -*-
import re

from odoo import api, fields, models, tools

try:
    import phonenumbers
except ImportError:  # pragma: no cover - optional dependency in staging/prod
    phonenumbers = None


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ming_pos_customer_code = fields.Char(index=True, copy=False, string='Mã khách hàng POS/KiotViet')
    ming_kiotviet_customer_id = fields.Char(index=True, copy=False, string='Mã khách hàng KiotViet')
    ming_source_system = fields.Selection(
        [
            ('manual', 'Nhập thủ công'),
            ('pos_excel', 'Import POS Excel'),
            ('kiotviet_api', 'API KiotViet'),
            ('kiotviet_ready', 'KiotViet sẵn sàng đồng bộ'),
            ('form', 'Biểu mẫu'),
            ('uat_positive_case', 'Ca UAT dương'),
            ('other', 'Khác'),
        ],
        default='manual',
        index=True,
        string='Nguồn dữ liệu',
    )
    ming_branch_id = fields.Many2one('ming.branch', string='Chi nhánh chính', index=True)
    ming_currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ CSKH',
        related='company_id.currency_id',
        readonly=True,
    )
    ming_total_spent = fields.Monetary(string='Tổng chi tiêu', currency_field='ming_currency_id', default=0.0, tracking=True)
    ming_loyalty_points = fields.Integer(default=0, tracking=True, string='Điểm tích lũy')
    ming_last_transaction_date = fields.Date(index=True, tracking=True, string='Ngày giao dịch cuối')
    ming_days_absent = fields.Integer(compute='_compute_ming_days_absent', store=True, index=True, string='Số ngày vắng')
    ming_activity_status = fields.Selection(
        [('active', 'Đang hoạt động'), ('at_risk', 'Có nguy cơ'), ('lost', 'Đã mất')],
        default='active',
        index=True,
        tracking=True,
        string='Trạng thái khách',
    )
    ming_is_vip = fields.Boolean(default=False, index=True, tracking=True, string='Khách VIP')
    ming_vip_rank = fields.Integer(index=True, readonly=True, tracking=True, string='Thứ hạng VIP')
    ming_alert_level = fields.Selection(
        [('0', 'Không cảnh báo'), ('1', 'Lần 1'), ('2', 'Lần 2'), ('3', 'Lần 3'), ('winback', 'Mời khách quay lại')],
        default='0',
        tracking=True,
        string='Mức cảnh báo',
    )
    ming_allow_sms = fields.Boolean(default=True, string='Cho phép SMS')
    ming_allow_email = fields.Boolean(default=True, string='Cho phép email')
    ming_do_not_contact = fields.Boolean(default=False, string='Không liên hệ')
    ming_phone_normalized = fields.Char(index=True, copy=False, string='Số điện thoại chuẩn hóa')
    ming_invalid_phone = fields.Boolean(default=False, string='Số điện thoại không hợp lệ')
    ming_invalid_email = fields.Boolean(default=False, string='Email không hợp lệ')
    ming_customer_note = fields.Text(string='Ghi chú chăm sóc nội bộ')
    ming_has_been_called = fields.Boolean(default=False, index=True, tracking=True, string='Đã gọi')
    ming_received_voucher = fields.Boolean(default=False, index=True, tracking=True, string='Đã nhận voucher')
    ming_has_returned = fields.Boolean(default=False, index=True, tracking=True, string='Đã quay lại')
    ming_returned_at = fields.Date(index=True, tracking=True, string='Ngày quay lại')
    ming_last_import_job_id = fields.Many2one('ming.import.job', copy=False, string='Đợt import gần nhất')
    ming_last_sync_at = fields.Datetime(copy=False, string='Lần đồng bộ gần nhất')
    ming_external_payload_hash = fields.Char(copy=False, string='Mã kiểm tra dữ liệu ngoài')
    ming_last_sync_log_id = fields.Many2one('ming.external.sync.log', copy=False, string='Nhật ký đồng bộ gần nhất')
    ming_purchase_history_ids = fields.One2many(
        'ming.purchase.history',
        'partner_id',
        string='Lịch sử mua hàng',
        readonly=True,
    )

    @api.depends('ming_last_transaction_date')
    def _compute_ming_days_absent(self):
        today = fields.Date.context_today(self)
        for partner in self:
            partner.ming_days_absent = (today - partner.ming_last_transaction_date).days if partner.ming_last_transaction_date else 9999

    @api.model
    def _normalize_vn_phone(self, raw_value):
        raw_text = (raw_value or '').strip()
        if not raw_text:
            return False, False, False

        sanitized = re.sub(r'[^\d+]', '', raw_text)
        if sanitized.startswith('00'):
            sanitized = '+' + sanitized[2:]

        if phonenumbers:
            try:
                parsed = phonenumbers.parse(sanitized, 'VN')
                if (
                    parsed.country_code == 84
                    and phonenumbers.is_possible_number(parsed)
                    and phonenumbers.is_valid_number_for_region(parsed, 'VN')
                ):
                    national = str(parsed.national_number)
                    if len(national) == 9:
                        return '0%s' % national, '+84%s' % national, True
            except Exception:
                pass

        digits = re.sub(r'\D', '', sanitized)
        if digits.startswith('84') and len(digits) == 11 and digits[2:3] in '235789':
            national = digits[2:]
            return '0%s' % national, '+84%s' % national, True
        if digits.startswith('0') and len(digits) == 10 and digits[1:2] in '235789':
            national = digits[1:]
            return '0%s' % national, '+84%s' % national, True
        return raw_text, False, False

    @api.model
    def _prepare_phone_write_vals(self, vals):
        values = dict(vals)

        if 'email' in values:
            email_value = (values.get('email') or '').strip()
            values['email'] = email_value or False
            values['ming_invalid_email'] = bool(email_value) and not bool(tools.single_email_re.match(email_value))

        if 'phone' not in values and 'mobile' not in values:
            return values

        input_phone = values.get('phone')
        if input_phone in (None, ''):
            input_phone = values.get('mobile')
        if not input_phone:
            values['ming_phone_normalized'] = False
            if 'ming_invalid_phone' not in values:
                values['ming_invalid_phone'] = False
            if 'phone' in values:
                values['phone'] = False
            return values

        local_phone, normalized_phone, is_valid = self._normalize_vn_phone(input_phone)
        values['ming_phone_normalized'] = normalized_phone or False
        if 'ming_invalid_phone' in values:
            values['ming_invalid_phone'] = bool(values['ming_invalid_phone'] or not is_valid)
        else:
            values['ming_invalid_phone'] = not is_valid
        if is_valid:
            values['phone'] = local_phone
        elif 'phone' in values:
            values['phone'] = local_phone
        return values

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals = [self._prepare_phone_write_vals(vals) for vals in vals_list]
        return super().create(prepared_vals)

    def write(self, vals):
        values = self._prepare_phone_write_vals(vals)
        if values.get('ming_has_returned') and 'ming_returned_at' not in values:
            values['ming_returned_at'] = fields.Date.context_today(self)
        elif 'ming_has_returned' in values and not values['ming_has_returned']:
            values['ming_returned_at'] = False
        return super().write(values)

    @api.onchange('phone', 'mobile', 'email')
    def _onchange_ming_contact_validation(self):
        for partner in self:
            if partner.email:
                partner.ming_invalid_email = not bool(tools.single_email_re.match(partner.email.strip()))
            elif 'email' in partner._cache:
                partner.ming_invalid_email = False

            mobile = partner.mobile if 'mobile' in partner._fields else ''
            input_phone = partner.phone or mobile
            if not input_phone:
                partner.ming_phone_normalized = False
                partner.ming_invalid_phone = False
                continue
            local_phone, normalized_phone, is_valid = partner._normalize_vn_phone(input_phone)
            partner.phone = local_phone
            partner.ming_phone_normalized = normalized_phone
            partner.ming_invalid_phone = not is_valid

    def _open_ming_send_message_wizard(self, channel):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gửi SMS' if channel == 'sms' else 'Gửi Email',
            'res_model': 'ming.send.message.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_channel': channel,
            },
        }

    def action_ming_send_sms(self):
        return self._open_ming_send_message_wizard('sms')

    def action_ming_send_email(self):
        return self._open_ming_send_message_wizard('email')
