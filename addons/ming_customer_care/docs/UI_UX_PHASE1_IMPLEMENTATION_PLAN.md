# UI/UX Phase 1 Implementation Plan

## 1. Mục tiêu

Kế hoạch này triển khai `Phase 1 Staff-first UI/UX Redesign` cho module `ming_customer_care`.

Nguyên tắc bắt buộc:

- Ưu tiên `Staff-first`
- Không sửa core Odoo
- Không sửa CRM core
- Không chuyển sang `crm.lead`
- Không thay đổi logic lõi nếu không bắt buộc
- Chỉ tối ưu trong module custom `ming_customer_care`
- `safe_mode` vẫn `True`
- Không bật SMS/email/Lark thật
- Không import dữ liệu khách hàng thật

Mục tiêu vận hành:

- Nhân viên đăng nhập vào là thấy ngay việc cần làm hôm nay
- Form xử lý task nhanh, gọn, ít rối
- Manager vẫn kiểm soát được chi nhánh ở mức cơ bản
- Founder/Admin vẫn xem được overview tổng

## 2. Chiến lược triển khai

Triển khai theo từng batch nhỏ, có kiểm tra sau mỗi batch.

Lý do:

- Giảm rủi ro khi sửa trực tiếp trên môi trường đang live
- Dễ rollback nếu lỗi nằm ở menu, dashboard hoặc form task
- Không làm đứt quy trình đang dùng demo/UAT

Thứ tự ưu tiên:

1. Dọn cấu trúc menu và app
2. Điều hướng theo vai trò
3. Tối ưu danh sách việc của Staff
4. Tối ưu form thao tác Staff
5. Tối ưu màn khách hàng CSKH
6. Giữ dashboard Manager/Admin ở mức kiểm soát cơ bản
7. Dọn nhẹ các màn phụ để đồng bộ trải nghiệm

## 3. Pre-flight / Backup

### 3.1 Việc phải làm trước khi sửa

- Backup database
- Backup filestore
- Backup source addon `ming_customer_care`
- Backup thư mục `docs/`

### 3.2 Thông tin cần ghi lại

- Backup path
- Thời gian backup
- Trạng thái `safe_mode` hiện tại
- Tên database live
- Phiên bản module hiện tại
- Số liệu demo/UAT hiện tại trước khi sửa

### 3.3 Dữ liệu snapshot nên ghi lại

- Số khách hàng CSKH
- Số task hôm nay
- Số task quá hạn
- Số alert 1 / 2 / 3
- Số message log
- Số task đã hoàn tất

### 3.4 Tiêu chí hoàn tất pre-flight

- Có backup đầy đủ
- Có thể rollback source addon
- Có thể restore DB nếu cần
- Xác nhận `safe_mode = True`

## 4. Batch 1: Dọn menu và app structure

### 4.1 Mục tiêu

- Chỉ giữ `Ming Customer Care` là app riêng
- Không còn menu trùng trong CRM
- App `Ming Customer Care` mở đúng landing hoặc dashboard
- Không làm mất menu con hiện tại

### 4.2 File dự kiến sửa

- `views/menu.xml`

Có thể cần kiểm tra thêm:

- `ir.ui.menu` trong database nếu menu cũ còn tồn tại

### 4.3 Phạm vi thay đổi

- Chỉ menu, action, parent menu, sequence, group hiển thị
- Không chạm model nghiệp vụ

### 4.4 Rủi ro

- Menu cũ còn tồn tại trong DB dù XML đã sửa
- User cache/browser cache làm nhìn như chưa đổi
- App entry và menu con bị lệch parent

### 4.5 Test sau batch

- App launcher chỉ thấy `1` app `Ming Customer Care`
- CRM gốc không còn menu `Ming Customer Care` trùng
- Admin/Manager/Staff vẫn vào được app
- Menu con vẫn mở đúng action

### 4.6 Mức rủi ro

- `Trung bình`

## 5. Batch 2: Role-based landing

### 5.1 Mục tiêu

- Staff mở vào `Việc của tôi hôm nay` hoặc `Cần gọi hôm nay`
- Manager mở vào dashboard chi nhánh
- Admin/Founder mở vào dashboard tổng
- Không đổi record rule lõi

### 5.2 File dự kiến sửa

- `views/dashboard_views.xml`
- `views/menu.xml`

Có thể cần thêm:

- action riêng cho Staff
- action riêng cho Manager
- action riêng cho Admin/Founder

Nếu cần code nhẹ:

- model dashboard hoặc helper method rất nhỏ để chọn action theo role

### 5.3 Rủi ro

- Odoo menu app mặc định thường trỏ một action cố định
- Nếu muốn landing khác nhau theo role có thể phải thêm lớp điều hướng nhẹ
- Nếu làm quá tay dễ chạm sang logic điều hướng ngoài phạm vi UI

### 5.4 Nguyên tắc thực hiện

- Ưu tiên dùng action/window action + group trước
- Chỉ code nhẹ nếu không thể đạt bằng XML/action
- Không thay record rule lõi

### 5.5 Test sau batch

- Staff vào đúng màn vận hành
- Manager vào đúng dashboard chi nhánh
- Admin vào dashboard tổng
- Không đổi record rule lõi

### 5.6 Mức rủi ro

- `Trung bình đến cao`

## 6. Batch 3: Tối ưu màn Staff - Cần gọi hôm nay

### 6.1 Mục tiêu

- Danh sách dễ đọc
- Nhân viên biết ai cần gọi trước
- Filter mặc định rõ
- Sort mặc định đúng ưu tiên vận hành

### 6.2 Cột ưu tiên hiển thị

- Mức ưu tiên
- Tên khách
- Số điện thoại
- Chi nhánh
- Nhóm khách
- Cảnh báo lần mấy
- Tổng chi tiêu
- Ngày giao dịch cuối
- Trạng thái xử lý
- Nhân viên phụ trách
- Ngày hẹn gọi lại

### 6.3 Filter cần có

- Việc của tôi hôm nay
- Chưa xử lý
- Đang xử lý
- Quá hạn
- VIP trước
- Cảnh báo lần 3
- Hẹn gọi lại hôm nay

### 6.4 Sort mặc định

1. VIP có nguy cơ
2. Cảnh báo lần 3
3. Task quá hạn
4. Tổng chi tiêu cao
5. Ngày giao dịch cuối xa nhất

### 6.5 File dự kiến sửa

- `views/care_task_views.xml`

Có thể cần chạm nhẹ nếu muốn sort ổn định hơn:

- model `ming.care.task`

### 6.6 Rủi ro

- Một số tiêu chí sort có thể chưa có field hiển thị đúng thứ tự sẵn
- Có thể phải dùng default order hoặc field hỗ trợ hiển thị ưu tiên
- Nếu thêm field hỗ trợ thì là chạm logic nhẹ

### 6.7 Test sau batch

- Staff thấy đúng task chi nhánh mình
- Staff không thấy chi nhánh khác
- Filter/search/group hoạt động
- List/form/search không crash

### 6.8 Mức rủi ro

- `Trung bình`

## 7. Batch 4: Tối ưu form xử lý task

### 7.1 Mục tiêu

Form task đi theo luồng thao tác thực tế:

1. Thông tin khách
2. Lý do cần gọi
3. Gợi ý nội dung gọi
4. Kết quả cuộc gọi
5. Hẹn gọi lại
6. Lịch sử chăm sóc gần nhất

### 7.2 Nút thao tác chính

- Nhận xử lý
- Ghi nhận kết quả
- Hẹn gọi lại
- Đánh dấu hoàn tất
- Báo quản lý

### 7.3 Yêu cầu

- Ẩn field kỹ thuật khỏi Staff
- Trường nhạy cảm vẫn chỉ đọc
- Không làm hỏng wizard ghi nhận CSKH
- Không làm hỏng tạo `ming.care.history`
- Không làm hỏng follow-up task

### 7.4 File dự kiến sửa

- `views/care_task_views.xml`
- `wizards/care_history_wizard_views.xml`
- có thể `views/care_history_views.xml`

### 7.5 Có thể chạm nhẹ logic ở đâu

- Nếu cần thêm action phụ hoặc button mở wizard theo luồng mới
- Nếu cần hiển thị lịch sử gần nhất trực tiếp trong task bằng domain/context

### 7.6 Rủi ro

- Đây là batch dễ đụng workflow thật nhất
- Nếu bố cục/wizard lệch có thể ảnh hưởng trực tiếp thao tác của Staff

### 7.7 Test sau batch

- Nhận xử lý pass
- Ghi nhận kết quả pass
- Hẹn gọi lại pass
- Task gốc chuyển trạng thái đúng
- Tạo history đúng
- Tạo follow-up task đúng

### 7.8 Mức rủi ro

- `Cao nhất`

## 8. Batch 5: Tối ưu màn Khách hàng CSKH

### 8.1 Mục tiêu

Form khách hàng CSKH dễ đọc, không giống Contacts mặc định gây rối.

### 8.2 Nhóm thông tin nên có

- Thông tin cơ bản
- Thông tin chi tiêu
- Trạng thái khách hàng
- Lịch sử chăm sóc
- Task đang mở
- Cảnh báo giữ chân
- Ghi chú nội bộ

### 8.3 Yêu cầu

- Staff không sửa được trường nhạy cảm
- Không đụng Contacts core
- Chỉ sửa view kế thừa hoặc custom view của `ming_customer_care`

### 8.4 File dự kiến sửa

- `views/partner_views.xml`
- `views/care_history_views.xml`
- `views/alert_views.xml`

### 8.5 Rủi ro

- Nếu nhồi quá nhiều thông tin vào form sẽ phản tác dụng
- Cần giữ cân bằng giữa thông tin đủ dùng và không rối

### 8.6 Test sau batch

- Mở khách hàng từ task không bị rối
- Staff chỉ thấy khách chi nhánh mình
- Manager chỉ thấy khách chi nhánh mình
- Admin thấy toàn hệ thống

### 8.7 Mức rủi ro

- `Trung bình`

## 9. Batch 6: Dashboard Manager/Admin cơ bản

### 9.1 Mục tiêu

#### Manager

- Task hôm nay của chi nhánh
- Task quá hạn
- Nhân viên chưa xử lý
- VIP có nguy cơ
- Tỷ lệ hoàn tất hôm nay
- Phản hồi tiêu cực

#### Founder/Admin

- Tổng khách
- Active / At-risk / Lost
- VIP / VIP nguy cơ
- Task hôm nay
- Task quá hạn
- Alert 1 / 2 / 3
- Tỷ lệ hoàn tất toàn hệ thống

### 9.2 File dự kiến sửa

- `views/dashboard_views.xml`

Có thể chạm nhẹ nếu thật sự cần:

- `models/dashboard.py`

### 9.3 Nguyên tắc

- Hạn chế tối đa logic mới
- Ưu tiên tái dùng các field compute đã có
- Chưa làm dashboard phân tích sâu

### 9.4 Rủi ro

- Nếu thêm compute mới có thể ảnh hưởng hiệu năng hoặc độ đúng số liệu
- Cần giới hạn ở mức overview cơ bản

### 9.5 Test sau batch

- Dashboard Staff/Manager/Admin mở đúng
- Số liệu không sai lệch bất thường
- Không chậm hơn đáng kể
- Không phá dữ liệu demo/UAT

### 9.6 Mức rủi ro

- `Trung bình`

## 10. Batch 7: Tin nhắn, cảnh báo, nhập liệu giữ ổn định

### 10.1 Mục tiêu

- Không redesign sâu trong Phase 1
- Chỉ dọn menu, filter, label nếu cần
- Không bật gửi thật
- `safe_mode` vẫn ON

### 10.2 File có thể sửa nhẹ

- `views/message_log_views.xml`
- `views/alert_views.xml`
- `views/import_views.xml`

### 10.3 Rủi ro

- Thấp nếu chỉ dọn view
- Tăng lên nếu chạm vào action gửi/log hoặc import flow

### 10.4 Test sau batch

- Log safe mode vẫn đọc được
- Cảnh báo vẫn mở đúng
- Nhập liệu vẫn mở đúng
- Không có gửi thật

### 10.5 Mức rủi ro

- `Thấp`

## 11. Regression test bắt buộc

### 11.1 Role phải test lại

- Admin/Founder
- Manager `MING-PR`
- Staff `MING-PR`

### 11.2 Luồng phải test lại

- Login
- Mở app `Ming Customer Care`
- Mở landing đúng role
- Xem `Cần gọi hôm nay`
- Nhận xử lý
- Ghi nhận kết quả
- Hẹn gọi lại
- Tạo care history
- Tạo follow-up task
- Xem khách hàng CSKH
- Xem lịch sử CSKH
- Xem cảnh báo
- Xem message log safe mode
- Manager chỉ thấy chi nhánh mình
- Staff chỉ thấy chi nhánh mình
- Admin thấy toàn hệ thống

### 11.3 Checklist sau mỗi batch

#### Sau Batch 1

- [ ] App launcher chỉ còn 1 Ming Customer Care
- [ ] CRM không còn menu trùng
- [ ] User vào được app

#### Sau Batch 2

- [ ] Staff vào đúng màn vận hành
- [ ] Manager vào dashboard chi nhánh
- [ ] Admin vào dashboard tổng

#### Sau Batch 3

- [ ] Filter mặc định hoạt động
- [ ] Sort ưu tiên hoạt động hợp lý
- [ ] Staff chỉ thấy task chi nhánh mình

#### Sau Batch 4

- [ ] Luồng xử lý task không vỡ
- [ ] History vẫn tạo đúng
- [ ] Follow-up task vẫn tạo đúng

#### Sau Batch 5

- [ ] Form khách hàng dễ đọc hơn
- [ ] Không lộ field kỹ thuật cho Staff
- [ ] Không vỡ quyền xem khách

#### Sau Batch 6

- [ ] Dashboard đúng vai trò
- [ ] Số liệu không lệch bất thường
- [ ] Không chậm đáng kể

#### Sau Batch 7

- [ ] Message log vẫn đúng safe mode
- [ ] Alert vẫn mở đúng
- [ ] Import screen vẫn ổn định

## 12. Rollback plan

### 12.1 Nếu lỗi menu

Rollback chính:

- `views/menu.xml`

Nếu menu record trong DB bị lệch:

- rollback source addon trước
- upgrade lại module
- chỉ restore DB nếu menu bị hỏng quá mức và khó sửa nhanh

### 12.2 Nếu lỗi dashboard

Rollback file:

- `views/dashboard_views.xml`
- nếu có chạm model: `models/dashboard.py`

### 12.3 Nếu lỗi task form

Rollback file:

- `views/care_task_views.xml`
- `wizards/care_history_wizard_views.xml`
- `views/care_history_views.xml`

### 12.4 Nếu lỗi quyền

Rollback file:

- view/action/menu trước
- chỉ rollback `record_rules.xml` hoặc `security` nếu thật sự có sửa vào đó

Nguyên tắc:

- Phase 1 không chủ động sửa record rule lõi
- nếu có lỗi quyền thì ưu tiên rollback action/view trước

### 12.5 Khi nào restore DB

Restore DB khi:

- upgrade module làm hỏng metadata khó sửa nhanh
- mất cấu trúc menu nghiêm trọng
- dashboard hoặc action lỗi hàng loạt
- thao tác Staff bị block toàn bộ

### 12.6 Khi nào chỉ rollback addon source

Chỉ rollback source khi:

- lỗi chủ yếu ở XML view/menu/action
- logic dữ liệu không bị ảnh hưởng
- có thể sửa bằng upgrade lại module

## 13. Đánh giá rủi ro theo batch

### Batch có rủi ro cao nhất

- `Batch 4: Tối ưu form xử lý task`

Lý do:

- chạm trực tiếp luồng thao tác thật của Staff
- liên quan wizard ghi nhận CSKH
- liên quan tạo history và follow-up task

### Batch có rủi ro trung bình cao

- `Batch 2: Role-based landing`

Lý do:

- có thể cần điều hướng theo role
- dễ gây hiểu nhầm hoặc vào sai màn nếu cấu hình action không chuẩn

### Batch chủ yếu là UI

- Batch 1
- Batch 3
- Batch 5
- Batch 7

### Batch có thể chạm logic nhẹ

- Batch 2
- Batch 3
- Batch 4
- Batch 6

## 14. Có cần staging không

Kết luận:

- `Có, nên có staging`

Lý do:

- Phase 1 tuy thiên về UI nhưng vẫn chạm action, landing, dashboard và form task
- form task là luồng vận hành quan trọng
- staging giúp kiểm tra từng batch trước khi áp live

### Nếu chưa có staging riêng

Khuyến nghị:

- dùng bản sao DB demo/UAT
- giữ `safe_mode = True`
- test đủ 3 role trước khi chạm live

## 15. Nếu không có staging, khung giờ deploy live an toàn

Khung giờ khuyến nghị:

- ngoài giờ vận hành
- cuối ngày sau khi team ngừng thao tác
- tránh giờ cao điểm CSKH

Khung triển khai an toàn nhất:

- `21:00 - 23:30` hoặc `sáng sớm trước giờ làm`

Nguyên tắc:

- mỗi batch nên deploy tách biệt
- test nhanh ngay sau deploy
- nếu có lỗi thì rollback ngay trong cùng khung giờ

## 16. Ước lượng thời gian từng batch

- Pre-flight / Backup: `0.5 ngày`
- Batch 1: `0.5 ngày`
- Batch 2: `0.5 đến 1 ngày`
- Batch 3: `1 ngày`
- Batch 4: `1 ngày`
- Batch 5: `0.5 đến 1 ngày`
- Batch 6: `1 ngày`
- Batch 7: `0.5 ngày`
- Regression test + polish: `1 ngày`

Tổng:

- `5 đến 6 ngày làm việc`

## 17. Kết luận triển khai

Kế hoạch triển khai Phase 1 nên đi theo thứ tự:

1. Backup đầy đủ
2. Dọn menu/app structure
3. Chốt landing theo role
4. Tối ưu danh sách việc của Staff
5. Tối ưu form task
6. Tối ưu màn khách hàng
7. Giữ dashboard Manager/Admin ở mức cơ bản
8. Dọn nhẹ cảnh báo, message log, import
9. Regression test đủ 3 role

Trọng tâm của toàn bộ Phase 1:

- làm cho Staff dùng nhanh và đúng mỗi ngày
- không làm vỡ workflow hiện có
- không đánh đổi tính ổn định để lấy thêm tính năng
