# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MingExternalCustomerMap(models.Model):
    _name = 'ming.external.customer.map'
    _description = 'Bản đồ khách hàng từ hệ thống ngoài'
    _order = 'write_date desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
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
    external_customer_id = fields.Char(index=True, copy=False, string='ID khách hàng ngoài hệ thống')
    external_customer_code = fields.Char(index=True, copy=False, string='Mã khách hàng ngoài hệ thống')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', index=True, string='Khách hàng Odoo')
    branch_id = fields.Many2one(related='partner_id.ming_branch_id', store=True, index=True, string='Chi nhánh')
    last_synced_at = fields.Datetime(copy=False, string='Lần đồng bộ gần nhất')
    raw_payload_hash = fields.Char(copy=False, string='Mã kiểm tra dữ liệu nguồn')
    raw_payload = fields.Text(copy=False, string='Dữ liệu nguồn gốc')
    active = fields.Boolean(default=True, string='Đang sử dụng')

    _external_customer_id_unique = models.Constraint(
        'UNIQUE(source_system, external_customer_id)',
        'Mỗi ID khách hàng ngoài hệ thống chỉ được có một bản đồ trong cùng một nguồn.',
    )
    _external_customer_code_unique = models.Constraint(
        'UNIQUE(source_system, external_customer_code)',
        'Mỗi mã khách hàng ngoài hệ thống chỉ được có một bản đồ trong cùng một nguồn.',
    )

    @api.depends('source_system', 'external_customer_id', 'external_customer_code', 'partner_id')
    def _compute_name(self):
        for record in self:
            identity = record.external_customer_id or record.external_customer_code or str(record.partner_id.id)
            record.name = '%s / %s' % (record.source_system or 'unknown', identity)
