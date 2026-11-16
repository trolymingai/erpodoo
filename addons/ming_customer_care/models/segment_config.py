# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError


class MingSegmentConfig(models.Model):
    _name = 'ming.segment.config'
    _description = 'Cấu hình giữ chân khách hàng'
    _rec_name = 'display_name'

    display_name = fields.Char(default='Cấu hình giữ chân mặc định', string='Tên cấu hình')
    branch_id = fields.Many2one('ming.branch', string='Chi nhánh áp dụng', help='Để trống nếu dùng chung toàn hệ thống')
    active = fields.Boolean(default=True, index=True, string='Đang áp dụng')
    active_days_threshold = fields.Integer(default=30, required=True, string='Ngưỡng khách đang hoạt động (ngày)')
    lost_days_threshold = fields.Integer(default=90, required=True, string='Ngưỡng khách đã mất (ngày)')
    vip_percent = fields.Float(default=10.0, required=True, string='Tỷ lệ VIP top (%)')
    alert_2_after_days = fields.Integer(default=7, required=True, string='Số ngày lên cảnh báo lần 2')
    alert_3_after_days = fields.Integer(default=14, required=True, string='Số ngày lên cảnh báo lần 3')
    conversion_window_days = fields.Integer(default=30, required=True, string='Cửa sổ theo dõi quay lại (ngày)')

    send_sms_enabled = fields.Boolean(default=True, string='Cho phép tạo SMS')
    send_email_enabled = fields.Boolean(default=True, string='Cho phép tạo email')
    send_lark_enabled = fields.Boolean(default=True, string='Cho phép tạo cảnh báo Lark')
    safe_mode = fields.Boolean(default=True, help='Khi bật, hệ thống chỉ ghi log mà không gửi thật', string='Chế độ an toàn')
    email_enabled = fields.Boolean(default=False, string='Bật gửi email thật')
    sms_enabled = fields.Boolean(default=False, string='Bật gửi SMS thật')
    test_mode = fields.Boolean(default=True, string='Chế độ test')
    email_test_whitelist = fields.Text(string='Whitelist email test')
    sms_test_whitelist = fields.Text(string='Whitelist SMS test')
    max_sms_per_day = fields.Integer(default=0, string='Giới hạn SMS mỗi ngày')
    max_email_per_day = fields.Integer(default=0, string='Giới hạn email mỗi ngày')

    smtp_sender_name = fields.Char(string='Tên người gửi email')
    smtp_sender_email = fields.Char(string='Email người gửi')
    default_email_from = fields.Char(string='Email gửi mặc định')
    default_reply_to = fields.Char(string='Email nhận phản hồi')

    sms_provider_name = fields.Char(string='Nhà cung cấp SMS')
    sms_provider = fields.Char(string='Mã nhà cung cấp SMS')
    sms_api_url = fields.Char(string='SMS API URL')
    sms_api_key = fields.Char(string='SMS API key')
    sms_brandname = fields.Char(string='SMS brandname')
    sms_sender_id = fields.Char(string='SMS sender ID')
    sms_sender_name = fields.Char(string='Brandname / SMS sender')

    message_currency = fields.Char(default='VND', string='Tiền tệ chi phí')
    sms_unit_cost = fields.Float(default=0.0, string='Đơn giá SMS')
    email_unit_cost = fields.Float(default=0.0, string='Đơn giá email')
    email_monthly_package_cost = fields.Float(default=0.0, string='Phí gói email/tháng')
    sms_monthly_package_cost = fields.Float(default=0.0, string='Phí gói SMS/tháng')
    daily_sms_budget_limit = fields.Float(default=0.0, string='Ngân sách SMS/ngày')
    daily_email_budget_limit = fields.Float(default=0.0, string='Ngân sách email/ngày')
    require_cost_confirmation = fields.Boolean(default=True, string='Bắt buộc xác nhận chi phí')

    test_sms_number = fields.Char(string='Số điện thoại test')
    test_email_to = fields.Char(string='Email test')
    lark_test_branch_id = fields.Many2one('ming.branch', string='Chi nhánh test webhook Lark')
    sms_template_level_1 = fields.Text(string='Mẫu SMS cảnh báo lần 1')
    sms_template_level_2 = fields.Text(string='Mẫu SMS cảnh báo lần 2')
    sms_template_level_3 = fields.Text(string='Mẫu SMS cảnh báo lần 3')
    sms_template_winback = fields.Text(string='Mẫu SMS mời quay lại')
    email_template_subject = fields.Char(string='Tiêu đề email mặc định')
    email_template_body = fields.Text(string='Nội dung email mặc định')
    lark_template_alert = fields.Text(string='Mẫu tin nhắn Lark')
    kiotviet_customer_code_key = fields.Char(string='Cột mã khách KiotViet', default='customer_code')
    kiotviet_phone_key = fields.Char(string='Cột số điện thoại KiotViet', default='phone')
    kiotviet_email_key = fields.Char(string='Cột email KiotViet', default='email')
    kiotviet_total_spent_key = fields.Char(string='Cột tổng chi tiêu KiotViet', default='total_spent')
    kiotviet_last_transaction_key = fields.Char(string='Cột giao dịch cuối KiotViet', default='last_transaction_date')
    pos_connection_mode = fields.Selection(
        [
            ('manual_file', 'Đọc tệp POS/Excel'),
            ('kiotviet_api', 'API KiotViet'),
            ('pos_api', 'API máy POS'),
        ],
        default='manual_file',
        required=True,
        string='Cách đọc dữ liệu POS',
    )
    pos_api_base_url = fields.Char(string='Địa chỉ API POS/KiotViet')
    pos_api_key = fields.Char(string='Mã API POS/KiotViet')
    pos_api_secret = fields.Char(string='Khóa bí mật API POS/KiotViet')
    pos_customer_code_key = fields.Char(default='ma_khach_hang', string='Cột mã khách từ POS')
    pos_customer_name_key = fields.Char(default='ten_khach_hang', string='Cột tên khách từ POS')
    pos_note_name_key = fields.Char(default='ghi_chu', string='Cột ghi chú dùng làm tên hiển thị')
    pos_phone_key = fields.Char(default='dien_thoai', string='Cột số điện thoại từ POS')
    pos_branch_key = fields.Char(default='chi_nhanh', string='Cột chi nhánh từ POS')
    pos_total_spent_key = fields.Char(default='tong_ban_tru_tra_hang', string='Cột tổng chi tiêu từ POS')
    pos_loyalty_points_key = fields.Char(default='diem_hien_tai', string='Cột điểm tích lũy từ POS')
    pos_last_transaction_key = fields.Char(default='ngay_giao_dich_cuoi', string='Cột ngày giao dịch cuối từ POS')

    def _build_test_log(self, channel, recipient, content, subject=False):
        partner = self.env['res.partner'].sudo().search(['|', ('email', '=', recipient), ('phone', '=', recipient)], limit=1)
        log_vals = {
            'channel': channel,
            'recipient': recipient,
            'subject': subject,
            'content': content,
            'safe_mode': self.safe_mode,
            'test_mode': self.test_mode,
            'provider': self.sms_provider if channel == 'sms' else 'odoo_mail' if channel == 'email' else 'lark',
            'status': 'safe_mode' if self.safe_mode else 'draft',
            'error_message': 'SAFE_MODE: chỉ ghi log, không gửi thật.' if self.safe_mode else 'Log test connector.',
        }
        if partner:
            log_vals['partner_id'] = partner.id
        log = self.env['ming.message.log'].sudo().create(log_vals)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nhật ký gửi tin',
            'res_model': 'ming.message.log',
            'res_id': log.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_test_sms_connector(self):
        self.ensure_one()
        if not self.test_sms_number:
            raise UserError('Vui lòng khai báo số điện thoại test trước khi kiểm tra SMS.')
        return self._build_test_log('sms', self.test_sms_number, 'Tin nhắn test từ cấu hình Ming Customer Care.')

    def action_test_email_connector(self):
        self.ensure_one()
        if not self.test_email_to:
            raise UserError('Vui lòng khai báo email test trước khi kiểm tra email.')
        return self._build_test_log(
            'email',
            self.test_email_to,
            'Email test từ cấu hình Ming Customer Care.',
            subject=self.email_template_subject or 'Kiểm tra kết nối email Ming Customer Care',
        )

    def action_test_lark_connector(self):
        self.ensure_one()
        branch = self.lark_test_branch_id or self.env['ming.branch'].search([('lark_webhook_url', '!=', False)], limit=1)
        if not branch or not branch.lark_webhook_url:
            raise UserError('Vui lòng chọn chi nhánh có webhook Lark trước khi kiểm tra.')
        return self._build_test_log('lark', branch.lark_webhook_url, 'Tin nhắn test Lark từ cấu hình Ming Customer Care.')

    def action_notify_cost_saved(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Đã lưu cấu hình chi phí',
                'message': 'Hệ thống sẽ hiển thị chi phí ước tính trước mỗi lần gửi.',
                'type': 'success',
                'sticky': False,
            },
        }
