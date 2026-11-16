# -*- coding: utf-8 -*-
from odoo import fields, models


class MingSalesProductLine(models.Model):
    _name = 'ming.sales.product.line'
    _description = 'Dòng dữ liệu bán hàng theo sản phẩm'
    _order = 'period_start desc, net_revenue desc'

    source_file = fields.Char(string='Tệp nguồn')
    source_key = fields.Char(index=True, copy=False, string='Khóa dòng nguồn')
    source_system = fields.Selection(
        [('pos_excel', 'Import POS'), ('kiotviet_ready', 'KiotViet sẵn sàng đồng bộ'), ('kiotviet_api', 'API KiotViet'), ('other', 'Khác')],
        default='pos_excel',
        index=True,
        string='Nguồn dữ liệu',
    )
    import_job_id = fields.Many2one('ming.import.job', copy=False, string='Đợt nhập liệu')
    sheet = fields.Char(string='Sheet')
    period_start = fields.Date(index=True, string='Từ ngày')
    period_end = fields.Date(index=True, string='Đến ngày')
    branch_name = fields.Char(index=True, string='Chi nhánh')
    branch_id = fields.Many2one('ming.branch', string='Chi nhánh chuẩn hóa')
    product_code = fields.Char(index=True, string='Mã sản phẩm')
    product_name = fields.Char(index=True, string='Tên sản phẩm')
    qty_sold = fields.Float(string='Số lượng bán')
    gross_revenue = fields.Monetary(currency_field='currency_id', string='Doanh thu gộp')
    qty_return = fields.Float(string='Số lượng trả')
    return_value = fields.Monetary(currency_field='currency_id', string='Giá trị trả')
    net_revenue = fields.Monetary(currency_field='currency_id', index=True, string='Doanh thu thuần')
    currency_id = fields.Many2one(related='company_id.currency_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
