# Báo cáo rà soát — 45 điểm lỗi, rủi ro và khoảng trống tính năng được xử lý

**Cơ sở rà soát**: mã nguồn V16.0.12 và phản hồi người dùng kèm ảnh UI. Phân biệt 3 mức: `LỖI` = hành vi sai/không ổn định có thể kiểm tra từ mã nguồn; `RỦI RO` = điểm yếu có thể gây lỗi hoặc vượt quyền; `BỔ SUNG` = chức năng/UX còn thiếu theo yêu cầu. **Không coi 45 mục dưới đây là 45 lỗi runtime đã tái hiện trên máy Windows thực tế.**

| STT | Loại | Vấn đề trước nâng cấp → xử lý V16.0.13 |
|---:|---|---|
| 01 | LỖI | Kiểm tra máy yêu cầu địa chỉ email dù chỉ muốn xem trạng thái mạng → tách kiểm tra máy/mạng độc lập |
| 02 | LỖI | Kiểm tra máy yêu cầu mật khẩu IMAP không liên quan → bỏ toàn bộ lời nhắc mail trong chẩn đoán cục bộ |
| 03 | LỖI | Chế độ nhiều hộp thư khiến nút chẩn đoán buộc chuyển sang Nhân viên → bỏ phụ thuộc chế độ email |
| 04 | LỖI | Cờ dừng tác vụ cũ có thể bỏ qua bước kiểm tra mạng tiếp theo → đặt lại cờ khi bắt đầu chẩn đoán |
| 05 | RỦI RO | Tiến trình chẩn đoán đọc `StringVar` từ worker thread → chụp đường dẫn từ luồng Tk trước khi chạy |
| 06 | RỦI RO | Worker quản lý mạng dùng `root.after` trực tiếp từ luồng khác → chuyển qua queue tới luồng giao diện |
| 07 | LỖI | Callback `after` còn tồn tại khi root bị hủy → quản lý và hủy callback theo vòng đời |
| 08 | LỖI | Callback quét LAN có thể chạy sau khi cửa sổ Hạ tầng bị đóng → hủy lịch cập nhật khi Destroy |
| 09 | LỖI | Mở PMC liên tiếp tạo nhiều cửa sổ trùng, dễ thao tác nhầm → dùng lại cửa sổ đang mở |
| 10 | LỖI | Mở Hạ tầng liên tiếp tạo cửa sổ trùng → dùng lại cửa sổ đang mở |
| 11 | LỖI | Mở quản lý Mạng/VPN liên tiếp tạo cửa sổ trùng → dùng lại cửa sổ đang mở |
| 12 | LỖI | Cửa sổ Hạ tầng không giữ tham chiếu notebook để đổi tab khi mở lại → lưu tham chiếu notebook |
| 13 | LỖI | Bảng quét mạng có scrollbar nhưng không đồng bộ chiều cuộn (`yscrollcommand`) → nối đồng bộ |
| 14 | LỖI | Kết quả lượt quét trước có thể được xuất trong khi quét mới → làm mới danh sách kết quả ở đầu lượt quét |
| 15 | LỖI | Xuất danh sách LAN trùng tên chỉ gây ngoại lệ không giải thích → thông báo chọn tên khác, không ghi đè |
| 16 | RỦI RO | Console Hạ tầng nối chuỗi vô hạn gây tăng RAM khi giám sát lâu → giới hạn và cắt bớt 1.000 dòng |
| 17 | LỖI | Xuất CSV danh sách email dùng copy ghi đè báo cáo có sẵn → dùng chế độ tạo tệp mới `xb` |
| 18 | LỖI | Chạy menu Dashboard tối nhưng thanh menu hệ thống màu xám lệch phong cách → đưa menu vào header tối |
| 19 | LỖI | Cửa sổ cố định quá lớn khiến UI bị khuất trên màn hình thấp → giới hạn kích thước theo màn hình |
| 20 | LỖI | Nội dung trung tâm cao hơn viewport không có cuộn dọc → thêm vùng cuộn đúng kích thước |
| 21 | LỖI | Ngăn console bị mất dưới phần nội dung `pack(expand=True)` → cố định thanh drawer dưới cùng |
| 22 | LỖI | Biểu đồ CPU ở đầu khiến nút sao lưu nằm dưới màn hình nhỏ → đưa bước chọn mail và Bắt đầu lên trước |
| 23 | BỔ SUNG | Thiếu thẻ KPI CPU/RAM/đĩa theo dõi dễ nhìn → bốn thẻ số liệu trạng thái theo máy thật |
| 24 | BỔ SUNG | Thiếu biểu đồ hoạt động không dùng số mẫu giả → đồ thị CPU bằng dữ liệu `psutil` theo thời gian |
| 25 | BỔ SUNG | Giao diện các cửa sổ phụ lẫn màu sáng/tối → hệ thống style chung tối cho Treeview, Notebook, Form |
| 26 | BỔ SUNG | Chưa hiển thị rõ người đang đăng nhập & vai trò → thêm danh tính phiên vào header |
| 27 | BỔ SUNG | Không có tài khoản đăng nhập ứng dụng riêng → tạo đăng nhập cục bộ tách khỏi IMAP |
| 28 | BỔ SUNG | Không có đăng ký tài khoản ứng dụng → có màn hình đăng ký và thiết lập đầu tiên |
| 29 | RỦI RO | Không có ranh giới quyền Quản trị IT/nhân viên/kiểm toán → định nghĩa vai trò và chặn lối vào UI |
| 30 | RỦI RO | Người dùng đăng ký mới có thể cần người duyệt thay vì cấp quyền ngay → luồng chờ phê duyệt |
| 31 | BỔ SUNG | Thiếu công cụ phê duyệt người dùng → trang quản lý và duyệt vai trò |
| 32 | RỦI RO | Nếu quản lý mật khẩu ứng dụng bằng văn bản thuần sẽ lộ dữ liệu → sử dụng băm `scrypt` + muối cá nhân |
| 33 | RỦI RO | Thiếu quy tắc mật khẩu → kiểm tra độ dài, chữ/số, ký tự điều khiển và giới hạn kích thước |
| 34 | RỦI RO | Thiếu kiểm tra tên tài khoản trùng do hoa/thường → chuẩn hóa `casefold` và ràng buộc UNIQUE |
| 35 | RỦI RO | Không hạn chế thử sai mật khẩu → đếm số lần sai và khóa 15 phút sau 5 lần |
| 36 | RỦI RO | Số lần đăng nhập sai không được bảo toàn khi phát sinh ngoại lệ → commit trước khi trả lỗi xác thực |
| 37 | RỦI RO | Tự vô hiệu hóa tài khoản quản trị đang dùng sẽ khóa người quản lý → từ chối tự khóa |
| 38 | RỦI RO | Có thể hạ quyền quản trị viên cuối cùng khi phê duyệt lại → chặn tự hạ quyền và mất admin cuối |
| 39 | BỔ SUNG | Không có đăng xuất ứng dụng → đăng xuất, hủy phiên cũ và yêu cầu đăng nhập lại |
| 40 | BỔ SUNG | Không có đổi mật khẩu ứng dụng → yêu cầu mật khẩu hiện tại để đổi |
| 41 | RỦI RO | Quyền có thể bị đổi nhưng cửa sổ nghiệp vụ cũ vẫn đang mở → kiểm tra quyền tại lúc nhấn các nút IT/PMC |
| 42 | RỦI RO | Tài khoản khóa/đổi vai trò vẫn dùng quyền trong phiên hiện tại → xác nhận lại vai trò/active từ DB khi thao tác |
| 43 | BỔ SUNG | Thiếu audit đăng ký/đăng nhập/phê duyệt → lưu nhật ký sự kiện không chứa mật khẩu và màn hình xem |
| 44 | RỦI RO | File tài khoản nếu lưu chung mã nguồn/backup có thể lộ/ghi đè → lưu độc lập trong thư mục dữ liệu người dùng, đặt quyền file riêng khi POSIX hỗ trợ |
| 45 | LỖI | Hộp thoại bắt đầu sao lưu gọi mật khẩu email là “mật khẩu ứng dụng” gây nhầm → đổi thành “mật khẩu EMAIL / app password IMAP” |

## Kiểm thử

- Chạy `python -m unittest discover -s tests -p 'test_*.py'` trong `xvfb-run` (Linux): **183/183 đạt** ở lần kiểm tra sau tích hợp.
- Có **80 bài kiểm thử mới** về xác thực ứng dụng và giao diện (103 bài cũ); gồm đăng ký, phân quyền, chống đăng nhập thử liên tục, thay mật khẩu, không yêu cầu mật khẩu mail khi vào PMC/IT/chẩn đoán và bố cục responsive.
- Chạy `python app.py --self-test`: **đạt**, xác nhận đọc/ghi cục bộ, SHA-256, SQLite và luồng khởi tạo tài khoản.
- Chụp trực tiếp cửa sổ qua màn hình ảo 1366×768 và 1600×1024 để quan sát vị trí nút điều khiển và console.

## Những gì chưa được xác nhận

- **Không** khẳng định không còn bất kỳ lỗi nào hoặc đã kiểm thử 40 sự cố trên máy của người dùng.
- Chưa thử end-to-end trên Windows 10/11, DPI 125/150%, IMAP Alibaba thật, LAN/camera thật, ERP thật, hoặc EXE đã build.
- RBAC là bộ lọc thao tác giao diện *trên máy cục bộ*, không đủ thay thế phân quyền server-side cho nhà máy nhiều người/máy.
- Các nhóm PMC/IT chưa kết nối ERP/AD/Zalo/API vẫn mang giới hạn kế thừa; bản này không thêm tích hợp backend chưa được xác thực.
