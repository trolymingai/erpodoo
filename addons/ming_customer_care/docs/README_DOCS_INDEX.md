# README - Bộ tài liệu vận hành Ming Customer Care

## Trạng thái hiện tại

- Module đã cài live trên Odoo
- Demo/UAT data đã dùng để training
- Safe mode đang ON
- Chưa import dữ liệu khách hàng thật
- Chưa bật SMS/email/Lark thật

## Danh sách tài liệu và mục đích từng file

- [BO_TAI_LIEU_BAN_GIAO_MING_CUSTOMER_CARE.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/BO_TAI_LIEU_BAN_GIAO_MING_CUSTOMER_CARE.md)  
  → Tài liệu tổng hợp bàn giao, mục lục lớn và quy trình triển khai.

- [QUICK_START_1_PAGE.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/QUICK_START_1_PAGE.md)  
  → Bản 1 trang để training nhanh cho nhân viên/quản lý.

- [HUONG_DAN_NHAN_VIEN_CSKH.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/HUONG_DAN_NHAN_VIEN_CSKH.md)  
  → Hướng dẫn chi tiết cho nhân viên CSKH.

- [SOP_CSKH_HANG_NGAY.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/SOP_CSKH_HANG_NGAY.md)  
  → Quy trình làm việc hằng ngày của nhân viên CSKH.

- [HUONG_DAN_QUAN_LY_CHI_NHANH.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/HUONG_DAN_QUAN_LY_CHI_NHANH.md)  
  → Hướng dẫn cho quản lý chi nhánh.

- [SOP_QUAN_LY_CHI_NHANH.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/SOP_QUAN_LY_CHI_NHANH.md)  
  → Quy trình quản lý kiểm tra công việc hằng ngày/cuối ngày.

- [HUONG_DAN_ADMIN_FOUNDER.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/HUONG_DAN_ADMIN_FOUNDER.md)  
  → Hướng dẫn cho Admin/Founder về cấu hình, phân quyền, kiểm tra hệ thống.

- [TRAINING_CHECKLIST.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/TRAINING_CHECKLIST.md)  
  → Checklist buổi training và nghiệm thu nội bộ.

## Thứ tự đọc đề xuất

### Nhân viên CSKH

1. [QUICK_START_1_PAGE.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/QUICK_START_1_PAGE.md)
2. [HUONG_DAN_NHAN_VIEN_CSKH.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/HUONG_DAN_NHAN_VIEN_CSKH.md)
3. [SOP_CSKH_HANG_NGAY.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/SOP_CSKH_HANG_NGAY.md)

### Quản lý chi nhánh

1. [QUICK_START_1_PAGE.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/QUICK_START_1_PAGE.md)
2. [HUONG_DAN_QUAN_LY_CHI_NHANH.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/HUONG_DAN_QUAN_LY_CHI_NHANH.md)
3. [SOP_QUAN_LY_CHI_NHANH.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/SOP_QUAN_LY_CHI_NHANH.md)
4. [TRAINING_CHECKLIST.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/TRAINING_CHECKLIST.md)

### Admin/Founder

1. [BO_TAI_LIEU_BAN_GIAO_MING_CUSTOMER_CARE.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/BO_TAI_LIEU_BAN_GIAO_MING_CUSTOMER_CARE.md)
2. [HUONG_DAN_ADMIN_FOUNDER.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/HUONG_DAN_ADMIN_FOUNDER.md)
3. [TRAINING_CHECKLIST.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/TRAINING_CHECKLIST.md)
4. Toàn bộ SOP nếu cần đào tạo team

## Cảnh báo an toàn

- Không tắt safe mode nếu chưa được duyệt.
- Không bật SMS/email/Lark thật trong giai đoạn demo.
- Không import dữ liệu khách hàng thật nếu chưa chạy dry-run.
- Không dùng dữ liệu demo để gọi khách thật.
- Không xóa dữ liệu nếu chưa backup.

## Việc còn lại để go-live thật

- [ ] Lấy file khách hàng thật từ POS/KiotViet.
- [ ] Chạy dry-run.
- [ ] Kiểm tra lỗi, dòng trùng, số điện thoại sai, chi nhánh không match.
- [ ] Backup trước import.
- [ ] Import thật.
- [ ] Chạy phân loại ngoài giờ.
- [ ] UAT với dữ liệu thật.
- [ ] Bật Lark trước, email sau, SMS cuối cùng.
