# Go Live Real Data Checklist

## Chuẩn bị file khách hàng thật

- [ ] Nhận file khách hàng thật từ POS/KiotViet
- [ ] Kiểm tra có đủ mã khách hàng
- [ ] Kiểm tra có đủ tên khách hàng
- [ ] Kiểm tra có đủ số điện thoại
- [ ] Kiểm tra có email nếu có
- [ ] Kiểm tra có chi nhánh
- [ ] Kiểm tra có tổng chi tiêu
- [ ] Kiểm tra có điểm tích lũy nếu có
- [ ] Kiểm tra có ngày giao dịch cuối
- [ ] Kiểm tra có nguồn dữ liệu

## Chuẩn bị trước khi import

- [ ] Backup database trước import
- [ ] Backup filestore trước import
- [ ] Backup addon trước import
- [ ] Dọn demo/UAT data hoặc đánh dấu rõ source
- [ ] Chuẩn bị đúng file import

## Dry-run và kiểm tra chất lượng dữ liệu

- [ ] Chạy dry-run
- [ ] Báo số dòng hợp lệ
- [ ] Báo số dòng lỗi
- [ ] Báo số điện thoại sai
- [ ] Báo khách trùng
- [ ] Báo chi nhánh không match

## Duyệt trước khi import thật

- [ ] Admin/Founder đã duyệt kết quả dry-run
- [ ] Chỉ import thật sau khi đã duyệt

## Sau khi import thật

- [ ] Chạy phân loại ngoài giờ
- [ ] UAT lại với dữ liệu thật
- [ ] Kiểm tra dashboard sau import
- [ ] Kiểm tra task chăm sóc sau import
- [ ] Kiểm tra cảnh báo giữ chân sau import

## Thứ tự bật connector thật

- [ ] Bật Lark trước
- [ ] Bật email sau
- [ ] Bật SMS cuối cùng
