# V16.0.6 - Sửa lỗi giao diện và thao tác menu

## Sửa lỗi xác nhận

1. Chế độ **Quản trị viên** không hiển thị ổn định vì dùng `pack(before=self.single_frame)` sau khi đã `pack_forget()` khung đăng nhập. Hai chế độ nay dùng chung một vùng hiển thị ổn định; khi chọn Quản trị viên sẽ thấy ô nhập **danh sách email (mỗi dòng một tài khoản)**. Nếu Nhân viên đã có email, ứng dụng điền trước tài khoản ấy vào danh sách (chỉ khi danh sách đang trống). Khi quay lại Nhân viên, email nhập trước không bị mất.
2. PMC và Hạ tầng gọi các đối tượng Tkinter (StringVar, widget, `after`) từ luồng nền. Đây là luồng không an toàn cho Tkinter. Các thao tác cục bộ hiện chạy trực tiếp trên luồng giao diện và hiển thị kết quả/lỗi ngay trong cửa sổ. Thao tác mạng có thể khiến giao diện đợi cho đến khi kiểm tra xong; tối ưu tiếp cần mô hình chụp giá trị đầu vào ở UI rồi chạy worker.
3. PMC có 21 tab quá dài để tìm trên màn hình nhỏ. Đã thêm danh sách thả xuống **Chọn chức năng**, và vẫn giữ nhóm PP/MC/BC/Kỹ thuật cũ.

## Hướng dẫn thử trên Windows

- Chạy `CHAY_THU_WINDOWS.bat` hoặc `python app.py` trên máy có Python, đúng thư mục ứng dụng.
- Ở **Email / Sao lưu**, chọn **Quản trị viên** để hiện vùng nhập nhiều email, mỗi dòng một địa chỉ. Mật khẩu từng địa chỉ sẽ được hỏi khi bấm **Bắt đầu sao lưu**; không thể dùng quyền admin để đọc tự động thư của người khác nếu không có thông tin xác thực/quyền hợp lệ.
- Chọn **PMC > II. MC > MRP & cảnh báo thiếu**. Dữ liệu để có kết quả phải nhập trước: đơn hàng, BOM và tồn kho. Có thể dùng nút **Nhập CSV** trong từng mục.
- Chọn **Hạ tầng CNTT > IT Helpdesk** để tạo ticket cục bộ hoặc **Giám sát** để thêm một IP/host rồi kiểm tra TCP. Những chức năng phụ thuộc AD, máy chủ DHCP, Digiwin/SAP, Telegram, Zalo, cấu hình mạng và quyền truy cập thực tế không thể hoạt động hoàn chỉnh khi chưa cấu hình kết nối.
- Các thao tác thay đổi kho hoặc xuất lệnh chỉ ảnh hưởng **CSDL PMC cục bộ**, không ghi tự động vào ERP. Hãy thử với dữ liệu mẫu trước.

## Kiểm thử

- Tổng cộng **81 bài kiểm thử**, gồm **2 bài giao diện mới** chạy qua Xvfb (Tkinter).
- Kết quả: **81/81 đạt** trên môi trường Linux; chưa kiểm thử trực tiếp trên máy Windows của người dùng và chưa đóng gói EXE.

## Bảo toàn dữ liệu

- Không thay đổi schema CSDL PMC, cấu trúc thư mục sao lưu mail hay thuật toán IMAP.
- Không chuyển hoặc ghi lại mật khẩu lên ổ cứng.
