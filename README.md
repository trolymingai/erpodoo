# Ming Coffee ERP (Odoo 19.0)

Hệ thống Quản trị Doanh nghiệp & Vận hành Chuỗi Cà phê Ming Coffee (Ming A3, Ming PR, The Goo Cafe - LD, The Goo Cafe - A2).
Truy cập: https://erp.mingcoffeemore.com/

## Cấu trúc Dự án
- `docker-compose.yml`: Cấu hình Docker cho Odoo 19.0 và PostgreSQL 16 Alpine.
- `odoo.conf`: Cấu hình hệ thống Odoo, addons_path, bộ nhớ và database mapping.
- `addons/`: Các module tùy biến (Custom Addons) độc quyền:
  - `ming_brand_theme`: Giao diện và nhận diện thương hiệu Ming Coffee.
  - `ming_customer_care`: Module CSKH, quản lý nhiệm vụ, checklist mở/đóng ca và tích hợp Ming AI.

## Vận hành & Cập nhật
```bash
# Khởi động dịch vụ
docker compose up -d

# Xem log Odoo
docker logs -f --tail 50 mingcrm-odoo
```
