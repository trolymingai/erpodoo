# SOP Quản Lý Chi Nhánh

## 1. Mục đích

Tài liệu này hướng dẫn quản lý chi nhánh cách theo dõi và điều hành Ming Customer Care mỗi ngày để:

- kiểm soát task chăm sóc khách hàng
- phát hiện khách VIP có nguy cơ
- theo dõi chất lượng xử lý của nhân viên
- kiểm tra tỷ lệ hoàn tất task cuối ngày

## 2. Quy trình đầu ngày

### Bước 1. Xem dashboard chi nhánh mỗi sáng

1. Đăng nhập Odoo bằng tài khoản quản lý.
2. Vào `Ming Customer Care`.
3. Mở `Bảng điều hành`.
4. Kiểm tra nhanh:
   - tổng khách của chi nhánh
   - khách có nguy cơ
   - khách đã mất
   - khách VIP
   - task cần gọi hôm nay
   - task quá hạn
   - cảnh báo lần 1 / 2 / 3

### Bước 2. Kiểm tra task cần gọi hôm nay

1. Vào `Cần gọi hôm nay`.
2. Xem nhân viên đã có đủ task để xử lý chưa.
3. Xác định nhóm khách cần ưu tiên trong ngày.

### Bước 3. Kiểm tra task quá hạn

1. Vào `Task quá hạn`.
2. Xem task nào đang tồn.
3. Xác định nguyên nhân:
   - nhân viên chưa nhận
   - nhân viên đã nhận nhưng chưa xử lý
   - task phát sinh quá nhiều
4. Yêu cầu xử lý dứt điểm các task quá hạn trước.

## 3. Theo dõi khách quan trọng

### Bước 4. Kiểm tra khách VIP có nguy cơ

1. Vào `Khách VIP có nguy cơ`.
2. Xem:
   - ai là khách quan trọng chưa quay lại
   - khách đang ở mức cảnh báo nào
   - khách nào cần quản lý can thiệp

### Bước 5. Kiểm tra nhân viên nào chưa xử lý

1. Trong màn task, dùng `Group By` theo `Nhân viên phụ trách`.
2. Xem:
   - ai chưa nhận task
   - ai để tồn quá nhiều task
   - ai xử lý chậm

## 4. Theo dõi chất lượng chăm sóc

### Bước 6. Xem lý do khách rời bỏ

1. Vào `Lịch sử CSKH`.
2. Lọc các trường hợp:
   - phản hồi tiêu cực
   - khách không còn nhu cầu
   - khách chuyển sang quán khác
3. Ghi nhận xu hướng chung của chi nhánh.

### Bước 7. Theo dõi lịch sử CSKH

1. Xem lịch sử theo từng nhân viên.
2. Kiểm tra ghi chú có rõ ràng không.
3. Kiểm tra các trường hợp hẹn gọi lại có được theo dõi tiếp không.

### Bước 8. Khi có phản hồi tiêu cực

Khi gặp phản hồi tiêu cực:

1. Mở task hoặc lịch sử liên quan.
2. Xác nhận nguyên nhân.
3. Quản lý trực tiếp xử lý nếu cần.
4. Ghi nhận rõ hướng xử lý của quản lý.
5. Theo dõi lại kết quả sau đó.

## 5. Kiểm tra cuối ngày

### Bước 9. Kiểm tra tỷ lệ hoàn tất task

Cuối ngày, quản lý cần xem:

- còn bao nhiêu task chưa xử lý
- còn bao nhiêu task quá hạn
- tỷ lệ hoàn tất task trong ngày
- nhân viên nào cần nhắc nhở hoặc hỗ trợ thêm

### Bước 10. Kiểm tra log tin nhắn

1. Vào `Tin nhắn đã gửi`.
2. Kiểm tra xem hệ thống có ghi log bình thường không.
3. Nếu có lỗi Lark, SMS, email thì ghi nhận để báo Admin.

## 6. Lưu ý quan trọng khi safe mode còn bật

Hiện tại `safe mode` đang bật.

Điều này có nghĩa:

- log có thể được tạo bình thường
- nhưng hệ thống chưa gửi SMS thật
- chưa gửi email thật
- chưa gửi Lark thật

Quản lý không được lấy log này để báo rằng chiến dịch chăm sóc đã chạy thật ra ngoài.

## 7. Checklist cuối ngày

- [ ] Đã xem dashboard chi nhánh buổi sáng
- [ ] Đã kiểm tra task cần gọi hôm nay
- [ ] Đã kiểm tra task quá hạn
- [ ] Đã kiểm tra khách VIP có nguy cơ
- [ ] Đã xác định nhân viên nào chưa xử lý
- [ ] Đã xem lý do khách rời bỏ
- [ ] Đã theo dõi lịch sử CSKH
- [ ] Đã kiểm tra phản hồi tiêu cực và hướng xử lý
- [ ] Đã xem tỷ lệ hoàn tất task cuối ngày
- [ ] Đã kiểm tra log tin nhắn
- [ ] Đã nhớ rằng safe mode vẫn đang ON
