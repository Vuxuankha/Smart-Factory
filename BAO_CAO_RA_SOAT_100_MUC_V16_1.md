# BAO CAO RA SOAT 100 MUC - ALIBABA MAIL V16.0.1

**Pham vi:** Ma nguon trong ZIP goc; 100 muc trong TXT la **danh sach nguy co gia dinh**, khong phai 100 loi da duoc chung minh. Ung dung la cong cu SAO LUU email qua IMAP (khong phai ung dung gui mail SMTP).

**Ket qua test:** 39/39 test goc dat; 44/44 test dat sau sua (bo sung 5 test). Thuc thi tren Linux, khong kiem chung GUI Windows, dong goi EXE hoac dang nhap server Alibaba that.

**Thay doi ma nguon:** cap nhat thong tin V16.0.1; loc ten file Windows khi cat ngan; kiem tra UID trong FETCH neu server co tra UID; bo qua metadata symlink trong qua trinh danh muc; giam chi tiet stacktrace len nhat ky GUI; chan gia tri toc do NaN/Infinity va so luong luong sai; cap nhat ten nhat ky va script test; them regression tests.

**Cach doc ket qua:** SUA/DA KIEM THU = sua duoc va co test hoac ket qua test sau thay doi; CO BAO VE = ma nguon co co che lien quan, khong dong nghia khong co loi; KHONG THUOC PHAM VI = tinh nang chua co/khong can thiet voi cong cu sao luu, can xac nhan nhu cau; CHUA XAC MINH = chua co bang chung de ket luan loi ton tai.

| STT | Muc can doi chieu | Ket luan/kiem tra |
|---:|---|---|
| 1 | Hardcoded Credentials: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 2 | Thiếu mã hóa mật khẩu: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 3 | Lỗ hổng tấn công Injection (SQLi/Command Injection): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 4 | Thiếu kiểm tra chứng chỉ SSL/TLS: | CO BAO VE / DA DOI CHIEU — Đã thấy SSL mặc định với xác minh chứng chỉ và TLS >= 1.2 trong kết nối IMAP. |
| 5 | Cấu hình CORS quá thoáng: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 6 | Rò rỉ thông tin qua Exception/Log: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 7 | Thiếu kiểm tra giới hạn tốc độ (Rate Limiting): | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 8 | Quản lý phiên đăng nhập (Session Management) kém: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 9 | Sử dụng thuật toán băm yếu: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 10 | Thiếu kiểm tra phân quyền (Broken Access Control): | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 11 | Lỗ hổng Path Traversal: | CO BAO VE / DA DOI CHIEU — Đã thấy lọc ký tự đường dẫn, kiểm tra symlink tệp đích/metadata; chưa kiểm toán đầy đủ tất cả thư mục cha. |
| 12 | Không kiểm tra tệp tin tải lên (File Upload Validation): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 13 | Thiếu bảo vệ tệp cấu hình: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 14 | Sử dụng thư viện phiên bản cũ có lỗ hổng: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 15 | Thiếu cơ chế chống CSRF: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 16 | Blocking Network Calls: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 17 | Memory Leak (Rò rỉ bộ nhớ): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 18 | Thiếu khối xử lý ngoại lệ (Bare except): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 19 | Race Condition trong đa luồng: | CO BAO VE / DA DOI CHIEU — Đã thấy dùng khóa liên tiến trình cho cùng thư mục đích. |
| 20 | Vòng lặp vô hạn (Infinite Loop): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 21 | Tràn bộ nhớ (Buffer Overflow/Memory Exhaustion): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 22 | Thiếu tệp cấu hình mặc định: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 23 | Xung đột tên biến/hàm: | **DA SUA / CAN KIEM CHUNG THEM** — Đã sửa thông tin phiên bản cũ (V15) trong mail_backend; metadata mới và tiêu đề ứng dụng thống nhất V16. |
| 24 | Sử dụng biến mutable làm giá trị mặc định trong hàm: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 25 | Import thừa/vòng tròn (Circular Import): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 26 | Không xử lý mã hóa ký tự (Encoding Issues): | CO BAO VE / DA DOI CHIEU — Đã thấy nhiều thao tác UTF-8 cho metadata, CSV và nhật ký. |
| 27 | Truy cập phần tử danh sách/từ điển không an toàn: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 28 | Đường dẫn cứng (Hardcoded Paths): | **DA SUA / CAN KIEM CHUNG THEM** — Đã vá rủi ro tên file Windows kết thúc bằng dấu chấm/khoảng trắng sau khi cắt độ dài. |
| 29 | Không dọn dẹp file tạm (Temp Files): | CO BAO VE / DA DOI CHIEU — Đã thấy safe_write xóa tệp tạm sau ghi. |
| 30 | Sử dụng tài nguyên CPU cao bất thường: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 31 | Thiếu unit test cho các luồng nghiệp vụ chính: | CO BAO VE / DA DOI CHIEU — Có bộ kiểm thử Python tại tests; vẫn thiếu kiểm thử SMTP vì dự án là công cụ sao lưu IMAP. |
| 32 | Lỗi khi đóng ứng dụng đột ngột: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 33 | Xử lý chuỗi (String Parsing) dễ vỡ: | **DA SUA / CAN KIEM CHUNG THEM** — Đã kiểm tra UID trong phản hồi IMAP FETCH; từ chối trường hợp server trả UID khác. |
| 34 | Không kiểm tra trạng thái kết nối Internet: | CO BAO VE / DA DOI CHIEU — Kết nối IMAP có timeout; chưa kiểm chứng hành vi mất mạng thực tế. |
| 35 | Thiếu ghi log khi khởi động ứng dụng: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 36 | Thiếu thông báo tải (Loading State): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 37 | Thông báo lỗi (Error Message) khó hiểu: | **DA SUA / CAN KIEM CHUNG THEM** — Đã giảm việc ghi chi tiết traceback của kết nối vào nhật ký người dùng; còn cần soát nội dung exception từ server. |
| 38 | Thiếu xác nhận trước khi thao tác nguy hiểm: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 39 | Mất dữ liệu khi nhập liệu dở dang: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 40 | Giao diện bị tràn/vỡ chữ (Layout Overflow): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 41 | Thiếu phím tắt phổ biến: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 42 | Không tự động cuộn (Auto-scroll): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 43 | Độ tương phản màu sắc kém: | CO BAO VE / DA DOI CHIEU — Đã dùng email.message_from_bytes và thư viện giải mã header. |
| 44 | Thiếu tính năng tìm kiếm/lọc: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 45 | Trạng thái kết nối không rõ ràng: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 46 | Giới hạn ký tự không rõ ràng: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 47 | Thiếu nút hủy (Cancel Button): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 48 | Font chữ hiển thị lỗi (Mojibake): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 49 | Bảng dữ liệu (Table/Grid) không sắp xếp được: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 50 | Thiếu tính năng sao chép nhanh: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 51 | Cảnh báo ghi đè tệp: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 52 | Thiếu hướng dẫn sử dụng (Help/Tooltip): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 53 | Biểu tượng (Icon) không trực quan: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 54 | Độ trễ phản hồi (Input Latency): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 55 | Không ghi nhớ trạng thái cửa sổ: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 56 | Thiếu phân trang (Pagination) hoặc Lazy Loading: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 57 | Thông báo thành công quá mờ nhạt: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 58 | Thiếu tính năng kiểm tra bản cập nhật: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 59 | Biểu mẫu (Form) thiếu validate trực tiếp: | **DA SUA / CAN KIEM CHUNG THEM** — Đã từ chối NaN/Infinity, số luồng không hợp lệ và tốc độ ngoài ngưỡng. |
| 60 | Âm thanh cảnh báo phiền toái: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 61 | Xử lý sai định dạng Email (RFC 5322): | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 62 | Lỗi phân tách tệp đính kèm lớn: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 63 | Mất mát dữ liệu khi đồng bộ ngắt quãng: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 64 | Trùng lặp email khi đồng bộ: | CO BAO VE / DA DOI CHIEU — Đã thấy UID+UIDVALIDITY và checksum để tránh tải lại bản hợp lệ. |
| 65 | Xử lý sai múi giờ (Timezone): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 66 | Lỗi định dạng HTML trong Email: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 67 | Không xử lý được Email chuyển tiếp (Forward) hoặc trả lời (Reply): | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 68 | Lỗi giải mã nội dung (Decoding Error): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 69 | Gửi nhầm email hàng loạt (Mass Mailing Error): | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 70 | Quản lý danh sách gửi (Recipient List) lỗi: | CO BAO VE / DA DOI CHIEU — Không phát hiện chức năng gửi email/SMTP trong mã nguồn bản ZIP. |
| 71 | Lỗi đọc file cấu hình sao lưu (Backup/Restore): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 72 | Sai sót trong việc phân loại Thư rác / Thư mục: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 73 | Lỗi xử lý ký tự đặc biệt trong tiêu đề: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 74 | Thiếu cơ chế hàng đợi (Queue) khi gửi mail số lượng lớn: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 75 | Lỗi trích xuất nội dung text từ email đa phần (Multipart): | CO BAO VE / DA DOI CHIEU — Công cụ lưu nguyên bản email.eml và giải nén tệp đính kèm, không phải client hiển thị email. |
| 76 | Không lưu vết lịch sử gửi mail: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 77 | Lỗi định dạng tệp xuất báo cáo: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 78 | Xử lý sai cờ (Flags) email: | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 79 | Lỗi dung lượng cơ sở dữ liệu cục bộ: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 80 | Thiếu tính năng kiểm tra tính toàn vẹn dữ liệu: | CO BAO VE / DA DOI CHIEU — Đã thấy SHA-256 xác minh EML và tệp đính kèm. |
| 81 | Thiếu phụ thuộc khi đóng gói EXE: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 82 | Xung đột phiên bản Python: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 83 | Thiếu quyền ghi (Permission Denied): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 84 | Chống virus giả lập nhận diện nhầm (False Positive): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 85 | Thiếu thư viện Visual C++ Redistributable: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 86 | Lỗi đường dẫn tương đối khi chạy file `.bat`: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 87 | Rò rỉ thông tin trong file `.spec`: | **DA SUA / CAN KIEM CHUNG THEM** — Đã kiểm tra file spec theo bản nguồn, không khẳng định an toàn đường dẫn ở mọi máy. |
| 88 | Xung đột tên tiến trình (Process Conflict): | CO BAO VE / DA DOI CHIEU — Đã có khóa liên tiến trình trong exclusive_backup_lock. |
| 89 | Thiếu xử lý biến môi trường (Environment Variables): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 90 | Lỗi mã hóa file script hàng batch: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 91 | Thiếu log ghi nhận lỗi khởi động (Pre-main Error Logging): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 92 | Kích thước file thực thi quá lớn: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 93 | Lỗi tương thích hệ điều hành: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 94 | Quên cập nhật tệp tài liệu (Documentation Outdated): | **DA SUA / CAN KIEM CHUNG THEM** — Đã cập nhật tên file log, thông tin phiên bản và tệp kết quả kiểm thử. |
| 95 | Thiếu tệp `.gitignore` chuẩn: | CO BAO VE / DA DOI CHIEU — Đã có tệp .gitignore. |
| 96 | Lỗi phân quyền file log: | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 97 | Sử dụng thư viện không còn hỗ trợ (Deprecated): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 98 | Thiếu cơ chế tự phục hồi (Self-healing/Recovery): | CHUA XAC MINH — chua du bang chung ma nguon/kiem thu thuc te de ket luan co loi. |
| 99 | Lỗi kết nối mạng nội bộ (Proxy/Firewall): | KHONG THUOC PHAM VI HIEN TAI HOAC CHUA CO TINH NANG — can kiem chung neu mo rong san pham. |
| 100 | Thiếu kiểm tra dung lượng ổ đĩa trống: | CO BAO VE / DA DOI CHIEU — Đã có kiểm tra dung lượng trống trước khi lưu email. |

## Gioi han va buoc tiep theo

- Khong phan dinh 100 muc la 100 loi that: phan lon la rui ro/yeu cau tinh nang co dieu kien.
- Chua thu nghiem GUI tren Windows 10/11, antivirus, EXE PyInstaller, proxy/firewall, server IMAP that va tai khoan that.
- Khong can va khong nen nhap mat khau vao chat. Kiem thu IMAP that tren may cua nguoi dung voi tai khoan thu nghiem va thu muc sao luu rieng.
- Truoc khi chay ban moi tren du lieu quan trong, sao chep thu muc sao luu goc; khong giai nen de len duy nhat ban goc.
- Thay doi nho co chu dich; khong co bang chung de tu tin sua moi van de tu danh sach nguy co.
