# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tools.safe_eval import safe_eval
from odoo.tests.common import TransactionCase


class TestMingOperationalContract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.context_today(cls.env['res.partner'])

    def _branch(self, code, manager=False):
        values = {'name': 'Test %s' % code, 'code': code}
        if manager:
            values['manager_id'] = manager.id
        return self.env['ming.branch'].create(values)

    def _partner(self, branch, name, days_absent=1, total_spent=0):
        return self.env['res.partner'].create(
            {
                'name': name,
                'ming_branch_id': branch.id,
                'ming_pos_customer_code': 'TEST-%s' % name.replace(' ', '-'),
                'ming_last_transaction_date': self.today - timedelta(days=days_absent),
                'ming_total_spent': total_spent,
            }
        )

    def test_vip_ranking_is_calculated_per_branch(self):
        branch_a = self._branch('TEST-A')
        branch_b = self._branch('TEST-B')
        for branch in (branch_a, branch_b):
            self.env['ming.segment.config'].create(
                {
                    'branch_id': branch.id,
                    'vip_percent': 40,
                }
            )
            for index in range(1, 6):
                self._partner(branch, '%s Customer %s' % (branch.code, index), total_spent=1000 - index)

        self.env['ming.retention.engine'].cron_run_retention_engine()

        for branch in (branch_a, branch_b):
            partners = self.env['res.partner'].search([('ming_branch_id', '=', branch.id)])
            self.assertEqual(partners.filtered('ming_is_vip').ids, partners.sorted('ming_total_spent', reverse=True)[:2].ids)
            self.assertEqual(partners.filtered('ming_vip_rank').mapped('ming_vip_rank'), [1, 2])

    def test_manual_customer_with_branch_is_in_ming_scope(self):
        branch = self._branch('TEST-MANUAL')
        partner = self.env['res.partner'].create(
            {
                'name': 'Manual Customer',
                'ming_source_system': 'manual',
                'ming_branch_id': branch.id,
                'ming_last_transaction_date': self.today,
            }
        )

        action = self.env.ref('ming_customer_care.action_ming_customer_list')
        domain = safe_eval(action.domain or '[]')

        self.assertIn(partner, self.env['res.partner'].search(domain))

    def test_retention_reuses_existing_open_task_without_alert(self):
        branch = self._branch('TEST-TASK')
        partner = self._partner(branch, 'Open Task Customer', days_absent=40, total_spent=100)
        existing = self.env['ming.care.task'].create(
            {
                'name': 'Task đã có',
                'partner_id': partner.id,
                'task_type': 'at_risk',
                'pipeline_status': 'pending',
            }
        )

        self.env['ming.retention.engine'].cron_run_retention_engine()

        self.assertEqual(
            self.env['ming.care.task'].search_count(
                [('partner_id', '=', partner.id), ('task_type', '=', 'at_risk'), ('pipeline_status', 'in', ('pending', 'in_progress'))]
            ),
            1,
        )
        self.assertTrue(existing.latest_history_id or existing.id)

    def test_negative_feedback_escalates_once_to_manager(self):
        manager = self.env.user
        branch = self._branch('TEST-NEG', manager=manager)
        partner = self._partner(branch, 'Negative Customer')
        task = self.env['ming.care.task'].create({'name': 'Gọi khách', 'partner_id': partner.id})
        values = {
            'partner_id': partner.id,
            'task_id': task.id,
            'call_status': 'negative_feedback',
            'note': 'Khách phản hồi chưa hài lòng.',
        }

        self.env['ming.care.history'].create(values)
        self.env['ming.care.history'].create(values)

        manager_tasks = self.env['ming.care.task'].search(
            [('partner_id', '=', partner.id), ('task_type', '=', 'negative_feedback'), ('pipeline_status', 'in', ('pending', 'in_progress'))]
        )
        self.assertEqual(len(manager_tasks), 1)
        self.assertEqual(manager_tasks.assigned_user_id, manager)
        self.assertEqual(manager_tasks.priority, '3')

    def test_callback_does_not_create_duplicate_open_follow_up(self):
        branch = self._branch('TEST-CALLBACK')
        partner = self._partner(branch, 'Callback Customer')
        task = self.env['ming.care.task'].create({'name': 'Gọi khách', 'partner_id': partner.id})
        follow_up_date = self.today + timedelta(days=2)
        values = {
            'partner_id': partner.id,
            'task_id': task.id,
            'call_status': 'callback_2',
            'follow_up_date': follow_up_date,
        }

        self.env['ming.care.history'].create(values)
        self.env['ming.care.history'].create(values)

        self.assertEqual(
            self.env['ming.care.task'].search_count(
                [('partner_id', '=', partner.id), ('task_type', '=', 'follow_up'), ('pipeline_status', 'in', ('pending', 'in_progress'))]
            ),
            1,
        )

    def test_recent_transaction_converts_open_alert(self):
        branch = self._branch('TEST-CONVERT')
        partner = self._partner(branch, 'Returning Customer', days_absent=40, total_spent=100)

        self.env['ming.retention.engine'].cron_run_retention_engine()
        alert = self.env['ming.retention.alert'].search([('partner_id', '=', partner.id)], limit=1)
        self.assertTrue(alert)

        partner.write({'ming_last_transaction_date': self.today})
        self.env['ming.retention.engine'].cron_run_retention_engine()

        self.assertEqual(alert.status, 'converted')
        self.assertTrue(alert.converted_at)

    def test_disabled_channel_is_logged_without_provider_call(self):
        config = self.env['ming.segment.config'].search([('branch_id', '=', False)], limit=1)
        config.write(
            {
                'safe_mode': False,
                'test_mode': False,
                'sms_enabled': True,
                'send_sms_enabled': False,
                'sms_unit_cost': 1,
            }
        )
        partner = self._partner(self._branch('TEST-SMS'), 'SMS Customer')
        partner.write({'phone': '0912345678'})

        log = self.env['ming.message.service'].send_message(partner, 'sms', 'Nội dung test', confirmed_cost=True)

        self.assertEqual(log.status, 'rejected')
        self.assertIn('tắt', log.error_message)

    def test_resending_a_safe_mode_log_does_not_create_a_second_log(self):
        config = self.env['ming.segment.config'].search([('branch_id', '=', False)], limit=1)
        config.write({'safe_mode': True})
        partner = self._partner(self._branch('TEST-LOG'), 'Log Customer')
        partner.write({'phone': '0912345678'})
        log = self.env['ming.message.log'].create(
            {
                'partner_id': partner.id,
                'channel': 'sms',
                'recipient': '+84912345678',
                'content': 'Nội dung test',
            }
        )
        count_before = self.env['ming.message.log'].search_count([])

        log.action_send()

        self.assertEqual(self.env['ming.message.log'].search_count([]), count_before)
        self.assertEqual(log.status, 'safe_mode')
