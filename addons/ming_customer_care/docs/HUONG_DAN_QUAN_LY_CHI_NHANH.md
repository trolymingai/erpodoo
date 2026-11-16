# Hướng Dẫn Quản Lý Chi Nhánh

## 1. Mục tiêu sử dụng

Quản lý chi nhánh dùng Ming Customer Care để:

- theo dõi tình hình CSKH của chi nhánh mình
- giám sát task của nhân viên
- xem khách VIP có nguy cơ
- xem lịch sử chăm sóc
- kiểm tra log cảnh báo và log an toàn

## 2. Cách vào Ming Customer Care

1. Đăng nhập bằng tài khoản quản lý chi nhánh.
2. Bấm app `Ming Customer Care`.
3. Hoặc vào `CRM > Ming Customer Care`.

## 3. Cách xem Dashboard

Trên `Bảng điều hành`, quản lý cần theo dõi:

- số khách thuộc chi nhánh
- khách có nguy cơ
- khách đã mất
- khách VIP
- task cần gọi hôm nay
- task quá hạn
- cảnh báo lần 1 / 2 / 3
- log SMS / email / Lark

Quản lý chỉ nhìn thấy dữ liệu chi nhánh mình.

## 4. Cách xử lý màn Cần gọi hôm nay

1. Vào `Cần gọi hôm nay`.
2. Kiểm tra:
   - task nào đang quá hạn
   - task VIP
   - task đã được nhân viên nhận chưa
3. Dùng filter:
   - `Hôm nay`
   - `Quá hạn`
   - `VIP`
   - `Cảnh báo lần 1 / 2 / 3`
   - `Chưa xử lý`
   - `Đang xử lý`
   - `Đã hoàn tất`
4. Dùng `Group By`:
   - `Nhóm theo nhân viên phụ trách`
   - `Nhóm theo trạng thái xử lý`
   - `Nhóm theo chi nhánh`

## 5. Cách nhận task

Thông thường quản lý không nhận thay nhân viên, nhưng có thể mở task để kiểm tra:

1. Mở task.
2. Xác nhận:
   - khách hàng
   - mức cảnh báo
   - nhân viên phụ trách
   - ngày cần gọi
3. Nếu cần hỗ trợ trực tiếp, quản lý có thể xử lý trên task theo đúng quyền được cấp.

## 6. Cách ghi nhận kết quả gọi

1. Mở task cần kiểm tra hoặc cần hỗ trợ.
2. Bấm `Ghi nhận kết quả gọi`.
3. Chọn kết quả phù hợp.
4. Điền ghi chú nếu quản lý trực tiếp xử lý.
5. Lưu lại để hệ thống tạo `Lịch sử CSKH`.

## 7. Cách hẹn gọi lại

1. Trong task, bấm `Hẹn gọi lại`.
2. Chọn trạng thái hẹn gọi lại.
3. Bắt buộc nhập `Ngày hẹn gọi lại`.
4. Ghi rõ lý do hoặc hướng xử lý.
5. Bấm `Lưu kết quả`.

Sau khi lưu:

- lịch sử CSKH được tạo
- task follow-up mới sẽ được tạo đúng ngày

## 8. Cách xem lịch sử CSKH

1. Vào menu `Lịch sử CSKH`.
2. Lọc theo:
   - nhân viên
   - kết quả chăm sóc
   - chi nhánh
3. Dùng `Group By` để xem hiệu suất:
   - theo nhân viên phụ trách
   - theo kết quả chăm sóc
   - theo ngày hẹn gọi lại

## 9. Cách kiểm tra Tin nhắn đã gửi

1. Vào `Tin nhắn đã gửi`.
2. Kiểm tra log theo:
   - SMS
   - email
   - Lark
3. Khi safe mode còn bật, log chủ yếu là log thử hoặc log an toàn.
4. Nếu Lark chưa cấu hình webhook, log failed là bình thường, hệ thống không được crash.

## 10. Những điều không được làm khi safe mode còn bật

- không thông báo với team rằng SMS đã gửi thật cho khách
- không xem log safe mode là bằng chứng gửi thật
- không yêu cầu nhân viên xác nhận khách đã nhận tin nếu log chỉ là `SAFE_MODE`
- không tự ý tắt safe mode nếu chưa có phê duyệt của Admin hoặc Founder

## 11. Điều quản lý cần kiểm tra mỗi ngày

- còn task quá hạn không
- nhân viên nào chưa nhận hoặc chưa xử lý task
- khách VIP có nguy cơ đang ở mức cảnh báo nào
- có follow-up task nào đến hạn hôm nay không
- có log lỗi Lark / SMS / email nào cần báo Admin không
