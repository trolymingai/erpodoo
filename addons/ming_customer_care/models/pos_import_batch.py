# -*- coding: utf-8 -*-
from odoo import fields, models


class MingPosImportBatch(models.Model):
    _name = 'ming.pos.import.batch'
    _description = 'Lô import POS Ming'
    _order = 'started_at desc, id desc'

    name = fields.Char(required=True, string='Tên đợt import')
    file_name = fields.Char(string='Tên tệp')
    uploaded_by = fields.Many2one('res.users', default=lambda self: self.env.user, string='Người tải lên')
    branch_id = fields.Many2one('ming.branch', string='Chi nhánh')
    total_rows = fields.Integer(default=0, string='Tổng dòng')
    success_rows = fields.Integer(default=0, string='Dòng xử lý được')
    failed_rows = fields.Integer(default=0, string='Dòng lỗi')
    duplicate_rows = fields.Integer(default=0, string='Dòng trùng')
    invalid_phone_rows = fields.Integer(default=0, string='Số điện thoại sai')
    unmatched_branch_rows = fields.Integer(default=0, string='Chi nhánh không khớp')
    dry_run = fields.Boolean(default=True, string='Chỉ kiểm tra, chưa ghi dữ liệu')
    state = fields.Selection(
        [('draft', 'Nháp'), ('processing', 'Đang xử lý'), ('dry_run', 'Đã kiểm tra thử'), ('done', 'Hoàn tất'), ('partial', 'Hoàn tất có lỗi'), ('failed', 'Lỗi')],
        default='draft',
        required=True,
        string='Trạng thái',
    )
    started_at = fields.Datetime(default=fields.Datetime.now, string='Bắt đầu')
    finished_at = fields.Datetime(string='Kết thúc')
    error_summary = fields.Text(string='Tóm tắt lỗi')
    sync_log_id = fields.Many2one('ming.external.sync.log', copy=False, string='Nhật ký đồng bộ')
    error_ids = fields.One2many('ming.pos.import.error', 'batch_id', string='Chi tiết lỗi')


class MingPosImportError(models.Model):
    _name = 'ming.pos.import.error'
    _description = 'Lỗi import POS Ming'
    _order = 'batch_id desc, row_number asc'

    batch_id = fields.Many2one('ming.pos.import.batch', required=True, ondelete='cascade', string='Lô import')
    row_number = fields.Integer(required=True, string='Dòng')
    raw_data = fields.Text(string='Dữ liệu gốc')
    error_message = fields.Text(required=True, string='Thông báo lỗi')
