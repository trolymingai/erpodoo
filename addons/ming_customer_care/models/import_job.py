# -*- coding: utf-8 -*-
from odoo import fields, models


class MingImportJob(models.Model):
    _name = 'ming.import.job'
    _description = 'Nhật ký import Ming'
    _order = 'create_date desc'

    name = fields.Char(required=True, string='Tên đợt import')
    import_type = fields.Selection(
        [('customer', 'Khách hàng'), ('care_task', 'Công việc CSKH'), ('sales_product', 'Bán hàng theo sản phẩm'), ('other', 'Khác')],
        default='customer',
        string='Loại dữ liệu',
    )
    source_file_name = fields.Char(string='Tệp nguồn')
    uploaded_by = fields.Many2one('res.users', default=lambda self: self.env.user, string='Người tải lên')
    branch_id = fields.Many2one('ming.branch', string='Chi nhánh')
    total_rows = fields.Integer(string='Tổng dòng')
    success_rows = fields.Integer(string='Dòng xử lý được')
    failed_rows = fields.Integer(string='Dòng lỗi')
    duplicate_rows = fields.Integer(string='Dòng trùng')
    invalid_phone_rows = fields.Integer(string='Số điện thoại sai')
    unmatched_branch_rows = fields.Integer(string='Chi nhánh không khớp')
    dry_run = fields.Boolean(default=True, string='Chỉ kiểm tra, chưa ghi dữ liệu')
    sync_log_id = fields.Many2one('ming.external.sync.log', copy=False, string='Nhật ký đồng bộ')
    line_ids = fields.One2many('ming.import.job.line', 'job_id', string='Chi tiết dòng')
    status = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('dry_run', 'Đã kiểm tra thử'),
            ('done', 'Hoàn tất'),
            ('partial', 'Hoàn tất có lỗi'),
            ('failed', 'Lỗi'),
            ('rollback', 'Đã hoàn tác'),
        ],
        default='draft',
        string='Trạng thái',
    )
    note = fields.Text(string='Ghi chú')
