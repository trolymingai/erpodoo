# Bộ Tài Liệu Bàn Giao Ming Customer Care

## 1. Mục lục tổng quan

### Ming Customer Care là gì

Ming Customer Care là hệ thống chăm sóc khách hàng được xây trên Odoo để hỗ trợ team:

- theo dõi khách hàng cần chăm sóc
- gọi lại khách có nguy cơ rời bỏ
- theo dõi khách VIP
- ghi nhận lịch sử chăm sóc
- kiểm tra log SMS, email, Lark ở chế độ an toàn

### Trạng thái môi trường hiện tại

Hiện tại hệ thống đang ở trạng thái phục vụ training và UAT:

- đang dùng dữ liệu `demo/UAT`
- `safe mode` đang `ON`
- chưa bật gửi `SMS` thật
- chưa bật gửi `email` thật
- chưa bật gửi `Lark` thật
- chưa import dữ liệu khách hàng thật

Tài liệu này dùng để bàn giao cho quản lý và team vận hành trước khi đi tiếp sang dữ liệu thật.

## 2. Thứ tự đọc tài liệu theo vai trò

### Cho Nhân viên CSKH

Nhân viên CSKH nên đọc theo thứ tự:

1. [QUICK_START_1_PAGE.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/QUICK_START_1_PAGE.md)
2. [HUONG_DAN_NHAN_VIEN_CSKH.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/HUONG_DAN_NHAN_VIEN_CSKH.md)
3. [SOP_CSKH_HANG_NGAY.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/SOP_CSKH_HANG_NGAY.md)

### Cho Quản lý chi nhánh

Quản lý chi nhánh nên đọc theo thứ tự:

1. [QUICK_START_1_PAGE.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/QUICK_START_1_PAGE.md)
2. [HUONG_DAN_QUAN_LY_CHI_NHANH.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/HUONG_DAN_QUAN_LY_CHI_NHANH.md)
3. [SOP_QUAN_LY_CHI_NHANH.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/SOP_QUAN_LY_CHI_NHANH.md)
4. [TRAINING_CHECKLIST.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/TRAINING_CHECKLIST.md)

### Cho Admin hoặc Founder

Admin hoặc Founder nên:

- đọc toàn bộ bộ tài liệu
- đọc kỹ [HUONG_DAN_ADMIN_FOUNDER.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/HUONG_DAN_ADMIN_FOUNDER.md)
- đọc kỹ [TRAINING_CHECKLIST.md](C:/Users/Frank Nguyen/Documents/Odoo Minghouse/odoo/addons/ming_customer_care/docs/TRAINING_CHECKLIST.md)
- kiểm tra lại:
  - `safe mode`
  - phân quyền user
  - dữ liệu `demo/UAT`

## 3. Quy trình training đề xuất

### Buổi 1. Admin hoặc Founder xem Dashboard tổng

Mục tiêu:

- hiểu tổng quan hệ thống
- biết các màn chính
- biết trạng thái hiện tại đang là training/UAT

### Buổi 2. Quản lý chi nhánh xem dashboard chi nhánh

Mục tiêu:

- biết xem task của chi nhánh
- biết xem task quá hạn
- biết xem khách VIP có nguy cơ

### Buổi 3. Nhân viên CSKH xử lý task demo

Mục tiêu:

- mở `Cần gọi hôm nay`
- nhận task
- ghi nhận kết quả gọi
- hoàn tất task

### Buổi 4. Test hẹn gọi lại và lịch sử CSKH

Mục tiêu:

- hẹn gọi lại đúng cách
- kiểm tra task follow-up được tạo
- xem lại lịch sử CSKH

### Buổi 5. Tổng kết lỗi và chốt quy trình

Mục tiêu:

- ghi nhận các lỗi khi training
- thống nhất cách ghi chú
- thống nhất cách chọn trạng thái chăm sóc
- chốt quy trình trước khi dùng dữ liệu thật

## 4. Checklist trước khi cho team dùng demo

- [ ] App `Ming Customer Care` đã xuất hiện
- [ ] Dashboard mở được
- [ ] Có dữ liệu `demo/UAT`
- [ ] User CSKH đăng nhập được
- [ ] User Manager đăng nhập được
- [ ] User Admin đăng nhập được
- [ ] `Safe mode` vẫn `ON`
- [ ] SMS, email, Lark chưa gửi thật

## 5. Checklist trước khi import dữ liệu thật

- [ ] Có file khách hàng đúng schema
- [ ] Có mã khách hàng
- [ ] Có tên khách
- [ ] Có số điện thoại
- [ ] Có chi nhánh
- [ ] Có tổng chi tiêu
- [ ] Có điểm tích lũy nếu có
- [ ] Có ngày giao dịch cuối
- [ ] Đã backup database và filestore
- [ ] Đã dọn dữ liệu `demo/UAT` hoặc đánh dấu rõ nguồn
- [ ] Đã chạy `dry-run`
- [ ] Đã báo rõ số dòng lỗi
- [ ] Đã báo rõ số dòng trùng
- [ ] Đã báo rõ số điện thoại sai
- [ ] Đã báo rõ số chi nhánh không match
- [ ] Chỉ import thật khi Admin duyệt

## 6. Quy tắc an toàn production

- không tắt `safe mode` nếu chưa được duyệt
- không bật SMS thật khi chưa UAT với dữ liệu thật
- không bật email thật khi template chưa duyệt
- không bật Lark thật khi webhook chưa test
- không import báo cáo bán hàng như dữ liệu khách hàng
- không xử lý khách thật trên dữ liệu demo

## 7. Bảng trạng thái hiện tại

Trạng thái hiện tại của hệ thống:

- Module đã cài live: `Đã xong`
- Demo/UAT pass: `Đã xong`
- Training docs đã có: `Đã xong`
- Safe mode: `ON`
- Dữ liệu thật: `Chưa có`
- SMS thật: `Chưa bật`
- Email thật: `Chưa bật`
- Lark thật: `Chưa bật`

## 8. Việc còn lại để go-live thật

Các bước còn lại trước khi chạy thật:

1. lấy file khách hàng thật từ POS hoặc KiotViet
2. chạy `dry-run`
3. import dữ liệu thật
4. chạy phân loại ngoài giờ
5. UAT lại với dữ liệu thật
6. bật Lark trước
7. bật email sau
8. bật SMS cuối cùng

## 9. Gợi ý sử dụng bộ tài liệu bàn giao

Người quản lý có thể dùng file này như tài liệu trung tâm:

- mở tài liệu này trước
- chọn đúng nhóm người dùng
- gửi đúng tài liệu theo vai trò
- dùng checklist để xác nhận team đã hoàn thành training
- chỉ chuyển sang dữ liệu thật sau khi tất cả phần training/UAT đã đạt
