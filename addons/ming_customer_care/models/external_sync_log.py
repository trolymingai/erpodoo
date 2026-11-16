# -*- coding: utf-8 -*-
from odoo import fields, models


class MingExternalSyncLog(models.Model):
    _name = 'ming.external.sync.log'
    _description = 'Nhật ký đồng bộ dữ liệu ngoài'
    _order = 'started_at desc, id desc'

    name = fields.Char(required=True, string='Tên lần đồng bộ')
    source_system = fields.Selection(
        [
            ('pos_excel', 'Import POS'),
            ('kiotviet_ready', 'KiotViet sẵn sàng đồng bộ'),
            ('kiotviet_api', 'API KiotViet'),
            ('manual', 'Nhập thủ công'),
            ('other', 'Khác'),
        ],
        required=True,
        index=True,
        string='Nguồn dữ liệu',
    )
    sync_type = fields.Selection(
        [
            ('manual_import', 'Import thủ công'),
            ('api_pull', 'Lấy dữ liệu từ API'),
            ('webhook', 'Webhook'),
        ],
        required=True,
        default='manual_import',
        string='Loại đồng bộ',
    )
    file_name = fields.Char(string='Tập tin nguồn')
    started_at = fields.Datetime(default=fields.Datetime.now, required=True, string='Bắt đầu')
    finished_at = fields.Datetime(string='Kết thúc')
    total_records = fields.Integer(string='Tổng bản ghi')
    created_count = fields.Integer(string='Tạo mới')
    updated_count = fields.Integer(string='Cập nhật')
    skipped_count = fields.Integer(string='Bỏ qua')
    failed_count = fields.Integer(string='Lỗi')
    duplicate_count = fields.Integer(string='Trùng')
    invalid_phone_count = fields.Integer(string='Số điện thoại sai')
    unmatched_branch_count = fields.Integer(string='Chi nhánh không khớp')
    status = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('running', 'Đang chạy'),
            ('dry_run', 'Đã kiểm tra thử'),
            ('done', 'Hoàn tất'),
            ('partial', 'Hoàn tất có lỗi'),
            ('failed', 'Thất bại'),
        ],
        default='draft',
        required=True,
        index=True,
        string='Trạng thái',
    )
    error_message = fields.Text(string='Lỗi tổng quát')
    cursor = fields.Char(copy=False, string='Mốc đồng bộ')
    import_job_id = fields.Many2one('ming.import.job', ondelete='set null', string='Đợt nhập liệu')
