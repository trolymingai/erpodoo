# Quy tắc nhập dữ liệu POS an toàn

## Nguyên tắc dữ liệu

- Cột `Ghi chú` chỉ được dùng làm **tên khách hàng dự phòng** khi dòng nhập không có cột tên hoặc cột tên đang trống.
- Nội dung `Ghi chú nội bộ` đang có trong ERP không bị ghi đè bởi file POS.
- Tên, số điện thoại, email, trạng thái CSKH, VIP, mức cảnh báo và các trường chăm sóc đã có không bị thay thế bằng giá trị mới. Hệ thống chỉ bổ sung thông tin nhận diện còn trống.
- Tổng chi tiêu, điểm tích lũy và ngày giao dịch cuối chỉ cập nhật theo snapshot mua hàng mới nhất. Snapshot cũ được lưu riêng trong **Lịch sử mua hàng**.

## Upload lại cùng file

- Mỗi dòng được tạo khóa dữ liệu nguồn ổn định từ nguồn, mã/ID khách, số điện thoại, email, ngày giao dịch, tổng chi tiêu và điểm tích lũy.
- Upload lại đúng cùng snapshot sẽ ghi nhận là trùng/bỏ qua, không tạo khách hoặc lịch sử mua hàng trùng.
- Upload snapshot mới của cùng khách sẽ không xóa snapshot cũ; hệ thống thêm một dòng lịch sử và đánh dấu dòng mới nhất.
- Import luôn tạo `ming.import.job`, `ming.pos.import.batch`, dòng chi tiết và nhật ký đồng bộ để đối soát.

## Cờ vận hành trên hồ sơ khách hàng

Hồ sơ khách hàng có các trường theo dõi:

- `Đã gọi`: tự bật khi ghi nhận một lần chăm sóc.
- `Đã nhận voucher`: tự bật khi kết quả là gửi ưu đãi hoặc quản lý ghi nhận đã tặng voucher.
- `Đã quay lại`: tự bật khi cảnh báo được đánh dấu đã quay lại hoặc engine nhận diện giao dịch mới trong cửa sổ chuyển đổi.

Các cờ này có bộ lọc trong màn **Khách hàng CSKH** và không làm thay đổi dữ liệu ghi chú.

## Cấu hình đọc dữ liệu POS

Trong **Cấu hình > Rule cảnh báo và connector**, tab **Đọc dữ liệu POS** cho phép khai báo:

- Chế độ đọc tệp POS/Excel, API KiotViet hoặc API máy POS.
- Địa chỉ API và thông tin xác thực.
- Tên cột mã khách, tên khách, ghi chú dự phòng, số điện thoại, chi nhánh, tổng chi tiêu, điểm tích lũy và ngày giao dịch cuối.

Hiện module đã sẵn sàng cho mapping và import tệp. Kết nối trực tiếp máy POS/API chỉ được bật sau khi có endpoint, tài khoản/API key, định dạng dữ liệu và cơ chế đồng bộ do nhà cung cấp POS xác nhận. Không tự động gọi endpoint khi chưa đủ cấu hình.

## Quy trình vận hành đề xuất

1. Sao lưu database, filestore và addon.
2. Chạy **Chỉ kiểm tra, chưa ghi dữ liệu**.
3. Kiểm tra lỗi, trùng khách, SĐT sai và chi nhánh không khớp.
4. Admin/Founder duyệt kết quả.
5. Chạy import thật.
6. Kiểm tra **Lịch sử mua hàng**, cờ vận hành và dashboard.
7. Giữ `safe_mode=True`; không bật SMS/email/Lark thật trong bước import.
