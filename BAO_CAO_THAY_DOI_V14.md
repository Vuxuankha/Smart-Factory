# Báo cáo thay đổi V14 — Người gửi / người nhận

## Phạm vi
- Sắp xếp **cả người gửi và người nhận** ở tên thư mục khi tải mới. Có 3 chế độ chọn từ giao diện.
- Lấy tên hiển thị từ header From/To của thư (dùng địa chỉ email nếu không có tên), lưu To/Cc đầy đủ trong metadata và CSV.
- Nếu To chứa nhiều người nhận, tên thư mục dùng người đầu tiên và số lượng người còn lại.
- File `email_sap_xep_nguoi_gui_nguoi_nhan.csv` cung cấp bảng đã sắp xếp; ứng dụng không xóa hoặc đổi tên bản cũ.

## Bảo vệ dữ liệu
- Mỗi email được định danh bởi tài khoản, tên hộp thư, UIDVALIDITY, UID.
- Khi đổi cách sắp xếp, UID hợp lệ đã sao lưu ở V13 vẫn được kiểm tra SHA-256 và bỏ qua; không tải/ghi trùng.
- Tên đường dẫn giới hạn số đơn vị UTF-16, luôn giữ hậu tố UID; tên dài được rút gọn riêng người gửi, người nhận và tiêu đề.
- Không lưu mật khẩu và không thay đổi trạng thái email IMAP.

## Thử nghiệm
- Chạy `KIEM_TRA_MA_NGUON.bat` trên Windows có Python và openpyxl. Test V9-V14 bao gồm 33 trường hợp IMAP giả lập.
- Không thể kiểm tra đóng gói EXE Windows hoặc kết nối tài khoản Alibaba Mail thật trong môi trường này.

## Lưu ý
- Nếu bản V13 đã hoàn tất và còn nguyên vẹn, V14 không tự đổi tên thư mục cũ. CSV mới vẫn điền các cột người gửi/người nhận từ header .eml cũ.
- Mã nguồn dùng trình phân tích email của Python; tên hiển thị lấy đúng theo From/To, không tra danh bạ bên ngoài.
