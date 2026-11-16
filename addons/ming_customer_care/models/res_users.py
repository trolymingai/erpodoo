# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    ming_branch_ids = fields.Many2many(
        'ming.branch',
        'ming_branch_res_users_rel',
        'res_users_id',
        'ming_branch_id',
        string='Chi nhánh được xem',
    )
    ming_default_branch_id = fields.Many2one('ming.branch', string='Chi nhánh mặc định')
