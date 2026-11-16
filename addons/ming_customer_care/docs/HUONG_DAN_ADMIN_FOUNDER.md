# Hướng Dẫn Admin Founder

## 1. Mục tiêu sử dụng

Admin hoặc Founder dùng Ming Customer Care để:

- xem toàn hệ thống
- theo dõi Dashboard tổng hợp
- kiểm tra chất lượng vận hành của các chi nhánh
- kiểm tra rule, cấu hình, connector và safe mode
- hỗ trợ import dữ liệu và kiểm tra log hệ thống

## 2. Cách vào Ming Customer Care

1. Đăng nhập bằng tài khoản Admin hoặc Founder.
2. Bấm app `Ming Customer Care`.
3. Hoặc vào `CRM > Ming Customer Care`.
4. Có thể vào thẳng Dashboard nếu cần.

## 3. Cách xem Dashboard

Dashboard dùng để theo dõi toàn hệ thống:

- tổng khách hàng
- khách đang hoạt động
- khách có nguy cơ
- khách đã mất
- khách VIP
- số task cần gọi hôm nay
- số task quá hạn
- số cảnh báo lần 1 / 2 / 3
- số log SMS / email / Lark
- top chi nhánh có nguy cơ
- top sản phẩm / doanh thu

## 4. Cách xử lý Cần gọi hôm nay

1. Vào `Cần gọi hôm nay`.
2. Dùng filter để kiểm tra chất lượng vận hành:
   - `Quá hạn`
   - `VIP`
   - `Đang xử lý`
   - `Đã hoàn tất`
3. Dùng `Group By`:
   - theo chi nhánh
   - theo trạng thái xử lý
   - theo nhân viên phụ trách
4. Xác định chi nhánh hoặc nhân viên đang bị tồn task.

## 5. Cách nhận task

Admin có thể mở và nhận task khi cần hỗ trợ xử lý trực tiếp:

1. Mở task.
2. Bấm `Nhận xử lý`.
3. Xác nhận người phụ trách hiện tại và trạng thái trước khi can thiệp.

## 6. Cách ghi nhận kết quả gọi

1. Mở task.
2. Bấm `Ghi nhận kết quả gọi`.
3. Chọn kết quả phù hợp.
4. Điền ghi chú rõ ràng nếu Admin hoặc Founder trực tiếp tham gia.
5. Lưu để tạo `Lịch sử CSKH`.

## 7. Cách hẹn gọi lại

1. Trong task, bấm `Hẹn gọi lại`.
2. Chọn trạng thái hẹn gọi lại.
3. Bắt buộc nhập `Ngày hẹn gọi lại`.
4. Ghi chú thêm nếu cần follow-up bởi quản lý hoặc nhân viên khác.

## 8. Cách xem lịch sử CSKH

1. Vào `Lịch sử CSKH`.
2. Xem theo:
   - chi nhánh
   - nhân viên
   - kết quả chăm sóc
   - ngày hẹn gọi lại
3. Dùng màn này để audit chất lượng chăm sóc và kiểm tra việc bàn giao.

## 9. Cách kiểm tra Tin nhắn đã gửi

1. Vào `Tin nhắn đã gửi`.
2. Kiểm tra log theo:
   - kênh gửi
   - trạng thái
   - khách hàng
3. Kiểm tra các log:
   - `SAFE_MODE`
   - lỗi webhook Lark
   - lỗi email
   - lỗi số điện thoại không hợp lệ

## 10. Những điều không được làm khi safe mode còn bật

- không bật gửi SMS thật nếu chưa hoàn tất UAT
- không bật gửi email thật khi chưa kiểm tra sender và template
- không bật webhook Lark thật khi chưa test log
- không dùng log safe mode để báo là chiến dịch đã chạy production
- không giao cho team vận hành hiểu nhầm rằng log là gửi thật

## 11. Những việc Admin hoặc Founder cần kiểm tra định kỳ

- CRM official và Ming Customer Care còn installed không
- app launcher còn thấy `CRM` và `Ming Customer Care` không
- safe mode còn đang bật không
- cron retention còn chạy bình thường không
- chi nhánh nào có nhiều khách nguy cơ tăng bất thường
- có import lỗi hoặc dữ liệu chi nhánh không match không
- connector nào đang thiếu cấu hình hoặc đang fail log
