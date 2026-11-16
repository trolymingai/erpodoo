# UI/UX Phase 1 Execution Log

## Trạng thái tổng hợp

- Batch 1: PASS - dọn menu trùng, giữ Ming Customer Care là app riêng.
- Batch 2: PASS - điều hướng theo vai trò.
- Batch 3: PASS - tối ưu danh sách Cần gọi hôm nay.
- Batch 3.1: PASS - thêm số điện thoại, mã khách và ngày giao dịch cuối vào list.
- Batch 4: PASS - tối ưu form xử lý task CSKH.
- Batch 5: PASS - tối ưu màn Khách hàng CSKH.
- Batch 6: PASS - dashboard Manager/Admin cơ bản.
- Batch 7: PASS - polish Tin nhắn, Cảnh báo và Nhập liệu.
- Batch 6.1: PASS một phần - branding Ming, dashboard card layout, backend accent.
- Batch 6.1.1: PASS một phần - favicon/logo/company logo xử lý ở mức an toàn.
- Data hardening audit 2026-08-02: PASS local; chưa deploy live version mới.

## Ràng buộc an toàn đang giữ

- Không sửa core Odoo.
- Không sửa CRM core.
- Không chuyển sang `crm.lead`.
- Không thay đổi record rule trong đợt data hardening.
- `safe_mode=True`.
- Không bật SMS thật, email thật hoặc Lark thật.
- Chưa import dữ liệu khách hàng thật.

## 2026-07-02 - Dashboard cleanup và encoding hotfix

- Đã thay dashboard view bằng bản sạch để loại bỏ lỗi tiếng Việt và chữ thừa.
- Đã đổi menu Nhập liệu/Đồng bộ thành Nhập dữ liệu để rõ nghiệp vụ.
- Đã sửa style tab Báo cáo nhanh để chữ không bị chìm khi active.
- Đã kiểm tra dashboard view, menu import và safe mode trên live tại thời điểm đó.

## 2026-07-02 - Full Vietnamese enable on live

- Đã kích hoạt/cài `vi_VN` trên live Odoo.
- Đã đặt ngôn ngữ user nội bộ và company partner sang `vi_VN`.
- Đã kiểm tra user nội bộ và Admin không còn dùng ngôn ngữ ngoài dự kiến.

## 2026-07-02 - UTF-8 Safety Rules

- Đã thêm `.editorconfig` để ép UTF-8, LF, dòng cuối và indentation thống nhất.
- Đã thêm `tools/check_vietnamese_encoding.py` để quét `ming_customer_care` và `ming_brand_theme`.
- Quy tắc bắt buộc: nếu scan encoding lỗi thì dừng upgrade/deploy và sửa encoding trước.
- Không thay đổi business logic, record rule hoặc connector thật trong đợt này.

## 2026-07-02 - Nhập dữ liệu menu action fix

- Menu `Nhập dữ liệu` là leaf menu trỏ trực tiếp vào import wizard.
- Lịch sử import POS là menu riêng để không làm menu nhập liệu biến thành thư mục.
- Không chạy import và không ghi dữ liệu khách thật.

## 2026-07-02 - SMS/Email controlled sending foundation

- Đã thêm service SMS/email, provider, kiểm soát chi phí và wizard gửi thủ công.
- Đã mở rộng `ming.message.log` với safe mode, test mode, chi phí và trạng thái chi tiết.
- Mặc định vẫn là `safe_mode=True`, `test_mode=True`, `sms_enabled=False`, `email_enabled=False`.
- Không bật gửi SMS/email/Lark thật.

## 2026-07-02 - Vietnamese UI label normalization

- Đã chuẩn hóa label hiển thị của task, khách hàng và dashboard bằng chuỗi Unicode an toàn.
- Đã kiểm tra label runtime không còn chuỗi không dấu trong luồng chính.
- Không đổi workflow CSKH, connector hoặc record rule.

## 2026-08-02 - Data integration hardening và audit build

- Backup source trước audit: thực hiện theo quy trình local; version source sau audit là `19.0.1.2.2`.
- Bổ sung `active` cho cấu hình phân loại để có thể tắt cấu hình cũ an toàn.
- Bổ sung thứ hạng VIP theo từng chi nhánh và hiển thị readonly trong hồ sơ khách.
- Bổ sung kết quả chăm sóc trên task và ẩn snapshot kỹ thuật khỏi vai trò không phải Admin/Founder.
- Bổ sung chống trùng task hẹn gọi lại, task phản hồi tiêu cực, cảnh báo chuyển đổi và log gửi lại.
- Bổ sung khóa kênh SMS/email/Lark trước provider; khi kênh tắt chỉ ghi log bị chặn.
- Bổ sung adapter Lark an toàn, không gọi thật khi safe mode/test mode hoặc thiếu cấu hình.
- Đưa khách nhập thủ công có nguồn và chi nhánh vào phạm vi danh sách/dashboard Ming; không đưa toàn bộ Contacts vào.
- Không chạm core Odoo, CRM core, record rule, dữ liệu demo/UAT hoặc connector thật.

### Kết quả kiểm tra

- Python compile: PASS.
- XML parse: PASS.
- ACL model coverage runtime: PASS.
- Fresh install và upgrade local: PASS.
- Test contract Odoo: 7/7 PASS.
- Dry-run demo khách: 260 dòng kiểm tra, 11 cảnh báo số điện thoại, không ghi dữ liệu.
- Dry-run sales: 2.289 dòng kiểm tra, 49 dòng trùng khóa nguồn; 1.185 dòng `Phố Digital` chờ ánh xạ, không ghi dữ liệu.
- Test import lặp trong transaction rồi rollback: không tạo khách hoặc dòng bán hàng trùng.
- Safe mode sau test: vẫn `True`.

### Việc còn lại trước production

- Upgrade `19.0.1.2.2` trên staging và smoke test bằng database staging.
- Xác nhận ánh xạ `Phố Digital` trước khi import dữ liệu bán hàng thật.
- Nhận file khách thật, chạy dry-run và chờ Admin/Founder duyệt.
- Chốt quy tắc thời điểm cảnh báo lần 2/lần 3.
- Chỉ triển khai API KiotViet sau khi có credential, mapping contract, retry/cursor và UAT.

## 2026-08-03 23:51 +07:00 - Nhập POS an toàn, lịch sử mua hàng và cờ vận hành

- Backup trước deploy: `/opt/mingcrm/backups/customer_import_safety_20260803_183741`.
- Nâng version module lên `19.0.1.2.4`; source live đã được backup và thay theo staging source.
- File runtime đã cập nhật: `models/purchase_history.py`, `models/res_partner.py`, `models/care_history.py`, `models/retention_alert.py`, `models/retention_engine.py`, `models/segment_config.py`, `wizards/import_wizard.py`, các view/ACL/record rule/menu liên quan và manifest.
- `Ghi chú` chỉ làm tên dự phòng khi thiếu tên; không ghi vào `comment` hoặc `ming_customer_note` đã có trong ERP.
- Upload lại đúng snapshot được nhận diện trùng; snapshot mới theo ngày/số liệu tạo thêm dòng **Lịch sử mua hàng**, không xóa dòng cũ.
- Bổ sung cờ hồ sơ khách: `Đã gọi`, `Đã nhận voucher`, `Đã quay lại`; có bộ lọc trên màn Khách hàng CSKH.
- Bổ sung màn/menu **Lịch sử mua hàng** và tab lịch sử trong hồ sơ khách.
- Bổ sung cấu hình mapping cột POS/API; chế độ mặc định vẫn là đọc tệp. Chưa bật kết nối trực tiếp máy POS vì chưa có endpoint/credential/protocol do nhà cung cấp xác nhận.
- Upgrade live: PASS. Restart Odoo: PASS. HTTP live: `303`. Log container chính sau restart: không có ERROR/CRITICAL/Traceback/ParseError.
- Live transaction test: PASS cho name fallback, bảo toàn ghi chú ERP, idempotent upload, snapshot mua hàng mới, cờ CSKH và safe mode; transaction QA đã rollback.
- Kiểm tra sau test: module `installed` `19.0.1.2.4`, model/ACL/rule/menu lịch sử mua hàng tồn tại, không còn bản ghi QA.
- `safe_mode=True`, `test_mode=True`, `email_enabled=False`, `sms_enabled=False`; không gửi SMS/email/Lark thật và không import dữ liệu thật.
