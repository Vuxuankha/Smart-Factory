# Alibaba Operations Center V16.0.13 — Hướng dẫn vận hành và tài khoản

## 1. Các thay đổi chính

- **Đăng nhập riêng cho ứng dụng**: tài khoản này dùng mở các phân hệ vận hành, **không phải** tài khoản Alibaba Mail/IMAP/SMTP.
- **Đăng ký người dùng**: tài khoản đầu tiên trên máy được tạo ở vai trò Quản trị IT để khởi tạo hệ thống. Sau đó, các tài khoản tự đăng ký luôn ở trạng thái chờ phê duyệt.
- **Quản lý người dùng** (Quản trị IT): duyệt thành Nhân viên, Kiểm toán viên hoặc Quản trị IT; vô hiệu hóa người dùng; xem nhật ký tài khoản. Quyền tác vụ được kiểm tra khi mở và khi bấm nút nghiệp vụ trong IT/PMC.
- **Đổi mật khẩu ứng dụng, đăng xuất**: trong menu **Chức năng → Công cụ** hoặc nút đăng xuất ở góc trên. Không cho đăng xuất khi còn tác vụ chạy.
- **Kiểm tra mạng/máy tính không cần mật khẩu mail**. Chức năng này chỉ kiểm tra dung lượng ổ đĩa, DNS và kết nối TCP IMAP (không đăng nhập); có thể truy cập bằng nút **Kiểm tra mạng/DNS**.
- **Mật khẩu hộp thư** chỉ được hỏi khi có thao tác IMAP thực sự: sao lưu, kiểm tra IMAP, xem quota một hộp thư. Mật khẩu IMAP không được lưu vào cơ sở dữ liệu người dùng của ứng dụng.
- Giao diện dashboard tối: cột trái điều hướng, trung tâm thao tác chính, cột phải trạng thái/đường tắt, log thu gọn ở đáy; KPI CPU/RAM/ổ đĩa đọc từ máy thật.
- Trên màn hình nhỏ, phần giữa có thanh cuộn, nút BẮT ĐẦU hiện phía trên biểu đồ, không còn lệ thuộc chiều cao màn hình.

## 2. Chạy trên Windows 10/11

**Chạy mã nguồn**: cài Python 3.10+ và `openpyxl` (tùy chọn `psutil` để có CPU/RAM), rồi chạy `CHAY_THU_WINDOWS.bat`. Giải nén toàn bộ ZIP trước khi chạy.

**Đóng gói EXE không hiện CMD**: chạy `TAO_EXE_WINDOWS.bat` trên Windows có Internet. Kết quả dự kiến ở `dist/AlibabaOperationsCenter.exe`. File thực thi `console=False`; đây mới là cấu hình build, **chưa được biên dịch hoặc kiểm thử trên Windows thực tế trong phiên rà soát này**.

Hệ thống thông tin tài khoản ứng dụng lưu trong `%LOCALAPPDATA%\AlibabaOperationsCenter\accounts.sqlite3`. Không xóa/move file này nếu vẫn cần giữ tài khoản. Đây là DB **cục bộ cho một tài khoản Windows/máy**; không phải AD, LDAP, SSO hoặc máy chủ danh tính doanh nghiệp.

### Khởi chạy lần đầu

1. Tạo một tài khoản Quản trị IT mới trong màn hình khởi tạo. **Không nhập mật khẩu email**.
2. Đăng nhập vào giao diện chính, kiểm tra sidebar và các nút tác vụ.
3. Người dùng khác chọn **Đăng ký tài khoản mới**. Tài khoản mới sẽ ở trạng thái *chờ duyệt*.
4. Quản trị viên IT vào **Quản lý người dùng** để phê duyệt và cấp vai trò thích hợp.
5. Người dùng đăng nhập bằng tên và mật khẩu ứng dụng. Các phần IT, PMC, Mạng tùy vai trò sẽ mở mà không cần mật khẩu email.
6. Để sao lưu một hộp thư, nhập địa chỉ trong khu vực Bước 1, chọn thư mục rồi **Bắt đầu sao lưu**; lúc này mới nhập mật khẩu **EMAIL/IMAP** tương ứng.

### Vai trò

| Vai trò | Được truy cập trong giao diện |
|---|---|
| Nhân viên | Email & sao lưu, PMC, kiểm tra mạng/máy ở chế độ chỉ đọc |
| Quản trị IT | Toàn bộ nhóm Mail, Mạng, Hạ tầng IT, PMC, quản lý người dùng và nhật ký xác thực |
| Kiểm toán viên | Xem báo cáo & nhật ký, kiểm tra hệ thống; không sửa mạng, hạ tầng hoặc PMC |

**Cảnh báo về bảo mật**: RBAC này bảo vệ quy trình trong giao diện ứng dụng cục bộ, không thay thế quyền NTFS, quyền Windows Administrator, chính sách ERP, quyền máy chủ SMTP/IMAP, quản trị dữ liệu nhiều máy hoặc phân quyền được xác thực từ máy chủ. Người có quyền quản trị thiết bị vẫn có thể can thiệp trực tiếp vào file dữ liệu nội bộ. Dữ liệu quản trị doanh nghiệp nên đặt trong máy chủ tập trung nếu cần RBAC chống giả mạo đầy đủ.

### Mật khẩu và lịch sử

- Mật khẩu ứng dụng được kiểm tra bằng `scrypt` và muối riêng cho mỗi tài khoản; không lưu mật khẩu gốc.
- Chính sách tạo mới: ít nhất 12 ký tự, có chữ và số; tài khoản bị tạm khóa 15 phút sau 5 lần xác thực sai liên tiếp.
- Ghi nhật ký đăng ký, đăng nhập, sai mật khẩu, phê duyệt/khóa tài khoản và đổi mật khẩu. **Không** ghi mật khẩu vào nhật ký.
- Chưa có tự khôi phục tài khoản admin hoặc đồng bộ giữa các máy. Lưu bản sao an toàn của DB tài khoản; thử phục hồi trước khi sử dụng trong vận hành sản xuất.

## 3. Giới hạn kiểm thử

- Bộ kiểm thử tự động chạy thành công trong Linux/Xvfb, bao gồm GUI mô phỏng, các module cũ và phần auth mới. Tham khảo `BAO_CAO_RASOAT_45_VAN_DE_V16_0_13.md`.
- Chưa đăng nhập IMAP Alibaba thật, chưa kết nối AD, Digiwin, NAS thực, chưa kiểm tra Windows Defender, DPI 125–150% hay đóng gói EXE trên Windows thật.
- Đồ thị CPU sử dụng số đo thực tế của `psutil`. Nếu chưa có thư viện này, CPU/RAM hiện `N/A`, không sử dụng số liệu minh họa.
- Ứng dụng vẫn giữ những chức năng PMC/IT ở chế độ cục bộ hoặc bán tự động từ phiên bản trước; phiên bản này không biến các tích hợp chưa hoàn thành thành tác vụ thực thi trên hạ tầng nhà máy.
- Trước khi cập nhật ở máy đang dùng, **sao lưu thư mục dữ liệu cũ** và thử ZIP mới tại thư mục riêng. Không chuyển đổi/ghi đè dữ liệu sản xuất thật trong lần dùng đầu.
