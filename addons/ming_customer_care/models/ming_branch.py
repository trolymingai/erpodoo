# -*- coding: utf-8 -*-
from odoo import fields, models


class MingBranch(models.Model):
    _name = 'ming.branch'
    _description = 'Chi nhánh Ming'
    _order = 'name'

    name = fields.Char(required=True, string='Tên chi nhánh')
    code = fields.Char(index=True, string='Mã chi nhánh')
    source_aliases = fields.Text(
        string='Tên chi nhánh từ nguồn dữ liệu',
        help='Mỗi dòng một tên hoặc mã chi nhánh được POS/KiotViet sử dụng để ánh xạ về chi nhánh này.',
    )
    brand = fields.Selection([('ming', 'Ming Coffee'), ('goo', 'The Goo Cafe'), ('other', 'Khác')], default='ming', required=True, string='Thương hiệu')
    manager_id = fields.Many2one('res.users', string='Quản lý chi nhánh')
    lark_webhook_url = fields.Char(string='Webhook Lark')
    active = fields.Boolean(default=True, string='Đang hoạt động')
