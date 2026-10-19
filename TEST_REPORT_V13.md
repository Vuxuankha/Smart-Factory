# Kết quả kiểm thử Sao Lưu Alibaba Mail V13

**Môi trường chạy kiểm thử:** Linux sandbox, Python 3.13, mock IMAP **không có thông tin đăng nhập thật**.

**Đã kiểm tra:**

- Cú pháp Python và import module.
- Báo cáo `--self-test` không cần mạng.
- Danh sách UID snapshot duy nhất trước khi tải với 1/2/3 worker.
- Đồng bộ Inbox/Sent/Trash bằng fake server; không đánh dấu mail là đã đọc.
- Mất socket/SSL giả lập và thử tải lại.
- Từ chối tiếp tục nếu UIDVALIDITY bị thay đổi.
- Chỉ bỏ qua bản lưu SHA-256 hợp lệ; thiếu file tệp đính kèm tự tải lại.
- Tên file dài UTF-8 tiếng Việt/Trung, giữ UID và đuôi, chống trùng.
- Ghi nguyên tử, bản ghi cũ nguyên vẹn nếu thay thế thất bại.
- Nhận biết sai lệch `RFC822.SIZE` và báo lỗi UID, không đánh dấu hoàn tất.
- Danh sách CSV hơn 3000 dòng, không bị mất dữ liệu; chống công thức CSV.
- Report SQLite/Excel/CSV; không rò rỉ kết nối SQLite trong unit test.

**Chưa thực hiện / chưa có chứng cứ:**

- Kết nối Alibaba Mail thực tế với IMAP của doanh nghiệp.
- Tạo và mở file `.exe` trên Windows sạch chưa có Python.
- Kiểm thử tải nhiều GB và tệp đính kèm hàng trăm MB.
- Kiểm toán bảo mật độc lập, mã hóa bản sao lưu, ký số EXE.
- Xác minh toàn bộ 400 tuyên bố của tester bằng tình huống tái hiện cụ thể.

**Quy tắc phát hành:** Chưa nên triển khai hàng loạt trước khi thử trên tài khoản ít thư, đối chiếu bản lưu với máy chủ và chạy EXE trên máy khác.
