# -*- coding: utf-8 -*-
import base64
import csv
import re
import json
import unicodedata
from io import BytesIO, StringIO

from openpyxl import load_workbook

from odoo import _, fields, models, tools
from odoo.exceptions import UserError

from ..data_ingestion_utils import (
    CUSTOMER_REQUIRED_HEADERS,
    missing_required_headers,
    normalize_identity,
    normalize_header,
    normalize_row_keys,
    parse_import_date,
    stable_source_key,
)


class MingImportRowError(UserError):
    def __init__(self, message, *, duplicate=False, invalid_phone=False, unmatched_branch=False):
        self.duplicate = duplicate
        self.invalid_phone = invalid_phone
        self.unmatched_branch = unmatched_branch
        super().__init__(message)


class MingCustomerImportWizard(models.TransientModel):
    _name = 'ming.customer.import.wizard'
    _description = 'Import dữ liệu Ming từ CSV/XLSX'

    file = fields.Binary(required=True, string='Tệp dữ liệu')
    file_name = fields.Char(required=True, string='Tên tệp')
    import_type = fields.Selection(
        [('customer', 'Khách hàng CSV/XLSX'), ('care_task', 'Công việc CSKH CSV/XLSX'), ('sales_product', 'Bán hàng theo sản phẩm CSV/XLSX')],
        default='customer',
        required=True,
        string='Loại dữ liệu',
    )
    branch_id = fields.Many2one('ming.branch', string='Chi nhánh áp dụng')
    dry_run = fields.Boolean(default=True, string='Chỉ kiểm tra, chưa ghi dữ liệu')
    allow_contact_updates = fields.Boolean(
        default=False,
        string='Cho phép cập nhật tên/SĐT/email đã có',
        help=(
            'Khi bật, dữ liệu nhập có thể cập nhật tên, SĐT và email đã có trên khách hàng. '
            'Nếu cột ghi chú được cấu hình làm tên hiển thị thì cột đó luôn được ưu tiên cho tên. '
            'Không bao giờ ghi đè ghi chú ERP, ghi chú CSKH, chi tiêu, điểm, ngày giao dịch, '
            'trạng thái, VIP hoặc cờ vận hành.'
        ),
    )
    result = fields.Text(readonly=True, string='Kết quả import')

    def _pick(self, row, *keys):
        for key in keys:
            value = row.get(key)
            if value in (None, ''):
                value = row.get(normalize_header(key))
            if value not in (None, ''):
                return value
        return False

    def _has_value(self, row, *keys):
        return self._pick(row, *keys) not in (None, False, '')

    def _to_bool(self, value, default=False):
        if value in (None, ''):
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ('1', 'true', 't', 'yes', 'y')

    def _to_float(self, value, default=0.0):
        if value in (None, ''):
            return default
        normalized = str(value).replace(',', '').strip()
        if normalized.lower() in ('false', 'none', 'null'):
            return default
        try:
            return float(normalized)
        except (TypeError, ValueError) as exc:
            raise MingImportRowError('Giá trị số không hợp lệ: %s' % value) from exc

    def _to_int(self, value, default=0):
        if value in (None, ''):
            return default
        normalized = str(value).replace(',', '').strip()
        if normalized.lower() in ('false', 'none', 'null'):
            return default
        try:
            return int(float(normalized))
        except (TypeError, ValueError) as exc:
            raise MingImportRowError('Giá trị số nguyên không hợp lệ: %s' % value) from exc

    def _date_value(self, value, label):
        if value in (None, ''):
            return False
        try:
            return parse_import_date(value).isoformat()
        except ValueError as exc:
            raise MingImportRowError('%s: %s' % (label, exc)) from exc

    def _normalize_source_system(self, value):
        allowed = dict(self.env['res.partner']._fields['ming_source_system'].selection)
        source = str(value or '').strip()
        return source if source in allowed else 'pos_excel'

    def _normalize_text(self, value):
        text = unicodedata.normalize('NFKD', (value or '').strip())
        text = ''.join(ch for ch in text if not unicodedata.combining(ch)).lower().replace('đ', 'd')
        return ' '.join(re.sub(r'[^0-9a-z]+', ' ', text).split())

    def _resolve_branch(self, row):
        if self.branch_id:
            return self.branch_id
        branch_model = self.env['ming.branch'].sudo()
        branch_code = self._pick(row, 'Branch Code', 'branch_code', 'chi_nhanh', 'ma_chi_nhanh')
        if branch_code:
            branch = branch_model.search([('code', '=', str(branch_code).strip())], limit=1)
            if branch:
                return branch
        branch_name = self._pick(row, 'branch', 'branch_name', 'Branch Name', 'chi_nhanh', 'ten_chi_nhanh')
        if not branch_name:
            return branch_model.browse()
        branch_name = str(branch_name).strip()
        branch = branch_model.search([('name', '=', branch_name)], limit=1)
        if branch:
            return branch
        normalized_target = self._normalize_text(branch_name.split(',')[0])
        for item in branch_model.search([]):
            if self._normalize_text(item.name) == normalized_target:
                return item
            aliases = {
                self._normalize_text(alias)
                for alias in (item.source_aliases or '').splitlines()
                if alias.strip()
            }
            if normalized_target in aliases:
                return item
        return branch_model.browse()

    def _required_headers(self):
        if self.import_type == 'customer':
            requirements = list(CUSTOMER_REQUIRED_HEADERS)
            if self.branch_id:
                requirements = [item for item in requirements if item[0] != 'branch']
            return requirements
        if self.import_type == 'care_task':
            return [
                ('customer_identity', {'customer_id', 'ming_pos_customer_code', 'ma_kh', 'ma_khach', 'ma_khach_hang', 'phone', 'sdt', 'name', 'ten_khach', 'ten_khach_hang', 'customer_name'}),
                ('due_date', {'due_date', 'ngay_can_goi'}),
            ]
        return [
            ('source_file', {'source_file', 'file_name'}),
            ('period_start', {'period_start', 'from_date', 'tu_ngay'}),
            ('period_end', {'period_end', 'to_date', 'den_ngay'}),
            ('branch', {'branch', 'branch_name', 'branch_code', 'chi_nhanh', 'ma_chi_nhanh'}),
            ('product_code', {'product_code', 'ma_san_pham'}),
            ('product_name', {'product_name', 'ten_san_pham'}),
        ]

    def _validate_headers(self, rows):
        if not rows:
            raise UserError(_('Tệp không có dòng dữ liệu.'))
        missing = missing_required_headers(rows[0].keys(), self._required_headers())
        if missing:
            raise UserError(_('Thiếu cột bắt buộc: %s') % ', '.join(missing))

    def _read_rows(self):
        raw = base64.b64decode(self.file)
        if self.file_name.lower().endswith('.csv'):
            return [normalize_row_keys(row) for row in csv.DictReader(StringIO(raw.decode('utf-8-sig')))]
        if self.file_name.lower().endswith('.xlsx'):
            workbook = load_workbook(filename=BytesIO(raw), read_only=True, data_only=True)
            sheet = workbook.active
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                return []
            headers = [str(value).strip() if value is not None else '' for value in rows[0]]
            output = []
            for row in rows[1:]:
                if not any(value not in (None, '') for value in row):
                    continue
                item = {}
                for index, header in enumerate(headers):
                    if not header:
                        continue
                    value = row[index] if index < len(row) else None
                    item[header] = '' if value is None else str(value).strip()
                output.append(normalize_row_keys(item))
            return output
        raise UserError(_('Chỉ hỗ trợ tệp .csv và .xlsx.'))

    def _apply_configured_pos_mapping(self, rows):
        Config = self.env['ming.segment.config'].sudo()
        config = False
        if self.branch_id:
            config = Config.search([('active', '=', True), ('branch_id', '=', self.branch_id.id)], order='id desc', limit=1)
        if not config:
            config = Config.search([('active', '=', True), ('branch_id', '=', False)], order='id desc', limit=1)
        if not config:
            return rows
        configured_fields = (
            ('pos_customer_code_key', 'ming_pos_customer_code'),
            ('pos_customer_name_key', 'name'),
            ('pos_note_name_key', 'ghi_chu'),
            ('pos_phone_key', 'dien_thoai'),
            ('pos_branch_key', 'chi_nhanh'),
            ('pos_total_spent_key', 'tong_ban_tru_tra_hang'),
            ('pos_loyalty_points_key', 'diem_hien_tai'),
            ('pos_last_transaction_key', 'ngay_giao_dich_cuoi'),
        )
        for row in rows:
            for config_field, canonical_key in configured_fields:
                configured_key = normalize_header(config[config_field])
                if configured_key and configured_key in row and row.get(canonical_key) in (None, ''):
                    row[canonical_key] = row[configured_key]
            note_key = normalize_header(config.pos_note_name_key)
            if note_key and row.get(note_key) not in (None, ''):
                # When the configured note column contains the customer name,
                # make it the authoritative display name for this import row.
                row['name'] = row[note_key]
        return rows

    def _source_system_for_import(self, rows):
        if self.import_type == 'sales_product':
            return 'pos_excel'
        for row in rows:
            source = self._pick(row, 'source_system', 'ming_source_system')
            if source:
                return self._normalize_source_system(source)
        return 'pos_excel' if self.import_type == 'customer' else 'manual'

    def _json(self, value):
        return json.dumps(value, ensure_ascii=False, default=str, sort_keys=True)

    def _snapshot_partner(self, partner):
        return {
            'name': partner.name,
            'phone': partner.phone,
            'email': partner.email,
            'ming_pos_customer_code': partner.ming_pos_customer_code,
            'ming_kiotviet_customer_id': partner.ming_kiotviet_customer_id,
            'ming_branch_id': partner.ming_branch_id.id,
            'ming_total_spent': partner.ming_total_spent,
            'ming_loyalty_points': partner.ming_loyalty_points,
            'ming_last_transaction_date': partner.ming_last_transaction_date,
        }

    def _search_unique(self, model, domain, label, **error_flags):
        records = model.search(domain, limit=2)
        if len(records) > 1:
            raise MingImportRowError('Có nhiều khách trùng theo %s.' % label, duplicate=True, **error_flags)
        return records[:1]

    def _find_customer_match(self, source_system, external_id, code, phone_normalized, email):
        partner_model = self.env['res.partner'].sudo()
        mapping_model = self.env['ming.external.customer.map'].sudo()
        candidates = []
        mapping = mapping_model.browse()

        for field_name, value, label in (
            ('external_customer_id', external_id, 'ID khách ngoài hệ thống'),
            ('external_customer_code', code, 'mã khách ngoài hệ thống'),
        ):
            if not value:
                continue
            found_mapping = self._search_unique(
                mapping_model,
                [('source_system', '=', source_system), (field_name, '=', value)],
                label,
            )
            if found_mapping:
                mapping |= found_mapping
                candidates.append(found_mapping.partner_id)

        for field_name, value, label in (
            ('ming_kiotviet_customer_id', external_id, 'ID KiotViet'),
            ('ming_pos_customer_code', code, 'mã khách hàng'),
            ('ming_phone_normalized', phone_normalized, 'số điện thoại chuẩn hóa'),
            ('email', email, 'email'),
        ):
            if not value:
                continue
            found_partner = self._search_unique(partner_model, [(field_name, '=', value)], label)
            if found_partner:
                candidates.append(found_partner)

        unique_ids = {record.id for record in candidates if record}
        if len(unique_ids) > 1:
            raise MingImportRowError('Mã khách, ID ngoài hệ thống, SĐT hoặc email trỏ tới nhiều khách khác nhau.', duplicate=True)
        partner = candidates[0] if candidates else partner_model.browse()
        if mapping and partner and any(item.partner_id != partner for item in mapping):
            raise MingImportRowError('Bản đồ dữ liệu ngoài hệ thống trỏ sai khách hàng.', duplicate=True)
        return partner, mapping[:1]

    def _create_job_line(self, job, row_number, row, outcome=None, status='preview', error_message=False, **flags):
        outcome = outcome or {}
        self.env['ming.import.job.line'].sudo().create(
            {
                'job_id': job.id,
                'row_number': row_number,
                'operation': outcome.get('operation', 'error' if error_message else 'skip'),
                'status': status,
                'external_customer_id': outcome.get('external_customer_id'),
                'external_customer_code': outcome.get('external_customer_code'),
                'source_key': outcome.get('source_key'),
                'partner_id': outcome.get('partner_id'),
                'duplicate_found': flags.get('duplicate', outcome.get('duplicate', False)),
                'invalid_phone': flags.get('invalid_phone', outcome.get('invalid_phone', False)),
                'unmatched_branch': flags.get('unmatched_branch', outcome.get('unmatched_branch', False)),
                'raw_data': self._json(row),
                'old_values': self._json(outcome.get('old_values', {})),
                'new_values': self._json(outcome.get('new_values', {})),
                'error_message': error_message,
            }
        )

    def _has_prior_job_line(self, job, *, source_key=False, external_customer_id=False, external_customer_code=False):
        terms = []
        if source_key:
            terms.append(('source_key', '=', source_key))
        if external_customer_id:
            terms.append(('external_customer_id', '=', external_customer_id))
        if external_customer_code:
            terms.append(('external_customer_code', '=', external_customer_code))
        if not terms:
            return False
        domain = [('job_id', '=', job.id), ('status', '!=', 'failed')]
        if len(terms) > 1:
            domain.extend(['|'] * (len(terms) - 1))
        domain.extend(terms)
        return bool(self.env['ming.import.job.line'].sudo().search(domain, limit=1))

    def action_import(self):
        if not self.file_name.lower().endswith(('.csv', '.xlsx')):
            raise UserError(_('Chỉ hỗ trợ tệp .csv và .xlsx.'))
        rows = self._apply_configured_pos_mapping(self._read_rows())
        self._validate_headers(rows)
        source_system = self._source_system_for_import(rows)
        sync_log = self.env['ming.external.sync.log'].sudo().create(
            {
                'name': self.file_name,
                'source_system': source_system,
                'sync_type': 'manual_import',
                'file_name': self.file_name,
                'total_records': len(rows),
                'status': 'running',
            }
        )
        job = self.env['ming.import.job'].create(
            {
                'name': self.file_name,
                'import_type': self.import_type,
                'source_file_name': self.file_name,
                'branch_id': self.branch_id.id,
                'total_rows': len(rows),
                'dry_run': self.dry_run,
                'sync_log_id': sync_log.id,
                'status': 'draft',
            }
        )
        sync_log.import_job_id = job.id
        batch = self.env['ming.pos.import.batch'].create(
            {
                'name': self.file_name,
                'file_name': self.file_name,
                'uploaded_by': self.env.user.id,
                'branch_id': self.branch_id.id,
                'total_rows': len(rows),
                'dry_run': self.dry_run,
                'sync_log_id': sync_log.id,
                'state': 'processing',
            }
        )
        success = failed = duplicate = invalid_phone = unmatched_branch = 0
        created = updated = skipped = 0
        errors = []
        for row_number, row in enumerate(rows, start=2):
            try:
                with self.env.cr.savepoint():
                    if self.import_type == 'customer':
                        outcome = self._import_customer_row(row, job)
                    elif self.import_type == 'care_task':
                        outcome = self._import_care_task_row(row, job)
                    else:
                        outcome = self._import_sales_row(row, job)
                    operation = outcome.get('operation', 'skip')
                    status_map = {'create': 'created', 'update': 'updated', 'skip': 'skipped'}
                    self._create_job_line(job, row_number, row, outcome, status='preview' if self.dry_run else status_map.get(operation, 'skipped'))
                success += 1
                duplicate += int(outcome.get('duplicate', False))
                invalid_phone += int(outcome.get('invalid_phone', False))
                unmatched_branch += int(outcome.get('unmatched_branch', False))
                created += int(operation == 'create')
                updated += int(operation == 'update')
                skipped += int(operation == 'skip')
            except MingImportRowError as exc:
                failed += 1
                duplicate += int(exc.duplicate)
                invalid_phone += int(exc.invalid_phone)
                unmatched_branch += int(exc.unmatched_branch)
                message = 'Dòng %s: %s' % (row_number, exc)
                errors.append(message)
                self._create_job_line(
                    job,
                    row_number,
                    row,
                    status='failed',
                    error_message=str(exc),
                    duplicate=exc.duplicate,
                    invalid_phone=exc.invalid_phone,
                    unmatched_branch=exc.unmatched_branch,
                )
                self.env['ming.pos.import.error'].create(
                    {
                        'batch_id': batch.id,
                        'row_number': row_number,
                        'raw_data': self._json(row),
                        'error_message': str(exc),
                    }
                )
            except Exception as exc:
                failed += 1
                message = 'Dòng %s: %s' % (row_number, exc)
                errors.append(message)
                self._create_job_line(job, row_number, row, status='failed', error_message=str(exc))
                self.env['ming.pos.import.error'].create(
                    {
                        'batch_id': batch.id,
                        'row_number': row_number,
                        'raw_data': self._json(row),
                        'error_message': str(exc),
                    }
                )

        job_status = 'dry_run' if self.dry_run and not failed else 'partial' if failed and success else 'failed' if failed else 'done'
        batch_state = 'dry_run' if self.dry_run and not failed else 'partial' if failed and success else 'failed' if failed else 'done'
        job.write(
            {
                'success_rows': success,
                'failed_rows': failed,
                'duplicate_rows': duplicate,
                'invalid_phone_rows': invalid_phone,
                'unmatched_branch_rows': unmatched_branch,
                'status': job_status,
                'note': '\n'.join(errors[:100]),
            }
        )
        batch.write(
            {
                'success_rows': success,
                'failed_rows': failed,
                'duplicate_rows': duplicate,
                'invalid_phone_rows': invalid_phone,
                'unmatched_branch_rows': unmatched_branch,
                'state': batch_state,
                'finished_at': fields.Datetime.now(),
                'error_summary': '\n'.join(errors[:50]),
            }
        )
        sync_log.write(
            {
                'created_count': created,
                'updated_count': updated,
                'skipped_count': skipped,
                'failed_count': failed,
                'duplicate_count': duplicate,
                'invalid_phone_count': invalid_phone,
                'unmatched_branch_count': unmatched_branch,
                'status': 'dry_run' if self.dry_run and not failed else 'partial' if failed and success else 'failed' if failed else 'done',
                'finished_at': fields.Datetime.now(),
                'error_message': '\n'.join(errors[:50]),
            }
        )
        self.result = 'Dòng qua kiểm tra: %s | Lỗi: %s | Trùng: %s | SĐT sai: %s | Chi nhánh không khớp: %s\n%s' % (
            success,
            failed,
            duplicate,
            invalid_phone,
            unmatched_branch,
            '\n'.join(errors[:50]),
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _import_customer_row(self, row, job):
        code = str(self._pick(row, 'ming_pos_customer_code', 'customer_code', 'external_customer_code', 'customer_id', 'id', 'ma_kh', 'ma_khach', 'ma_khach_hang') or '').strip() or False
        external_id = str(self._pick(row, 'ming_kiotviet_customer_id', 'kiotviet_customer_id', 'external_customer_id') or '').strip() or False
        raw_phone = str(self._pick(row, 'phone', 'mobile', 'sdt', 'dien_thoai', 'so_dien_thoai') or '').strip() or False
        email = str(self._pick(row, 'email') or '').strip().lower() or False
        source_note = str(self._pick(row, 'ming_customer_note', 'customer_note', 'ghi_chu', 'note') or '').strip()
        name = str(self._pick(row, 'name', 'ten_kh', 'ten_khach', 'ten_khach_hang', 'customer_name') or '').strip() or source_note
        name_from_note = bool(source_note and name == source_note)
        if not name:
            raise MingImportRowError('Thiếu tên khách hàng.')
        if not any((code, external_id, raw_phone, email)):
            raise MingImportRowError('Thiếu mã khách, ID ngoài hệ thống, SĐT hoặc email để đối chiếu.')

        partner_model = self.env['res.partner'].sudo()
        phone_local = phone_normalized = False
        phone_valid = True
        if raw_phone:
            phone_local, phone_normalized, phone_valid = partner_model._normalize_vn_phone(raw_phone)
        invalid_phone = self._to_bool(self._pick(row, 'invalid_phone'), default=False) or (bool(raw_phone) and not phone_valid)
        branch = self._resolve_branch(row)
        if not branch:
            raise MingImportRowError('Chi nhánh không tồn tại hoặc chưa được khai báo.', invalid_phone=invalid_phone, unmatched_branch=True)
        if email and not tools.single_email_re.match(email):
            raise MingImportRowError('Email không hợp lệ: %s' % email, invalid_phone=invalid_phone)
        last_transaction_date = self._date_value(
            self._pick(row, 'last_transaction_date', 'last transaction', 'ming_last_transaction_date', 'ngay_giao_dich_cuoi'),
            'Ngày giao dịch cuối',
        )
        purchase_total = False
        if self._has_value(row, 'ming_total_spent', 'total_spent', 'total spend', 'tong_chi_tieu', 'tong_ban_tru_tra_hang', 'tong_ban'):
            purchase_total = self._to_float(
                self._pick(row, 'ming_total_spent', 'total_spent', 'total spend', 'tong_chi_tieu', 'tong_ban_tru_tra_hang', 'tong_ban')
            )
        purchase_points = False
        if self._has_value(row, 'ming_loyalty_points', 'loyalty_points', 'points', 'diem_tich_luy', 'diem_hien_tai', 'tong_diem'):
            purchase_points = self._to_int(
                self._pick(row, 'ming_loyalty_points', 'loyalty_points', 'points', 'diem_tich_luy', 'diem_hien_tai', 'tong_diem')
            )
        source_system = self._normalize_source_system(self._pick(row, 'source_system', 'ming_source_system'))
        partner, mapping = self._find_customer_match(source_system, external_id, code, phone_normalized, email)
        duplicate = bool(partner)
        source_key = stable_source_key(
            {
                'source_system': source_system,
                'external_customer_id': external_id,
                'external_customer_code': code,
                'phone': phone_normalized,
                'email': email,
                'transaction_date': last_transaction_date,
                'total_spent': purchase_total,
                'loyalty_points': purchase_points,
            }
        )
        if self.dry_run and self._has_prior_job_line(
            job,
            source_key=source_key,
            external_customer_id=external_id,
            external_customer_code=code,
        ):
            return {
                'operation': 'skip',
                'duplicate': True,
                'source_key': source_key,
                'external_customer_id': external_id,
                'external_customer_code': code,
            }
        if partner and self.env['ming.purchase.history'].sudo().search_count([('source_key', '=', source_key)]):
            return {
                'operation': 'skip',
                'duplicate': True,
                'source_key': source_key,
                'external_customer_id': external_id,
                'external_customer_code': code,
            }
        vals = {
            'ming_last_import_job_id': job.id,
            'ming_last_sync_at': fields.Datetime.now(),
            'ming_last_sync_log_id': job.sync_log_id.id,
            'ming_external_payload_hash': stable_source_key(row),
        }
        if not partner:
            vals.update(
                {
                    'name': name,
                    'ming_source_system': source_system,
                    'ming_branch_id': branch.id,
                }
            )
            if source_note:
                # Keep the source note visible in the CSKH profile for new customers.
                vals['ming_customer_note'] = source_note
            if code:
                vals['ming_pos_customer_code'] = code
            if external_id:
                vals['ming_kiotviet_customer_id'] = external_id
            if raw_phone:
                vals.update(
                    {
                        'phone': phone_local or raw_phone,
                        'ming_phone_normalized': phone_normalized or False,
                        'ming_invalid_phone': invalid_phone,
                    }
                )
            else:
                vals['ming_invalid_phone'] = False
            if email:
                vals.update({'email': email, 'ming_invalid_email': False})
            for field_name, aliases in (
                ('ming_allow_sms', ('allow_sms',)),
                ('ming_allow_email', ('allow_email',)),
                ('ming_do_not_contact', ('do_not_contact',)),
                ('ming_is_vip', ('is_vip',)),
            ):
                if self._has_value(row, *aliases):
                    vals[field_name] = self._to_bool(self._pick(row, *aliases))
        else:
            # A configured note-name column is authoritative for POS display names.
            # Other incoming names remain protected unless contact updates are enabled.
            if name and (
                name_from_note
                or not partner.name
                or self.allow_contact_updates
            ):
                vals['name'] = name
            if code and not partner.ming_pos_customer_code:
                vals['ming_pos_customer_code'] = code
            if external_id and not partner.ming_kiotviet_customer_id:
                vals['ming_kiotviet_customer_id'] = external_id
            if raw_phone and (not partner.phone or self.allow_contact_updates):
                vals.update(
                    {
                        'phone': phone_local or raw_phone,
                        'ming_phone_normalized': phone_normalized or False,
                        'ming_invalid_phone': invalid_phone,
                    }
                )
            if email and (not partner.email or self.allow_contact_updates):
                vals.update({'email': email, 'ming_invalid_email': False})
            if not partner.ming_branch_id:
                vals['ming_branch_id'] = branch.id

        incoming_date = fields.Date.to_date(last_transaction_date) if last_transaction_date else False
        previous_date = partner.ming_last_transaction_date if partner else False
        purchase_is_latest = not partner or not previous_date or bool(incoming_date and incoming_date >= previous_date)
        if purchase_total is not False and purchase_is_latest:
            vals['ming_total_spent'] = purchase_total
        if purchase_points is not False and purchase_is_latest:
            vals['ming_loyalty_points'] = purchase_points
        if last_transaction_date and purchase_is_latest:
            vals['ming_last_transaction_date'] = last_transaction_date
        if partner and incoming_date and previous_date and incoming_date > previous_date:
            if partner.ming_activity_status in ('at_risk', 'lost') or partner.ming_alert_level != '0':
                vals.update(
                    {
                        'ming_has_returned': True,
                        'ming_returned_at': incoming_date,
                    }
                )

        old_values = self._snapshot_partner(partner) if partner else {}
        if self.dry_run:
            partner_id = partner.id if partner else False
            operation = 'update' if partner else 'create'
        elif partner:
            partner.write(vals)
            partner_id = partner.id
            operation = 'update'
        else:
            partner = partner_model.create(vals)
            partner_id = partner.id
            operation = 'create'

        if not self.dry_run:
            history_model = self.env['ming.purchase.history'].sudo()
            if purchase_is_latest:
                history_model.search(
                    [('partner_id', '=', partner.id), ('is_latest', '=', True)]
                ).write({'is_latest': False})
            history_model.create(
                {
                    'partner_id': partner.id,
                    'source_system': source_system,
                    'source_file_name': self.file_name,
                    'source_key': source_key,
                    'external_customer_id': external_id,
                    'external_customer_code': code,
                    'transaction_date': incoming_date,
                    'total_spent': purchase_total if purchase_total is not False else partner.ming_total_spent,
                    'loyalty_points': purchase_points if purchase_points is not False else partner.ming_loyalty_points,
                    'is_latest': purchase_is_latest,
                    'import_job_id': job.id,
                    'sync_log_id': job.sync_log_id.id,
                    'raw_data': self._json(row),
                }
            )

        if not self.dry_run and (external_id or code):
            map_vals = {
                'source_system': source_system,
                'external_customer_id': external_id,
                'external_customer_code': code,
                'partner_id': partner.id,
                'last_synced_at': fields.Datetime.now(),
                'raw_payload_hash': stable_source_key(row),
                'raw_payload': self._json(row),
            }
            if mapping:
                mapping.write(map_vals)
            else:
                self.env['ming.external.customer.map'].sudo().create(map_vals)
        return {
            'operation': operation,
            'partner_id': partner_id,
            'duplicate': duplicate,
            'invalid_phone': invalid_phone,
            'source_key': source_key,
            'external_customer_id': external_id,
            'external_customer_code': code,
            'old_values': old_values,
            'new_values': vals,
        }

    def _import_sales_row(self, row, job):
        period_start = self._date_value(self._pick(row, 'period_start', 'from_date', 'tu_ngay'), 'Từ ngày')
        period_end = self._date_value(self._pick(row, 'period_end', 'to_date', 'den_ngay'), 'Đến ngày')
        branch = self._resolve_branch(row)
        if not branch:
            raise MingImportRowError('Chi nhánh không tồn tại hoặc chưa được khai báo.', unmatched_branch=True)
        source_file = self._pick(row, 'source_file', 'file_name')
        product_code = self._pick(row, 'product_code', 'ma_san_pham')
        product_name = self._pick(row, 'product_name', 'ten_san_pham')
        source_key = stable_source_key(
            {
                'source_file': source_file,
                'sheet': row.get('sheet'),
                'period_start': period_start,
                'period_end': period_end,
                'branch': row.get('branch') or row.get('branch_name') or row.get('branch_code'),
                'product_code': product_code,
                'product_name': product_name,
            }
        )
        line_model = self.env['ming.sales.product.line'].sudo()
        existing = line_model.search([('source_key', '=', source_key)], limit=2)
        if len(existing) > 1:
            raise MingImportRowError('Có nhiều dòng bán hàng trùng khóa nguồn.', duplicate=True)
        existing = existing[:1]
        if self.dry_run and self._has_prior_job_line(job, source_key=source_key):
            return {'operation': 'skip', 'duplicate': True, 'source_key': source_key}
        vals = {
            'source_file': source_file,
            'source_key': source_key,
            'source_system': self._normalize_source_system(row.get('source_system') or 'pos_excel'),
            'import_job_id': job.id,
            'sheet': row.get('sheet'),
            'period_start': period_start,
            'period_end': period_end,
            'branch_name': row.get('branch') or row.get('branch_name'),
            'branch_id': branch.id,
            'product_code': product_code,
            'product_name': product_name,
            'qty_sold': self._to_float(row.get('qty_sold')),
            'gross_revenue': self._to_float(row.get('gross_revenue')),
            'qty_return': self._to_float(row.get('qty_return')),
            'return_value': self._to_float(row.get('return_value')),
            'net_revenue': self._to_float(row.get('net_revenue')),
        }
        operation = 'update' if existing else 'create'
        if not self.dry_run:
            if existing:
                existing.write(vals)
            else:
                line_model.create(vals)
        return {'operation': operation, 'duplicate': bool(existing), 'source_key': source_key, 'new_values': vals}

    def _import_care_task_row(self, row, job):
        partner_model = self.env['res.partner'].sudo()
        customer_code = self._pick(row, 'customer_id', 'ming_pos_customer_code', 'customer_code', 'ma_kh')
        phone = self._pick(row, 'phone', 'sdt')
        email = str(self._pick(row, 'email') or '').strip().lower() or False
        partner = partner_model.browse()
        if customer_code:
            partner = self._search_unique(partner_model, [('ming_pos_customer_code', '=', customer_code)], 'mã khách hàng')
        if not partner and phone:
            _, normalized_phone, _ = partner_model._normalize_vn_phone(phone)
            if normalized_phone:
                partner = self._search_unique(partner_model, [('ming_phone_normalized', '=', normalized_phone)], 'số điện thoại')
            if not partner:
                partner = self._search_unique(partner_model, [('phone', '=', phone)], 'số điện thoại')
        if not partner and email:
            partner = self._search_unique(partner_model, [('email', '=', email)], 'email')
        if not partner:
            name = self._pick(row, 'customer_name', 'name')
            if name:
                partner = self._search_unique(partner_model, [('name', '=', name)], 'tên khách hàng')
        if not partner:
            raise MingImportRowError(_('Không tìm thấy khách hàng cho dòng task CSKH.'))
        due_date = self._date_value(self._pick(row, 'due_date', 'ngay_can_goi'), 'Ngày cần gọi')
        row_branch = self._resolve_branch(row) if self._has_value(row, 'branch', 'branch_name', 'branch_code', 'chi_nhanh', 'ma_chi_nhanh') else partner.ming_branch_id
        if not row_branch or row_branch != partner.ming_branch_id:
            raise MingImportRowError('Chi nhánh của task không khớp với khách hàng.', unmatched_branch=True)
        priority_map = {'low': '0', 'normal': '1', 'high': '2', 'urgent': '3'}
        alert_level = self._pick(row, 'alert_level') or False
        if alert_level == '0':
            alert_level = False
        source_key = stable_source_key(
            {
                'task_id': row.get('task_id'),
                'customer_id': customer_code or partner.ming_pos_customer_code,
                'due_date': due_date,
                'task_type': self._pick(row, 'task_type', 'reason') or 'manual',
                'task_name': self._pick(row, 'task_name', 'name'),
            }
        )
        task_model = self.env['ming.care.task'].sudo()
        existing = task_model.search([('source_key', '=', source_key)], limit=2)
        if len(existing) > 1:
            raise MingImportRowError('Có nhiều task trùng khóa nguồn.', duplicate=True)
        existing = existing[:1]
        if self.dry_run and self._has_prior_job_line(job, source_key=source_key):
            return {'operation': 'skip', 'duplicate': True, 'partner_id': partner.id, 'source_key': source_key}
        vals = {
            'name': self._pick(row, 'task_name', 'name') or _('Công việc CSKH'),
            'partner_id': partner.id,
            'task_type': self._pick(row, 'task_type', 'reason') or 'manual',
            'priority': priority_map.get((self._pick(row, 'priority') or 'normal').strip().lower(), '1'),
            'due_date': due_date,
            'pipeline_status': self._pick(row, 'pipeline_status', 'state') or 'pending',
            'days_absent': self._to_int(self._pick(row, 'days_absent')),
            'alert_level': alert_level,
            'is_vip': self._to_bool(self._pick(row, 'is_vip'), default=partner.ming_is_vip),
            'total_spent': self._to_float(self._pick(row, 'total_spent'), default=partner.ming_total_spent),
            'source_key': source_key,
            'import_job_id': job.id,
        }
        if self.dry_run:
            operation = 'skip' if existing else 'create'
        elif existing:
            operation = 'skip'
        else:
            task_model.create(vals)
            operation = 'create'
        return {'operation': operation, 'duplicate': bool(existing), 'partner_id': partner.id, 'source_key': source_key, 'new_values': vals}
