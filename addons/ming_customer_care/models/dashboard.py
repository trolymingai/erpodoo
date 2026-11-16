# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MingDashboardBoard(models.Model):
    _name = 'ming.dashboard.board'
    _description = 'B\u1ea3ng \u0111i\u1ec1u h\u00e0nh Ming Customer Care'

    name = fields.Char(default='B\u1ea3ng \u0111i\u1ec1u h\u00e0nh CSKH Ming', required=True, string='T\u00ean b\u1ea3ng \u0111i\u1ec1u h\u00e0nh')
    total_customers = fields.Integer(compute='_compute_dashboard', string='T\u1ed5ng kh\u00e1ch h\u00e0ng')
    active_customers = fields.Integer(compute='_compute_dashboard', string='Kh\u00e1ch \u0111ang ho\u1ea1t \u0111\u1ed9ng')
    at_risk_customers = fields.Integer(compute='_compute_dashboard', string='Kh\u00e1ch c\u00f3 nguy c\u01a1')
    lost_customers = fields.Integer(compute='_compute_dashboard', string='Kh\u00e1ch \u0111\u00e3 m\u1ea5t')
    vip_customers = fields.Integer(compute='_compute_dashboard', string='Kh\u00e1ch VIP')
    vip_at_risk_customers = fields.Integer(compute='_compute_dashboard', string='VIP c\u00f3 nguy c\u01a1')
    tasks_today = fields.Integer(compute='_compute_dashboard', string='C\u00f4ng vi\u1ec7c c\u1ea7n g\u1ecdi h\u00f4m nay')
    pending_tasks = fields.Integer(compute='_compute_dashboard', string='C\u00f4ng vi\u1ec7c ch\u01b0a x\u1eed l\u00fd')
    in_progress_tasks = fields.Integer(compute='_compute_dashboard', string='C\u00f4ng vi\u1ec7c \u0111ang x\u1eed l\u00fd')
    overdue_tasks = fields.Integer(compute='_compute_dashboard', string='C\u00f4ng vi\u1ec7c qu\u00e1 h\u1ea1n')
    done_today_tasks = fields.Integer(compute='_compute_dashboard', string='C\u00f4ng vi\u1ec7c \u0111\u00e3 ho\u00e0n t\u1ea5t h\u00f4m nay')
    alert_level_1_count = fields.Integer(compute='_compute_dashboard', string='C\u1ea3nh b\u00e1o l\u1ea7n 1')
    alert_level_2_count = fields.Integer(compute='_compute_dashboard', string='C\u1ea3nh b\u00e1o l\u1ea7n 2')
    alert_level_3_count = fields.Integer(compute='_compute_dashboard', string='C\u1ea3nh b\u00e1o l\u1ea7n 3')
    negative_feedback_count = fields.Integer(compute='_compute_dashboard', string='Ph\u1ea3n h\u1ed3i ti\u00eau c\u1ef1c')
    message_log_count = fields.Integer(compute='_compute_dashboard', string='Nh\u1eadt k\u00fd SMS/email/Lark')
    task_done_count = fields.Integer(compute='_compute_dashboard', string='T\u1ed5ng c\u00f4ng vi\u1ec7c \u0111\u00e3 ho\u00e0n t\u1ea5t')
    task_completion_rate = fields.Float(compute='_compute_dashboard', string='T\u1ef7 l\u1ec7 ho\u00e0n t\u1ea5t c\u00f4ng vi\u1ec7c (%)')
    risk_branch_summary = fields.Html(compute='_compute_dashboard', sanitize=False, string='Top chi nh\u00e1nh c\u00f3 nguy c\u01a1')
    product_revenue_summary = fields.Html(compute='_compute_dashboard', sanitize=False, string='Top s\u1ea3n ph\u1ea9m/doanh thu')
    employee_task_summary = fields.Html(compute='_compute_dashboard', sanitize=False, string='C\u00f4ng vi\u1ec7c theo nh\u00e2n vi\u00ean')
    branch_task_summary = fields.Html(compute='_compute_dashboard', sanitize=False, string='Hi\u1ec7u su\u1ea5t theo chi nh\u00e1nh')
    today_task_ids = fields.Many2many('ming.care.task', compute='_compute_dashboard', string='Danh s\u00e1ch c\u1ea7n g\u1ecdi h\u00f4m nay')
    overdue_task_ids = fields.Many2many('ming.care.task', compute='_compute_dashboard', string='Danh s\u00e1ch c\u00f4ng vi\u1ec7c qu\u00e1 h\u1ea1n')
    vip_risk_partner_ids = fields.Many2many('res.partner', compute='_compute_dashboard', string='Danh sach VIP c\u00f3 nguy c\u01a1')

    def _user_has_full_scope(self):
        user = self.env.user
        return user.has_group('ming_customer_care.group_ming_founder_admin') or user.has_group('base.group_system')

    def _branch_scope_ids(self):
        if self._user_has_full_scope():
            return []
        return self.env.user.ming_branch_ids.ids or [-1]

    def _scoped_domain(self, field_name):
        branch_ids = self._branch_scope_ids()
        if not branch_ids:
            return []
        return [(field_name, 'in', branch_ids)]

    def _build_summary_html(self, headers, rows):
        if not rows:
            return '<p>Ch\u01b0a c\u00f3 d\u1eef li\u1ec7u.</p>'
        thead = ''.join('<th>%s</th>' % header for header in headers)
        body = []
        for row in rows:
            body.append('<tr>%s</tr>' % ''.join('<td>%s</td>' % cell for cell in row))
        return '<table class="table table-sm table-striped"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (
            thead,
            ''.join(body),
        )

    def _branch_records(self, partner_model, partner_domain):
        branch_domain = list(partner_domain)
        if self._branch_scope_ids():
            branch_domain = [item for item in branch_domain if item[0] != 'ming_branch_id']
        partners = partner_model.search(branch_domain)
        return partners.mapped('ming_branch_id')

    @api.depends_context('uid')
    def _compute_dashboard(self):
        today = fields.Date.context_today(self)
        Partner = self.env['res.partner'].sudo()
        Task = self.env['ming.care.task'].sudo()
        Alert = self.env['ming.retention.alert'].sudo()
        History = self.env['ming.care.history'].sudo()
        MessageLog = self.env['ming.message.log'].sudo()
        SalesLine = self.env['ming.sales.product.line'].sudo()

        partner_domain = [
            '|',
            ('ming_pos_customer_code', '!=', False),
            '&',
            ('ming_source_system', '!=', False),
            ('ming_branch_id', '!=', False),
        ] + self._scoped_domain('ming_branch_id')
        task_domain = self._scoped_domain('branch_id')
        alert_domain = self._scoped_domain('branch_id')
        history_domain = self._scoped_domain('branch_id')
        message_domain = self._scoped_domain('partner_id.ming_branch_id')
        sales_domain = []
        branch_ids = self._branch_scope_ids()
        if branch_ids:
            sales_domain = [('branch_id', 'in', branch_ids)]

        for rec in self:
            rec.total_customers = Partner.search_count(partner_domain)
            rec.active_customers = Partner.search_count(partner_domain + [('ming_activity_status', '=', 'active')])
            rec.at_risk_customers = Partner.search_count(partner_domain + [('ming_activity_status', '=', 'at_risk')])
            rec.lost_customers = Partner.search_count(partner_domain + [('ming_activity_status', '=', 'lost')])
            rec.vip_customers = Partner.search_count(partner_domain + [('ming_is_vip', '=', True)])
            rec.vip_at_risk_customers = Partner.search_count(
                partner_domain + [('ming_is_vip', '=', True), ('ming_activity_status', '=', 'at_risk')]
            )

            today_domain = task_domain + [('due_date', '=', today), ('pipeline_status', '!=', 'cancelled')]
            rec.tasks_today = Task.search_count(today_domain)
            rec.pending_tasks = Task.search_count(task_domain + [('pipeline_status', '=', 'pending')])
            rec.in_progress_tasks = Task.search_count(task_domain + [('pipeline_status', '=', 'in_progress')])
            rec.overdue_tasks = Task.search_count(
                task_domain + [('due_date', '<', today), ('pipeline_status', 'in', ['pending', 'in_progress'])]
            )
            rec.done_today_tasks = Task.search_count(
                task_domain + [('completed_at', '>=', '%s 00:00:00' % today), ('completed_at', '<=', '%s 23:59:59' % today)]
            )

            rec.alert_level_1_count = Alert.search_count(alert_domain + [('alert_level', '=', '1')])
            rec.alert_level_2_count = Alert.search_count(alert_domain + [('alert_level', '=', '2')])
            rec.alert_level_3_count = Alert.search_count(alert_domain + [('alert_level', '=', '3')])
            rec.negative_feedback_count = History.search_count(history_domain + [('call_status', '=', 'negative_feedback')])
            rec.message_log_count = MessageLog.search_count(message_domain)

            task_total = Task.search_count(today_domain)
            rec.task_done_count = Task.search_count(task_domain + [('pipeline_status', '=', 'done')])
            rec.task_completion_rate = round((rec.done_today_tasks / task_total) * 100.0, 2) if task_total else 0.0

            risk_rows = []
            for branch_value, branch_count in Partner._read_group(
                partner_domain + [('ming_activity_status', '=', 'at_risk')],
                ['ming_branch_id'],
                ['__count'],
            ):
                branch_name = branch_value.display_name if branch_value else 'Ch\u01b0a g\u00e1n chi nh\u00e1nh'
                risk_rows.append((branch_name, branch_count))
            risk_rows = sorted(risk_rows, key=lambda item: item[1], reverse=True)[:5]
            rec.risk_branch_summary = self._build_summary_html(['Chi nh\u00e1nh', 'Kh\u00e1ch c\u00f3 nguy c\u01a1'], risk_rows)

            sales_rows = []
            for product_name, net_revenue in SalesLine._read_group(
                sales_domain,
                ['product_name'],
                ['net_revenue:sum'],
            ):
                sales_rows.append((product_name or 'Ch\u01b0a g\u00e1n s\u1ea3n ph\u1ea9m', '{:,.0f}'.format(net_revenue or 0.0)))
            sales_rows = sorted(sales_rows, key=lambda item: float(item[1].replace(',', '')), reverse=True)[:5]
            rec.product_revenue_summary = self._build_summary_html(['S\u1ea3n ph\u1ea9m', 'Doanh thu thu\u1ea7n'], sales_rows)

            employee_rows = []
            users = Task.search(task_domain).mapped('assigned_user_id')
            for user in users:
                user_name = user.display_name or 'Ch\u01b0a ph\u00e2n c\u00f4ng'
                pending_count = Task.search_count(task_domain + [('assigned_user_id', '=', user.id), ('pipeline_status', '=', 'pending')])
                progress_count = Task.search_count(task_domain + [('assigned_user_id', '=', user.id), ('pipeline_status', '=', 'in_progress')])
                done_count = Task.search_count(
                    task_domain + [('assigned_user_id', '=', user.id), ('completed_at', '>=', '%s 00:00:00' % today), ('completed_at', '<=', '%s 23:59:59' % today)]
                )
                employee_rows.append((user_name, pending_count, progress_count, done_count))
            employee_rows = sorted(employee_rows, key=lambda item: (item[1] + item[2]), reverse=True)[:8]
            rec.employee_task_summary = self._build_summary_html(
                ['Nh\u00e2n vi\u00ean', 'Ch\u01b0a x\u1eed l\u00fd', '\u0110ang x\u1eed l\u00fd', 'Ho\u00e0n t\u1ea5t h\u00f4m nay'],
                employee_rows,
            )

            branch_rows = []
            for branch in self._branch_records(Partner, partner_domain):
                branch_name = branch.display_name or 'Ch\u01b0a g\u00e1n chi nh\u00e1nh'
                branch_task_domain = task_domain + [('branch_id', '=', branch.id)]
                branch_today_domain = branch_task_domain + [('due_date', '=', today), ('pipeline_status', '!=', 'cancelled')]
                branch_today = Task.search_count(branch_today_domain)
                branch_overdue = Task.search_count(
                    branch_task_domain + [('due_date', '<', today), ('pipeline_status', 'in', ['pending', 'in_progress'])]
                )
                branch_done_today = Task.search_count(
                    branch_task_domain + [('completed_at', '>=', '%s 00:00:00' % today), ('completed_at', '<=', '%s 23:59:59' % today)]
                )
                branch_rate = round((branch_done_today / branch_today) * 100.0, 2) if branch_today else 0.0
                branch_rows.append((branch_name, branch_today, branch_overdue, '%s%%' % branch_rate))
            branch_rows = sorted(branch_rows, key=lambda item: item[1], reverse=True)[:8]
            rec.branch_task_summary = self._build_summary_html(
                ['Chi nh\u00e1nh', 'C\u00f4ng vi\u1ec7c h\u00f4m nay', 'Qu\u00e1 h\u1ea1n', 'T\u1ef7 l\u1ec7 ho\u00e0n t\u1ea5t'],
                branch_rows,
            )

            rec.today_task_ids = Task.search(
                task_domain + [('due_date', '<=', today), ('pipeline_status', 'in', ['pending', 'in_progress'])],
                limit=10,
                order='is_vip desc,total_spent desc,priority desc,due_date asc',
            )
            rec.overdue_task_ids = Task.search(
                task_domain + [('due_date', '<', today), ('pipeline_status', 'in', ['pending', 'in_progress'])],
                limit=10,
                order='is_vip desc,total_spent desc,priority desc,due_date asc',
            )
            rec.vip_risk_partner_ids = Partner.search(
                partner_domain + [('ming_is_vip', '=', True), ('ming_activity_status', '=', 'at_risk')],
                limit=10,
                order='ming_total_spent desc, ming_days_absent desc',
            )

    def action_refresh_dashboard(self):
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_open_today_tasks(self):
        action = self.env.ref('ming_customer_care.action_ming_care_task').sudo().read()[0]
        action['domain'] = [('due_date', '<=', fields.Date.context_today(self)), ('pipeline_status', 'in', ['pending', 'in_progress'])]
        return action

    def action_open_overdue_tasks(self):
        return self.env.ref('ming_customer_care.action_ming_manager_overdue_tasks').sudo().read()[0]

    def action_open_alerts(self):
        return self.env.ref('ming_customer_care.action_ming_retention_alert').sudo().read()[0]

    def action_open_messages(self):
        return self.env.ref('ming_customer_care.action_ming_message_log').sudo().read()[0]
