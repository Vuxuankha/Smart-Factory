# Kết quả kiểm thử V14 — Tên người gửi / người nhận

Ngày chạy: 2026-10-19.

## Kết quả đã kiểm chứng
- Biên dịch cú pháp các file nguồn: thành công (`python -m py_compile`).
- Chạy toàn bộ bài kiểm thử V9–V14: **33/33 đạt** trong Python 3.13, hộp thư IMAP **giả lập**, không truy cập tài khoản thật.
- Nhóm 7 bài kiểm thử V14: giải mã tên tiếng Việt/Trung và nhiều người nhận; sắp xếp ngày trước / người gửi trước; chế độ V13; đọc header From/To của bản lưu V13; giới hạn độ dài đường dẫn và UID; xử lý thiếu header; CSV sắp xếp và chống Excel formula injection.
- Kiểm tra `python app.py --self-test`: **đạt** (đọc/ghi tệp và SHA-256 tại máy phát triển).
- Smoke test khởi tạo cửa sổ Tk qua màn hình ảo Xvfb: **đạt**, 3 lựa chọn sắp xếp hiển thị.

## Giới hạn
- **Chưa đóng gói hoặc chạy EXE trên Windows thật.** BAT và file spec được chuẩn bị để tạo bản Windows với PyInstaller trên máy Windows của người dùng.
- **Chưa kết nối với tài khoản Alibaba Mail thật.** Không thể đảm bảo mọi biến thể header/IMAP thực tế sẽ thành công.
- Việc xử lý email/tệp đính kèm rất lớn vẫn có thể chiếm nhiều RAM như bản V13.
- Chức năng đổi tên thư mục email **đã lưu từ trước** không được tự động hóa nhằm tránh gây ghi đè hay mất dữ liệu.

## Kiểm thử thủ công sau khi build trên Windows
1. `TAO_EXE_WINDOWS.bat`, kiểm tra file `BUILD_V14.log` và kết quả `--self-test`.
2. Sao lưu thử một hộp thư có ít email và cả thư gửi/nhận; kiểm tra tên thư mục chứa `GUI-` và `NHAN-`.
3. Kiểm tra file `metadata.json` có danh sách `recipients` và `cc`, và CSV `_BAO_CAO_LOI/email_sap_xep_nguoi_gui_nguoi_nhan.csv` có đúng cột tên.
4. Chạy lại với kiểu sắp xếp khác, xác nhận email có SHA-256 hợp lệ **không tải lại/không lưu trùng**.
5. Đối chiếu số UID máy chủ và số UID xử lý (`loi=0`).
