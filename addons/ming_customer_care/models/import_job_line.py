# -*- coding: utf-8 -*-
from odoo import fields, models


class MingImportJobLine(models.Model):
    _name = 'ming.import.job.line'
    _description = 'Chi tiết dòng nhập liệu Ming'
    _order = 'job_id desc, row_number asc'

    job_id = fields.Many2one('ming.import.job', required=True, ondelete='cascade', index=True, string='Đợt nhập liệu')
    branch_id = fields.Many2one(related='job_id.branch_id', store=True, index=True, string='Chi nhánh')
    row_number = fields.Integer(required=True, string='Dòng')
    operation = fields.Selection(
        [('create', 'Tạo mới'), ('update', 'Cập nhật'), ('skip', 'Bỏ qua'), ('error', 'Lỗi')],
        default='skip',
        string='Thao tác dự kiến',
    )
    status = fields.Selection(
        [('preview', 'Xem trước'), ('created', 'Đã tạo'), ('updated', 'Đã cập nhật'), ('skipped', 'Đã bỏ qua'), ('failed', 'Lỗi')],
        default='preview',
        required=True,
        string='Trạng thái dòng',
    )
    external_customer_id = fields.Char(string='ID khách ngoài hệ thống')
    external_customer_code = fields.Char(string='Mã khách ngoài hệ thống')
    source_key = fields.Char(index=True, copy=False, string='Khóa nguồn')
    partner_id = fields.Many2one('res.partner', ondelete='set null', string='Khách hàng')
    duplicate_found = fields.Boolean(string='Phát hiện trùng')
    invalid_phone = fields.Boolean(string='Số điện thoại sai')
    unmatched_branch = fields.Boolean(string='Chi nhánh không khớp')
    raw_data = fields.Text(string='Dữ liệu gốc')
    old_values = fields.Text(string='Giá trị trước khi nhập')
    new_values = fields.Text(string='Giá trị dự kiến')
    error_message = fields.Text(string='Thông báo lỗi')
