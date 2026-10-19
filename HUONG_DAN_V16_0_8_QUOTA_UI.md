# Alibaba Operations Center V16.0.8 — Hướng dẫn & phạm vi triển khai

## Đã có mã nguồn hoạt động

- `Email / Sao lưu -> Dung lượng hộp thư (IMAP QUOTA)` hoặc mục `02 Dung lượng Email` trong sidebar.
- Hỏi mật khẩu từng hộp thư lúc kiểm tra. Không ghi mật khẩu ra báo cáo hay tệp cấu hình.
- Kết nối SSL tới máy chủ IMAP (mặc định `imap.qiye.aliyun.com:993`), đọc CAPABILITY và thử GETQUOTAROOT INBOX nếu hỗ trợ QUOTA.
- Hiện số bytes đã dùng / hạn mức / còn lại, tỷ lệ sử dụng; trạng thái UNSUPPORTED/DENIED/UNKNOWN khi máy chủ không cấp thông tin.
- Tập hợp kết quả hộp thư người dùng được cấp quyền đăng nhập, xuất CSV UTF-8 để mở trong Excel; không ghi đè tệp báo cáo cũ.
- Sidebar thu gọn/mở rộng, ngăn log ẩn/hiện; màu sidebar #0F172A, màu thao tác chính #3B82F6, màu trạng thái #10B981.
- Giữ lại các tác vụ Email backup, mạng IP/VPN, hạ tầng CNTT, PMC trước đây.

## Quy trình kiểm tra

1. Chạy `CHAY_THU_WINDOWS.bat` trên Windows có Python/phụ thuộc tương ứng.
2. Mở `Email / Sao lưu -> Dung lượng hộp thư`.
3. Nhập email của hộp thư được phép kiểm tra; nhập mật khẩu hoặc app password khi cửa sổ yêu cầu.
4. Nếu hiện `OK`, kiểm tra cột đã dùng/hạn mức/còn lại. Nếu `UNSUPPORTED`, `DENIED` hoặc `UNKNOWN`, dùng bản xuất báo cáo dung lượng từ trang quản trị Alibaba Mail.
5. Nhấn `Xuất kết quả CSV` để lưu. Không gửi mật khẩu cho người khác.

## Các hạng mục trong danh sách nâng cấp chưa được triển khai trong V16.0.8

- Tag/chip input, hệ phân quyền RBAC có xác thực thực sự, mã hóa credential AES-256 có quản lý khóa an toàn.
- Slider điều khiển tốc độ, tiến độ tổng thể xác thực theo % và ETA; topology đồ họa mạng, dashboard thời gian thực, tác vụ lịch nền và bảo trì máy.
- Tích hợp Telegram/Zalo ZNS, trợ lý AI gọi dịch vụ bên ngoài, executive infographic tự động.
- Eco Mode 24/7, system tray, global hotkeys, OTA tự cập nhật, thay đổi dark/light mode trực tiếp.

Những hạng mục trên đòi hỏi thiết kế lại sâu, quyền truy cập nhà máy/API, kho bí mật và kiểm thử Windows thực tế. KHÔNG nên đưa vào giao diện như chức năng đang chạy khi chưa có backend.

## Kiểm thử

Chạy: `python -m unittest discover -s tests -q` (trên Linux có giao diện dùng `xvfb-run -a`).
86/86 bài kiểm thử đã đạt trong môi trường xây dựng, bao gồm 5 bài kiểm thử IMAP QUOTA mới. **Chưa xác minh với máy chủ Alibaba Mail thực hoặc Windows của người dùng**, nên QUOTA có thể không được server cho phép.
