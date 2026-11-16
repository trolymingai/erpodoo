# -*- coding: utf-8 -*-
import base64

from odoo.tests.common import TransactionCase


class TestMingImportSafety(TransactionCase):
    def setUp(self):
        super().setUp()
        self.branch = self.env['ming.branch'].create(
            {
                'name': 'Chi nhánh kiểm thử import',
                'code': 'TEST-IMPORT',
            }
        )

    def _run_import(self, content, file_name='customer_import.csv', allow_contact_updates=False):
        wizard = self.env['ming.customer.import.wizard'].create(
            {
                'file': base64.b64encode(content.encode('utf-8')),
                'file_name': file_name,
                'import_type': 'customer',
                'dry_run': False,
                'allow_contact_updates': allow_contact_updates,
            }
        )
        wizard.action_import()
        self.assertNotIn('Lỗi: 1', wizard.result or '')
        return wizard

    def test_configured_note_name_updates_customer_without_overwriting_notes(self):
        partner = self.env['res.partner'].create(
            {
                'name': 'Tên cũ trong ERP',
                'comment': 'Ghi chú ERP phải giữ nguyên',
                'ming_customer_note': 'Ghi chú CSKH phải giữ nguyên',
                'ming_pos_customer_code': 'SAFE-001',
                'ming_branch_id': self.branch.id,
                'ming_last_transaction_date': '2026-07-01',
                'ming_total_spent': 100,
            }
        )
        self._run_import(
            'Mã khách hàng,Ghi chú,Điện thoại,Chi nhánh,Tổng bán trừ trả hàng,Ngày giao dịch cuối\n'
            'SAFE-001,Tên mới từ ghi chú,0912345678,Chi nhánh kiểm thử import,250,2026-08-01\n'
        )

        partner.invalidate_recordset()
        self.assertEqual(partner.name, 'Tên mới từ ghi chú')
        self.assertIn('Ghi chú ERP phải giữ nguyên', partner.comment or '')
        self.assertEqual(partner.ming_customer_note, 'Ghi chú CSKH phải giữ nguyên')
        self.assertEqual(partner.ming_total_spent, 250)

    def test_source_note_is_visible_on_a_new_customer(self):
        self._run_import(
            'Mã khách hàng,Ghi chú,Điện thoại,Chi nhánh,Tổng bán trừ trả hàng,Ngày giao dịch cuối\n'
            'SAFE-NEW-NOTE,Khách mới từ ghi chú,0912345689,Chi nhánh kiểm thử import,125,2026-08-01\n',
            'new_customer_note.csv',
        )
        partner = self.env['res.partner'].search(
            [('ming_pos_customer_code', '=', 'SAFE-NEW-NOTE')], limit=1
        )
        self.assertEqual(partner.name, 'Khách mới từ ghi chú')
        self.assertEqual(partner.ming_customer_note, 'Khách mới từ ghi chú')

    def test_configured_note_name_replaces_phone_like_import_name(self):
        self.env['ming.segment.config'].create(
            {
                'display_name': 'Cấu hình tên từ ghi chú kiểm thử',
                'active': True,
                'pos_customer_name_key': 'ten_khach_hang',
                'pos_note_name_key': 'ghi_chu',
            }
        )
        partner = self.env['res.partner'].create(
            {
                'name': '0912345699',
                'ming_pos_customer_code': 'NOTE-NAME-001',
                'ming_customer_note': 'Ghi chú cũ phải giữ nguyên',
                'ming_branch_id': self.branch.id,
            }
        )
        self._run_import(
            'Mã khách hàng,Tên khách hàng,Ghi chú,Điện thoại,Chi nhánh,Tổng bán trừ trả hàng,Ngày giao dịch cuối\n'
            'NOTE-NAME-001,0912345699,GIA NHI,0912345699,Chi nhánh kiểm thử import,125,2026-08-01\n',
            'note_name_mapping.csv',
        )

        partner.invalidate_recordset()
        self.assertEqual(partner.name, 'GIA NHI')
        self.assertEqual(partner.ming_customer_note, 'Ghi chú cũ phải giữ nguyên')

    def test_contact_update_option_never_updates_notes(self):
        partner = self.env['res.partner'].create(
            {
                'name': 'Tên đang dùng',
                'phone': '0912345678',
                'email': 'cu@example.com',
                'comment': 'Ghi chú ERP không được đổi',
                'ming_customer_note': 'Ghi chú CSKH không được đổi',
                'ming_pos_customer_code': 'SAFE-UPDATE-001',
                'ming_branch_id': self.branch.id,
            }
        )
        content = (
            'Mã khách hàng,Tên khách,Điện thoại,Email,Chi nhánh,Tổng bán trừ trả hàng,Ngày giao dịch cuối\n'
            'SAFE-UPDATE-001,Tên mới,0987654321,moi@example.com,Chi nhánh kiểm thử import,250,2026-08-01\n'
        )

        self._run_import(content, 'contact_protected.csv')
        partner.invalidate_recordset()
        self.assertEqual(partner.name, 'Tên đang dùng')
        self.assertEqual(partner.phone, '0912345678')
        self.assertEqual(partner.email, 'cu@example.com')
        self.assertEqual(partner.comment, 'Ghi chú ERP không được đổi')
        self.assertEqual(partner.ming_customer_note, 'Ghi chú CSKH không được đổi')

        update_content = content.replace('250,2026-08-01', '251,2026-08-02')
        self._run_import(update_content, 'contact_update.csv', allow_contact_updates=True)
        partner.invalidate_recordset()
        self.assertEqual(partner.name, 'Tên mới')
        self.assertEqual(partner.phone, '0987654321')
        self.assertEqual(partner.email, 'moi@example.com')
        self.assertEqual(partner.comment, 'Ghi chú ERP không được đổi')
        self.assertEqual(partner.ming_customer_note, 'Ghi chú CSKH không được đổi')
        self.assertEqual(self.env['ming.purchase.history'].search_count([('partner_id', '=', partner.id)]), 1)

    def test_reimport_is_idempotent_for_purchase_history(self):
        content = (
            'Mã khách hàng,Ghi chú,Điện thoại,Chi nhánh,Tổng bán trừ trả hàng,Ngày giao dịch cuối\n'
            'SAFE-002,Khách mới,0912345678,Chi nhánh kiểm thử import,350,2026-08-01\n'
        )
        self._run_import(content, 'same_file.csv')
        self._run_import(content, 'same_file.csv')

        partner = self.env['res.partner'].search([('ming_pos_customer_code', '=', 'SAFE-002')], limit=1)
        self.assertTrue(partner)
        self.assertEqual(self.env['ming.purchase.history'].search_count([('partner_id', '=', partner.id)]), 1)

    def test_new_purchase_snapshot_is_added_without_erasing_the_old_snapshot(self):
        first = (
            'Mã khách hàng,Ghi chú,Điện thoại,Chi nhánh,Tổng bán trừ trả hàng,Ngày giao dịch cuối\n'
            'SAFE-003,Khách mới,0912345678,Chi nhánh kiểm thử import,350,2026-08-01\n'
        )
        second = (
            'Mã khách hàng,Ghi chú,Điện thoại,Chi nhánh,Tổng bán trừ trả hàng,Ngày giao dịch cuối\n'
            'SAFE-003,Khách mới,0912345678,Chi nhánh kiểm thử import,400,2026-08-02\n'
        )
        self._run_import(first, 'snapshot_1.csv')
        self._run_import(second, 'snapshot_2.csv')

        partner = self.env['res.partner'].search([('ming_pos_customer_code', '=', 'SAFE-003')], limit=1)
        histories = self.env['ming.purchase.history'].search([('partner_id', '=', partner.id)], order='transaction_date')
        self.assertEqual(len(histories), 2)
        self.assertEqual(histories[0].transaction_date.isoformat(), '2026-08-01')
        self.assertFalse(histories[0].is_latest)
        self.assertEqual(histories[1].transaction_date.isoformat(), '2026-08-02')
        self.assertTrue(histories[1].is_latest)
        self.assertEqual(partner.ming_total_spent, 400)

    def test_care_flags_are_recorded_on_customer(self):
        partner = self.env['res.partner'].create(
            {
                'name': 'Khách có cờ CSKH',
                'ming_branch_id': self.branch.id,
            }
        )
        self.env['ming.care.history'].create(
            {
                'partner_id': partner.id,
                'call_status': 'sent_offer',
                'manager_action_type': 'voucher',
                'note': 'Đã gọi và gửi voucher.',
            }
        )

        partner.invalidate_recordset()
        self.assertTrue(partner.ming_has_been_called)
        self.assertTrue(partner.ming_received_voucher)

        alert = self.env['ming.retention.alert'].create(
            {
                'partner_id': partner.id,
                'alert_level': '1',
                'alert_type': 'at_risk',
            }
        )
        alert.action_mark_converted()
        partner.invalidate_recordset()
        self.assertTrue(partner.ming_has_returned)
        self.assertTrue(partner.ming_returned_at)

    def test_staff_care_flags_can_be_selected_on_customer(self):
        partner = self.env['res.partner'].create(
            {
                'name': 'Khách chọn trạng thái CSKH',
                'ming_branch_id': self.branch.id,
            }
        )
        partner.write(
            {
                'ming_has_been_called': True,
                'ming_received_voucher': True,
                'ming_has_returned': True,
            }
        )
        self.assertTrue(partner.ming_has_been_called)
        self.assertTrue(partner.ming_received_voucher)
        self.assertTrue(partner.ming_has_returned)
        self.assertTrue(partner.ming_returned_at)

        partner.write({'ming_has_returned': False})
        self.assertFalse(partner.ming_has_returned)
        self.assertFalse(partner.ming_returned_at)
