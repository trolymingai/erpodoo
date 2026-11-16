# Final UI Acceptance Checklist

## 1. Mục tiêu

Checklist này dùng để chốt lần cuối giao diện và vận hành của `ming_customer_care` trước khi bàn giao training nội bộ.

Phạm vi xác nhận:

- Không import dữ liệu khách hàng thật
- Không bật SMS thật
- Không bật email thật
- Không bật Lark thật
- Không thay đổi logic nghiệp vụ nếu không có lỗi blocker

## 2. Trạng thái tổng thể

- Kết luận hiện tại: `Đủ để bàn giao training nội bộ bằng demo/UAT data`
- Safe mode: `ON`
- Dữ liệu khách hàng thật: `Chưa import`
- SMS/email/Lark thật: `Chưa bật`

## 3. Kiểm tra màn hình chính

- [x] Dashboard
- [x] Khách hàng CSKH
- [x] Cần gọi hôm nay
- [x] Cảnh báo giữ chân
- [x] Lịch sử CSKH
- [x] Tin nhắn đã gửi
- [x] Nhập liệu / Đồng bộ
- [x] Form xử lý task CSKH

Ghi chú:

- Dashboard đã có action mở nhanh sang các màn vận hành chính.
- Form task đã có luồng `Nhận xử lý` -> `Ghi nhận kết quả gọi` -> `Hẹn gọi lại` -> `Đánh dấu hoàn tất`.
- Màn nhập liệu đang theo hướng an toàn: có dry-run và lịch sử import POS.

## 4. Kiểm tra UI

- [x] Menu tiếng Việt rõ ràng cho người dùng vận hành
- [x] Tên các màn chính dễ hiểu
- [x] Nút bấm chính của task dễ hiểu cho nhân viên CSKH
- [x] Dashboard đủ dễ xem để training
- [x] Form task đủ đơn giản để training nội bộ

Đánh giá thêm:

- Các menu vận hành chính đã Việt hóa: `Bảng điều hành`, `Khách hàng`, `Cần gọi hôm nay`, `Cảnh báo giữ chân`, `Lịch sử CSKH`, `Tin nhắn đã gửi`, `Nhập liệu / đồng bộ`, `Cấu hình`.
- Các filter vận hành chính đã Việt hóa.
- Các field nhạy cảm hoặc kỹ thuật đã được để `readonly` hoặc chỉ hiện cho Admin ở khu vực kỹ thuật.

Lỗi UI còn lại ở mức không blocker:

- Một số tên nhóm quyền nội bộ vẫn là tiếng Anh ở phần quản trị quyền, ví dụ `Ming CSKH Staff`, `Ming Branch Manager`, `Ming Founder/Admin`.
- Tên thương hiệu `Ming Customer Care` vẫn được giữ nguyên ở cấp app/menu, đây là chấp nhận được cho bàn giao nội bộ.
- Có thể còn một vài chuỗi kỹ thuật nhỏ chỉ xuất hiện trong vùng quản trị sâu của Odoo hoặc metadata, nhưng không phải luồng chính cho nhân viên vận hành.

## 5. Kiểm tra quyền

- [x] Admin thấy toàn hệ thống
- [x] Manager chỉ thấy chi nhánh mình
- [x] Staff chỉ thấy chi nhánh mình
- [x] Staff không sửa được trường nhạy cảm trên khách hàng

Các trường nhạy cảm đang được khóa đọc đối với giao diện vận hành:

- Tổng chi tiêu
- Điểm tích lũy
- Ngày giao dịch cuối
- Trạng thái khách
- VIP
- Mức cảnh báo
- Lần đồng bộ gần nhất

Vai trò cần có khi training thật:

- `Admin/Founder`
- `Quản lý chi nhánh`
- `Nhân viên CSKH`

## 6. Kiểm tra safe mode

- [x] `safe_mode = True`
- [x] Không gửi SMS thật
- [x] Không gửi email thật
- [x] Không gửi Lark thật
- [x] Có log để kiểm tra trong màn `Tin nhắn đã gửi`

Ghi chú:

- Cấu hình mặc định của module đang bật `safe_mode`.
- Training nội bộ phải tiếp tục dùng chế độ này cho đến khi có duyệt go-live dữ liệu thật.

## 7. Kết luận bàn giao

- [x] Các màn chính đã pass để training
- [x] Role chính đã pass để training
- [x] Safe mode vẫn đang ON
- [x] Không có lỗi blocker về UI trong phạm vi bàn giao training
- [x] Có thể bắt đầu training team bằng demo/UAT data

## 8. Việc cần chuẩn bị trước buổi training

- [ ] Tạo user thật cho 3 vai trò: Admin/Founder, Quản lý chi nhánh, Nhân viên CSKH
- [ ] Gán đúng chi nhánh cho từng user Manager/Staff
- [ ] Xác nhận dữ liệu đang dùng là demo/UAT
- [ ] Nhắc toàn team rằng SMS/email/Lark thật chưa được bật
- [ ] Không dùng dữ liệu demo để xử lý khách thật
