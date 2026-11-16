import random
import time
from datetime import timedelta

from odoo import fields


def ensure_branch(env, code, name):
    branch = env['ming.branch'].search([('code', '=', code)], limit=1)
    if not branch:
        branch = env['ming.branch'].create({'code': code, 'name': name, 'brand': 'ming'})
    return branch


def ensure_config(env):
    config = env['ming.segment.config'].search([], limit=1)
    if not config:
        config = env['ming.segment.config'].create({'display_name': 'Cấu hình benchmark'})
    config.write({'safe_mode': True, 'vip_percent': 10.0, 'active_days_threshold': 30, 'lost_days_threshold': 90})
    return config


def create_large_customer_set(env, total_customers=15000):
    branches = [
        ensure_branch(env, 'MING-B1', 'Ming Quận 1'),
        ensure_branch(env, 'MING-B3', 'Ming Quận 3'),
        ensure_branch(env, 'MING-B7', 'Ming Quận 7'),
    ]
    today = fields.Date.context_today(env.user)
    partners = env['res.partner'].search_count([('ming_pos_customer_code', 'like', 'PHASE3-UAT-%')])
    if partners >= total_customers:
        return

    vals_list = []
    for index in range(total_customers):
        branch = branches[index % len(branches)]
        absent_days = index % 140
        last_tx = today - timedelta(days=absent_days)
        phone_suffix = str(900000000 + index).zfill(9)
        vals_list.append(
            {
                'name': 'Khách UAT %05d' % index,
                'ming_pos_customer_code': 'PHASE3-UAT-%05d' % index,
                'phone': '0%s' % phone_suffix,
                'email': 'uat%05d@ming.local' % index,
                'ming_branch_id': branch.id,
                'ming_source_system': 'pos_excel',
                'ming_total_spent': float(50000 + ((index * 13791) % 5000000)),
                'ming_loyalty_points': index % 800,
                'ming_last_transaction_date': last_tx,
                'ming_allow_sms': True,
                'ming_allow_email': True,
            }
        )
        if len(vals_list) == 1000:
            env['res.partner'].create(vals_list)
            vals_list = []
    if vals_list:
        env['res.partner'].create(vals_list)


def run():
    ensure_config(env)
    create_large_customer_set(env)
    board = env.ref('ming_customer_care.dashboard_main')

    start_1 = time.perf_counter()
    env['ming.retention.engine'].cron_run_retention_engine()
    cron_first = round(time.perf_counter() - start_1, 2)

    task_count_1 = env['ming.care.task'].search_count([('partner_id.ming_pos_customer_code', 'like', 'PHASE3-UAT-%')])
    alert_count_1 = env['ming.retention.alert'].search_count([('partner_id.ming_pos_customer_code', 'like', 'PHASE3-UAT-%')])

    start_2 = time.perf_counter()
    env['ming.retention.engine'].cron_run_retention_engine()
    cron_second = round(time.perf_counter() - start_2, 2)

    task_count_2 = env['ming.care.task'].search_count([('partner_id.ming_pos_customer_code', 'like', 'PHASE3-UAT-%')])
    alert_count_2 = env['ming.retention.alert'].search_count([('partner_id.ming_pos_customer_code', 'like', 'PHASE3-UAT-%')])

    start_dashboard = time.perf_counter()
    board.invalidate_recordset()
    board._compute_dashboard()
    dashboard_seconds = round(time.perf_counter() - start_dashboard, 2)

    total_customers = env['res.partner'].search_count([('ming_pos_customer_code', 'like', 'PHASE3-UAT-%')])
    vip_customers = env['res.partner'].search_count(
        [('ming_pos_customer_code', 'like', 'PHASE3-UAT-%'), ('ming_is_vip', '=', True)]
    )
    vip_rate = round((vip_customers / total_customers) * 100.0, 2) if total_customers else 0.0

    print(
        {
            'total_customers': total_customers,
            'cron_first_seconds': cron_first,
            'cron_second_seconds': cron_second,
            'dashboard_seconds': dashboard_seconds,
            'task_count_first': task_count_1,
            'task_count_second': task_count_2,
            'alert_count_first': alert_count_1,
            'alert_count_second': alert_count_2,
            'task_duplicates_created': task_count_2 - task_count_1,
            'alert_duplicates_created': alert_count_2 - alert_count_1,
            'vip_customers': vip_customers,
            'vip_rate_percent': vip_rate,
            'safe_mode': env['ming.segment.config'].search([], limit=1).safe_mode,
        }
    )


run()
