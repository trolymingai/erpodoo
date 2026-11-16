# Hướng Dẫn Nhân Viên CSKH

## 1. Mục tiêu sử dụng

Nhân viên CSKH dùng Ming Customer Care để:

- xem danh sách khách cần chăm sóc trong ngày
- nhận task và xử lý theo đúng quy trình
- ghi nhận kết quả gọi
- hẹn gọi lại khi cần
- xem lại lịch sử chăm sóc khách hàng
- kiểm tra log tin nhắn hệ thống đã tạo

## 2. Cách vào Ming Customer Care

1. Đăng nhập vào Odoo bằng tài khoản nhân viên CSKH.
2. Tại app launcher, bấm `Ming Customer Care`.
3. Nếu đang ở trong CRM, vào menu `CRM > Ming Customer Care`.
4. Màn hình đầu tiên nên mở là `Bảng điều hành`.

## 3. Cách xem Dashboard

Trên `Bảng điều hành`, nhân viên cần chú ý:

- `Tổng khách hàng`
- `Khách có nguy cơ`
- `Cần gọi hôm nay`
- `Task quá hạn`
- `Cảnh báo lần 1 / 2 / 3`

Các nút mở nhanh cần dùng:

- `Mở Cần gọi hôm nay`
- `Mở Khách hàng`
- `Mở Cảnh báo giữ chân`
- `Mở Lịch sử CSKH`
- `Mở Tin nhắn đã gửi`

## 4. Cách xử lý Cần gọi hôm nay

1. Vào menu `Cần gọi hôm nay`.
2. Dùng filter để xem đúng nhóm cần làm:
   - `Hôm nay`
   - `Quá hạn`
   - `VIP`
   - `Cảnh báo lần 1 / 2 / 3`
   - `Hẹn gọi lại`
3. Ưu tiên xử lý:
   - khách VIP
   - khách có tổng chi tiêu cao
   - task quá hạn

## 5. Cách nhận task

1. Mở một task trong danh sách.
2. Bấm nút `Nhận xử lý`.
3. Kiểm tra lại:
   - khách hàng
   - chi nhánh
   - mức cảnh báo
   - ngày cần gọi
4. Sau khi nhận, task sẽ chuyển sang trạng thái `Đang xử lý`.

## 6. Cách ghi nhận kết quả gọi

1. Mở task đang xử lý.
2. Bấm `Ghi nhận kết quả gọi`.
3. Chọn `Kết quả chăm sóc`.
4. Nhập `Ghi chú chăm sóc` nếu cần.
5. Nếu khách phản hồi đặc biệt, ghi rõ nội dung để quản lý theo dõi.
6. Bấm `Lưu kết quả`.

Lưu ý:

- mỗi lần lưu kết quả sẽ tạo một bản ghi trong `Lịch sử CSKH`
- nội dung ghi chú phải ngắn, rõ, đủ để người khác đọc lại

## 7. Cách hẹn gọi lại

1. Trong task, bấm `Hẹn gọi lại`.
2. Chọn trạng thái phù hợp, thường là `Đã gọi - Hẹn gọi lại lần 2`.
3. Bắt buộc nhập `Ngày hẹn gọi lại`.
4. Nhập ghi chú lý do hẹn lại.
5. Bấm `Lưu kết quả`.

Kết quả sau khi lưu:

- task hiện tại sẽ hoàn tất
- hệ thống tạo `Lịch sử CSKH`
- hệ thống tạo task follow-up mới đúng ngày hẹn gọi lại

## 8. Cách xem lịch sử CSKH

1. Vào menu `Lịch sử CSKH`.
2. Tìm theo:
   - tên khách
   - số điện thoại
   - chi nhánh
3. Có thể lọc nhanh:
   - `Hẹn gọi lại`
   - `Phản hồi tiêu cực`
4. Dùng `Group By` để nhóm theo:
   - chi nhánh
   - nhân viên phụ trách
   - kết quả chăm sóc
   - ngày hẹn gọi lại

## 9. Cách kiểm tra Tin nhắn đã gửi

1. Vào menu `Tin nhắn đã gửi`.
2. Kiểm tra các cột:
   - ngày tạo log
   - kênh gửi
   - khách hàng
   - người nhận / đích gửi
   - kết quả
3. Nếu cần, lọc theo:
   - `Chế độ an toàn`
   - kênh gửi
   - kết quả

## 10. Những điều không được làm khi safe mode còn bật

Khi `Chế độ an toàn` còn bật:

- không kết luận rằng SMS đã gửi thật cho khách
- không kết luận rằng email đã gửi thật cho khách
- không kết luận rằng Lark đã gửi thật vào nhóm
- không dùng log `SAFE_MODE` để báo là chiến dịch đã chạy thật
- không tự ý tắt safe mode nếu chưa có xác nhận từ Admin hoặc Founder

## 11. Lưu ý vận hành hằng ngày

- luôn xử lý hết task quá hạn trước khi kết thúc ca
- ghi chú phải đủ rõ để người khác nhận bàn giao được
- nếu số điện thoại sai hoặc không liên hệ được, phải ghi nhận đúng kết quả
- nếu thấy dữ liệu khách không đúng chi nhánh hoặc không đúng trạng thái, báo quản lý chi nhánh
