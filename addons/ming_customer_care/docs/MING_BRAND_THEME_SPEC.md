# Ming Brand Theme Spec

## Muc tieu
Tao module rieng `ming_brand_theme` de chuan hoa login page, backend accent, va polish dashboard cho Ming Customer Care tren Odoo live theo phong cach sach - doanh nghiep.

## Nguyen tac
- Khong sua core Odoo, web, crm, contacts.
- Khong doi logic CSKH, dashboard KPI, record rule, safe_mode.
- Co the rollback bang uninstall/disable module `ming_brand_theme`.

## Thuong hieu
- Primary: `#fd9830`
- Background chinh: `#ffffff`
- Background phu: `#fff7ef` / `#fff4e8`
- Border: `#f3dcc8`
- Text chinh: `#1f1f1f`
- Text phu: `#6b6b6b`

## Pham vi
1. Login page branding qua inherit template `web.login_layout` / `web.login` va frontend assets.
2. Backend accent nhe qua `web.assets_backend`.
3. Dashboard Ming Customer Care duoc polish bang CSS va inherit view rat nhe de them logo nho neu can.
4. CRM goc tiep tuc an voi Staff/Manager; Admin van thay.

## Module de xuat
- `ming_brand_theme/__manifest__.py`
- `ming_brand_theme/README.md`
- `ming_brand_theme/views/login_templates.xml`
- `ming_brand_theme/views/webclient_templates.xml`
- `ming_brand_theme/static/src/img/ming_logo.png`
- `ming_brand_theme/static/src/scss/ming_brand.scss`
- `ming_brand_theme/static/src/css/ming_login.css`

## Login page
- Bo cuc 2 cot tren desktop, xep doc tren mobile.
- Ben trai: panel thuong hieu cam Ming, logo lon, title, subtitle.
- Ben phai: card form trang sach, giu nguyen noi dung form Odoo.
- Nut dang nhap dung mau `#fd9830`.
- Footer: `© Ming Coffee & More - Internal System`.

## Backend
- Accent cho button chinh, active menu, active tab, dashboard card border/highlight.
- Khong phu cam toan bo backend.

## Dashboard
- Tieu de: `Bang dieu hanh CSKH Ming`.
- Subtitle: `Tong quan cham soc khach hang hom nay`.
- Logo nho o header.
- KPI dang card layout ro rang, giu quick actions va notebook hien co.

## Test
- `/web/login` hien logo va mau cam dung.
- Admin/Manager/Staff login duoc.
- Staff vao `Can goi hom nay`; Manager/Admin vao dashboard.
- Quick buttons mo dung man.
- Role scope va safe_mode van pass.
