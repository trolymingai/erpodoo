"""Pure helpers shared by import and future external-sync adapters."""

from datetime import date, datetime
import hashlib
import json
import unicodedata


CUSTOMER_REQUIRED_HEADERS = (
    ('customer_name', {'name', 'ten_kh', 'ten_khach', 'ten_khach_hang', 'customer_name', 'ghi_chu', 'note'}),
    ('customer_identity', {'id', 'customer_code', 'customer_id', 'ming_pos_customer_code', 'ma_kh', 'ma_khach', 'ma_khach_hang', 'phone', 'sdt', 'mobile', 'dien_thoai', 'so_dien_thoai', 'email'}),
    ('branch', {'branch', 'branch_name', 'branch_code', 'chi_nhanh', 'ma_chi_nhanh', 'ten_chi_nhanh'}),
)


def normalize_identity(value):
    """Return a stable, case-insensitive identity value or ``None``."""
    if value is None:
        return None
    normalized = unicodedata.normalize('NFKC', str(value)).strip().casefold()
    return normalized or None


def normalize_header(value):
    if value is None:
        return None
    normalized = unicodedata.normalize('NFKD', str(value)).strip().casefold()
    normalized = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.replace('đ', 'd')
    if not normalized:
        return None
    return '_'.join(normalized.replace('-', '_').split())


def normalize_row_keys(row):
    """Normalize CSV/XLSX headers while preserving the first non-empty value."""
    normalized_row = {}
    for key, value in row.items():
        normalized_key = normalize_header(key) or str(key)
        if normalized_key not in normalized_row or normalized_row[normalized_key] in (None, ''):
            normalized_row[normalized_key] = value
    return normalized_row


def stable_source_key(values):
    """Build an idempotency key from a normalized mapping of source values."""
    normalized = {
        str(key): normalize_identity(value) or ''
        for key, value in values.items()
    }
    payload = json.dumps(normalized, ensure_ascii=True, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def missing_required_headers(headers, requirements):
    """Return logical requirements whose alias group is absent from headers."""
    normalized_headers = {normalize_header(header) for header in headers if normalize_header(header)}
    missing = []
    for label, aliases in requirements:
        normalized_aliases = {normalize_header(alias) for alias in aliases}
        if not normalized_headers.intersection(normalized_aliases):
            missing.append(label)
    return missing


def parse_import_date(value):
    """Parse only unambiguous ISO dates used by the import contract."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or '').strip()
    if not text:
        raise ValueError('Ngày không được để trống')
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        if 'T' in text or ' ' in text:
            try:
                return datetime.fromisoformat(text.replace(' ', 'T')).date()
            except ValueError:
                pass
        raise ValueError('Ngày phải theo định dạng YYYY-MM-DD') from exc
