# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MingPurchaseHistory(models.Model):
    _name = 'ming.purchase.history'
    _description = 'Lịch sử mua hàng từ POS/KiotViet'
    _order = 'transaction_date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(compute='_compute_name', store=True, string='Lần mua hàng')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', index=True, string='Khách hàng')
    branch_id = fields.Many2one(related='partner_id.ming_branch_id', store=True, index=True, string='Chi nhánh')
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
    source_file_name = fields.Char(string='Tập tin nguồn')
    source_key = fields.Char(required=True, index=True, copy=False, string='Khóa dữ liệu nguồn')
    external_customer_id = fields.Char(index=True, copy=False, string='ID khách ngoài hệ thống')
    external_customer_code = fields.Char(index=True, copy=False, string='Mã khách ngoài hệ thống')
    transaction_date = fields.Date(index=True, string='Ngày giao dịch')
    total_spent = fields.Monetary(currency_field='currency_id', string='Tổng chi tiêu tại thời điểm nhập')
    loyalty_points = fields.Integer(string='Điểm tích lũy tại thời điểm nhập')
    is_latest = fields.Boolean(default=True, index=True, string='Lần mua gần nhất')
    imported_at = fields.Datetime(default=fields.Datetime.now, required=True, string='Thời điểm ghi nhận')
    import_job_id = fields.Many2one('ming.import.job', ondelete='set null', index=True, string='Đợt nhập liệu')
    sync_log_id = fields.Many2one('ming.external.sync.log', ondelete='set null', index=True, string='Nhật ký đồng bộ')
    currency_id = fields.Many2one(related='partner_id.ming_currency_id', readonly=True, string='Tiền tệ')
    raw_data = fields.Text(copy=False, string='Dữ liệu nguồn')

    @api.depends('partner_id', 'transaction_date', 'source_system')
    def _compute_name(self):
        for record in self:
            date_label = fields.Date.to_string(record.transaction_date) if record.transaction_date else 'Chưa có ngày'
            source_label = dict(record._fields['source_system'].selection).get(record.source_system, record.source_system or 'Nguồn khác')
            record.name = '%s - %s (%s)' % (record.partner_id.display_name or 'Khách hàng', date_label, source_label)
