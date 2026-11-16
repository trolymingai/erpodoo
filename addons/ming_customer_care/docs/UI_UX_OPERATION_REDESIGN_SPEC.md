# UI/UX Operation Redesign Spec

## 1. Mục tiêu

Tài liệu này chốt định hướng redesign giao diện và cấu trúc vận hành cho module `ming_customer_care` theo hướng:

- `Staff-first` cho Phase 1
- Không sửa core Odoo
- Không sửa CRM core
- Không chuyển sang `crm.lead`
- Không thay đổi logic nghiệp vụ lõi nếu chưa cần
- `safe_mode = True` vẫn giữ nguyên
- Không bật SMS/email/Lark thật
- Không import dữ liệu khách hàng thật

Mục tiêu kinh doanh của Phase 1:

- Nhân viên CSKH đăng nhập vào là thấy ngay việc cần làm hôm nay
- Nhân viên biết khách nào cần gọi trước
- Nhân viên thao tác nhận xử lý, ghi nhận kết quả, hẹn gọi lại nhanh và rõ
- Quản lý có đủ góc nhìn để kiểm soát chi nhánh
- Founder/Admin có đủ dashboard tổng quan để theo dõi toàn hệ thống

## 2. Định hướng ưu tiên Phase 1

Tỷ trọng ưu tiên:

- Staff-first: `70%`
- Manager visibility cơ bản: `20%`
- Founder overview cơ bản: `10%`

Lý do:

- Chất lượng vận hành CSKH phụ thuộc trước hết vào việc nhân viên có dùng hệ thống mỗi ngày đúng và đều hay không.
- Nếu task không được xử lý đúng, lịch sử CSKH không được ghi nhận đúng, hoặc hẹn gọi lại không chuẩn, thì dashboard quản lý và báo cáo Founder cũng mất giá trị.

Kết luận thiết kế:

- Phase 1 phải tập trung tối đa vào màn hình vận hành cho Staff.
- Manager và Founder chỉ cần dashboard kiểm soát cơ bản, chưa làm phân tích sâu trong Phase đầu.

## 3. Cấu trúc app/menu đề xuất

App chính:

- `Ming Customer Care`

Nguyên tắc:

- `Ming Customer Care` là app vận hành riêng
- CRM mặc định không dùng làm nơi vận hành CSKH
- Không để trùng menu Ming Customer Care trong CRM

### Cấu trúc menu đề xuất

1. `Dashboard`

- Tổng quan hôm nay
- Hiệu suất CSKH
- Cảnh báo quan trọng

2. `Vận hành CSKH`

- Cần gọi hôm nay
- Quá hạn của tôi
- Hẹn gọi lại
- Khách VIP cần chăm sóc
- Lịch sử CSKH

3. `Khách hàng`

- Tất cả khách hàng
- Khách đang hoạt động
- Khách có nguy cơ
- Khách đã mất
- Khách VIP

4. `Cảnh báo giữ chân`

- Cảnh báo lần 1
- Cảnh báo lần 2
- Cảnh báo lần 3
- Phản hồi tiêu cực

5. `Tin nhắn / Gửi chăm sóc`

- Tin nhắn đã gửi
- Email đã gửi
- Nhật ký safe mode

6. `Báo cáo quản lý`

- Báo cáo theo chi nhánh
- Báo cáo theo nhân viên
- Tỷ lệ hoàn tất task
- Lý do khách rời bỏ
- Khách quay lại sau chăm sóc

7. `Cấu hình / Nhập liệu`

- Nhập khách hàng
- Đồng bộ dữ liệu
- Chi nhánh
- Rule phân loại khách
- Mẫu tin nhắn
- Cấu hình Safe Mode

## 4. Điểm vào app theo vai trò

### Staff

Khi mở app `Ming Customer Care`, Staff nên vào thẳng:

- `Việc của tôi hôm nay`
hoặc
- `Cần gọi hôm nay` với filter mặc định là việc của tôi

Mục tiêu:

- Không bắt nhân viên đi qua dashboard tổng có quá nhiều số liệu
- Không để nhân viên lạc sang Contacts mặc định hoặc CRM Pipeline

### Manager

Manager nên vào thẳng:

- `Dashboard chi nhánh`

Mục tiêu:

- Nhìn nhanh task hôm nay
- Task quá hạn
- Nhân viên chưa xử lý
- VIP có nguy cơ

### Admin/Founder

Admin/Founder nên vào thẳng:

- `Dashboard tổng`

Mục tiêu:

- Xem toàn hệ thống
- Không cần thao tác task quá chi tiết như Staff

## 5. Dashboard theo vai trò

### 5.1 Founder/Admin dashboard

Giữ ở mức overview cơ bản trong Phase 1:

- Tổng khách
- Active / At-risk / Lost
- VIP
- VIP có nguy cơ
- Task hôm nay
- Task quá hạn
- Tỷ lệ hoàn tất
- Alert lần 1 / 2 / 3

Chưa ưu tiên ở Phase 1:

- Dashboard phân tích sâu nhiều lớp
- Phân tích xu hướng dài hạn
- Drill-down quá phức tạp

### 5.2 Manager dashboard

Giữ ở mức kiểm soát chi nhánh:

- Task hôm nay của chi nhánh
- Task quá hạn
- Nhân viên chưa xử lý
- VIP có nguy cơ
- Tỷ lệ hoàn tất hôm nay
- Phản hồi tiêu cực

### 5.3 Staff dashboard

Đây là dashboard ưu tiên nhất trong Phase 1:

- Việc của tôi hôm nay
- Task chưa xử lý
- Task đang xử lý
- Hẹn gọi lại
- Quá hạn của tôi
- Khách ưu tiên cần gọi trước

Nguyên tắc:

- Ít KPI
- Nhiều hành động
- Dẫn thẳng sang màn xử lý task

## 6. Redesign mạnh cho màn Staff

Các màn cần redesign trước trong Phase 1:

1. `Cần gọi hôm nay`
2. `Hẹn gọi lại`
3. `Quá hạn của tôi`
4. `Form xử lý task`
5. `Lịch sử CSKH của khách`

### 6.1 Màn Cần gọi hôm nay

Cột cần hiển thị:

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

Filter mặc định:

- Việc của tôi hôm nay
- Chưa xử lý
- Đang xử lý
- Quá hạn
- VIP trước
- Cảnh báo lần 3
- Hẹn gọi lại hôm nay

Sort mặc định:

1. VIP có nguy cơ
2. Cảnh báo lần 3
3. Task quá hạn
4. Tổng chi tiêu cao
5. Ngày giao dịch cuối xa nhất

Mục tiêu trải nghiệm:

- Staff mở vào là biết gọi ai trước
- Không cần tự lọc thủ công nhiều bước

### 6.2 Màn Hẹn gọi lại

Mục tiêu:

- Tách rõ khỏi danh sách chung để Staff nhìn rõ các việc follow-up
- Có filter nhanh theo hôm nay, ngày mai, quá hạn

### 6.3 Màn Quá hạn của tôi

Mục tiêu:

- Giúp Staff thấy nợ việc của mình
- Hạn chế bỏ sót task cũ

### 6.4 Form xử lý task

Bố cục đề xuất:

1. Thông tin khách
2. Lý do cần gọi
3. Gợi ý nội dung gọi
4. Kết quả cuộc gọi
5. Hẹn gọi lại
6. Lịch sử chăm sóc gần nhất

Nút thao tác chính:

- Nhận xử lý
- Ghi nhận kết quả
- Hẹn gọi lại
- Đánh dấu hoàn tất
- Báo quản lý

Nguyên tắc:

- Ẩn field kỹ thuật khỏi Staff
- Giảm số field hiển thị trên cùng một màn
- Đưa lịch sử gần nhất xuống ngay trong task để không phải nhảy màn nhiều

### 6.5 Lịch sử CSKH của khách

Mục tiêu:

- Cho Staff xem nhanh lần chăm sóc gần nhất
- Nhìn được kết quả cũ trước khi gọi tiếp
- Hỗ trợ chăm sóc có ngữ cảnh

## 7. Tối ưu màn Khách hàng CSKH

Màn khách hàng cần chuyển từ dạng xem dữ liệu đơn thuần sang hỗ trợ chăm sóc.

Nhóm thông tin đề xuất:

1. Thông tin cơ bản
2. Thông tin chi tiêu
3. Trạng thái khách hàng
4. Lịch sử chăm sóc
5. Task đang mở
6. Cảnh báo giữ chân
7. Ghi chú nội bộ

Nguyên tắc:

- Staff không nên nhìn thấy field kỹ thuật
- Các thông tin cần cho cuộc gọi phải ở nửa trên form
- Lịch sử và task mở phải nhìn được ngay, không cần qua nhiều tab phức tạp

## 8. Cảnh báo giữ chân

Phase 1 chỉ cần cấu trúc rõ để vận hành:

- Cảnh báo lần 1
- Cảnh báo lần 2
- Cảnh báo lần 3
- Phản hồi tiêu cực

Mục tiêu:

- Staff và Manager đọc được danh sách cảnh báo theo mức độ
- Tập trung vào hành động tiếp theo, không chỉ xem danh sách

## 9. Tin nhắn / Gửi chăm sóc

Phase 1 chưa mở rộng thành trung tâm campaign.

Chỉ cần tổ chức rõ:

- Tin nhắn đã gửi
- Email đã gửi
- Nhật ký safe mode

Mục tiêu:

- Quản lý và Admin hiểu hệ thống đã tạo log gì
- Không nhầm log safe mode với gửi thật

## 10. Báo cáo quản lý

Phase 1 chỉ cần đủ dùng cho quản lý và Founder, chưa làm analytics sâu.

Cần có:

- Báo cáo theo chi nhánh
- Báo cáo theo nhân viên
- Báo cáo tỷ lệ hoàn tất task
- Báo cáo lý do khách rời bỏ
- Báo cáo khách VIP có nguy cơ
- Báo cáo khách quay lại sau chăm sóc

Ưu tiên hiển thị:

- Dễ đọc
- Ít thao tác
- Có thể drill down từ dashboard cơ bản

## 11. Ma trận quyền theo vai trò

### Admin/Founder

- Thấy toàn hệ thống
- Được cấu hình
- Được import
- Được xem báo cáo tổng

### Manager

- Chỉ thấy chi nhánh mình
- Xem báo cáo chi nhánh
- Xem nhân viên trong chi nhánh
- Không sửa rule hệ thống

### Staff

- Chỉ thấy task và khách của chi nhánh mình
- Xử lý task
- Ghi nhận CSKH
- Không sửa trường nhạy cảm

Kết luận:

- Phase 1 không cần đổi kiến trúc phân quyền
- Chỉ cần tối ưu UI theo vai trò dựa trên quyền hiện có

## 12. Nguyên tắc UI

- Tiếng Việt rõ ràng
- Không hiển thị field kỹ thuật cho nhân viên
- Dashboard không quá nhiều chữ
- Màn nhân viên ưu tiên thao tác nhanh
- Màn quản lý ưu tiên kiểm soát
- Màn Founder ưu tiên chỉ số và cảnh báo
- Không để trùng menu Ming Customer Care trong CRM
- Ming Customer Care là app riêng

## 13. Những màn cần redesign trước trong Phase 1

1. App landing theo role
2. Dashboard Staff
3. Dashboard Manager
4. Dashboard Founder/Admin
5. Màn Cần gọi hôm nay
6. Màn Hẹn gọi lại
7. Màn Quá hạn của tôi
8. Form xử lý task
9. Màn khách hàng CSKH
10. Màn lịch sử CSKH trong ngữ cảnh khách hàng

## 14. Những phần để Phase 2

Chưa làm sâu trong Phase 1:

- Dashboard phân tích nâng cao theo xu hướng
- Báo cáo drill-down đa lớp
- Thiết kế trung tâm gửi chăm sóc phức tạp
- Phân tích chuyên sâu khách quay lại
- Tối ưu UI cho campaign lớn
- Workflow mới ngoài logic lõi hiện có

## 15. View XML dự kiến sửa

Các file nhiều khả năng cần sửa trong triển khai Phase 1:

- `views/menu.xml`
- `views/dashboard_views.xml`
- `views/care_task_views.xml`
- `views/care_history_views.xml`
- `views/partner_views.xml`
- `views/alert_views.xml`
- `views/message_log_views.xml`
- `views/import_views.xml`

Có thể cần bổ sung:

- action riêng cho Staff landing
- action riêng cho Manager dashboard
- action riêng cho Founder/Admin dashboard

## 16. Ảnh hưởng tới logic nghiệp vụ

Đánh giá:

- `Không bắt buộc ảnh hưởng logic lõi` nếu triển khai đúng phạm vi Phase 1

Giải thích:

- Có thể redesign chủ yếu ở menu, action, domain mặc định, search filter, thứ tự cột, bố cục form, nhóm thông tin và role-based landing
- Logic phân loại khách, task, alert, care history, follow-up task có thể giữ nguyên

Chỉ có thể cần chạm nhẹ nếu muốn:

- tạo action mở theo role
- tối ưu default sort/filter
- thêm trường compute hiển thị ưu tiên rõ hơn cho list view

Những thay đổi này là thay đổi hỗ trợ UI vận hành, không phải thay đổi logic lõi nghiệp vụ

## 17. Ảnh hưởng tới phân quyền

Đánh giá:

- `Có ảnh hưởng nhẹ ở lớp trải nghiệm`
- `Không nên đổi record rule lõi trong Phase 1 nếu chưa có lỗi`

Ý nghĩa:

- Có thể cần điều chỉnh action/menu theo group để Staff, Manager, Founder vào đúng màn hơn
- Không cần thay đổi triết lý phân quyền hiện tại nếu các UAT role đã pass

## 18. Có cần backup trước khi triển khai không

Kết luận:

- `Có, bắt buộc backup trước khi sửa`

Nên backup:

- Database
- Filestore
- Source addon `ming_customer_care`
- Thư mục docs

Lý do:

- Dù chỉ sửa UI/menu/view, thay đổi ở XML action/menu vẫn có thể ảnh hưởng điều hướng live
- Cần khả năng rollback nhanh nếu giao diện mới gây rối cho team

## 19. Ước lượng triển khai

Ước lượng cho riêng Phase 1 Staff-first:

- Rà và chốt action/menu/view cần sửa: `0.5 ngày`
- Redesign menu + landing theo role: `0.5 ngày`
- Redesign dashboard theo 3 vai trò ở mức cơ bản: `1 ngày`
- Redesign màn Cần gọi hôm nay + filter/sort/list: `1 ngày`
- Redesign form task + lịch sử CSKH gần nhất: `1 ngày`
- Redesign màn khách hàng CSKH: `0.5 đến 1 ngày`
- Test role + polish + UAT nội bộ: `1 ngày`

Tổng ước lượng:

- `4.5 đến 5 ngày làm việc`

## 20. Kết luận

Spec này khóa hướng triển khai:

- `Phase 1 ưu tiên Staff-first`
- Manager và Founder chỉ giữ mức dashboard kiểm soát cơ bản
- Chưa mở rộng sang analytics sâu
- Chưa thêm tính năng mới nếu không thật sự cần
- Tập trung làm cho nhân viên CSKH dùng hằng ngày nhanh, rõ, ít rối và đúng quy trình
