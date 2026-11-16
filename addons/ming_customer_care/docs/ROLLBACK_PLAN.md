# Rollback Plan

## Backup cuối nằm ở đâu

- Backup cuối được lưu trong thư mục backup có timestamp trên server
- Tên thư mục theo mẫu: `/opt/mingcrm/backups/final_handoff_YYYYMMDD_HHMMSS`

## Khi có lỗi nghiêm trọng thì xử lý thế nào

Chỉ rollback khi:

- có lỗi nghiêm trọng ảnh hưởng vận hành
- đã có người duyệt rollback

Không rollback tự ý.

## Cách restore database

1. Xác định đúng file backup database trong thư mục backup cuối.
2. Dừng thao tác mới trên hệ thống.
3. Restore lại database từ bản backup gần nhất.
4. Kiểm tra lại đăng nhập và dữ liệu sau restore.

## Cách restore filestore

1. Xác định đúng file backup filestore trong thư mục backup cuối.
2. Restore lại filestore đúng database tương ứng.
3. Kiểm tra lại tài liệu đính kèm, log, và dữ liệu liên quan sau restore.

## Cách restore addon

1. Xác định đúng bản backup addon `ming_customer_care`.
2. Chép lại addon từ thư mục backup về addons path đang dùng.
3. Restart Odoo nếu cần để nạp lại source addon.
4. Kiểm tra lại menu và màn hình chính sau restore.

## Quy tắc khi rollback hoặc test lại

- Không rollback nếu chưa có người duyệt
- Luôn giữ `safe mode ON` khi restore hoặc test lại
- Không bật SMS thật
- Không bật email thật
- Không bật Lark thật
- Sau restore phải kiểm tra lại đăng nhập, dashboard, task, cảnh báo và lịch sử CSKH
