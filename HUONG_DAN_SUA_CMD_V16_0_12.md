# V16.0.12 - Khắc phục cửa sổ CMD bật lên khi quét LAN

## Nguyên nhân
Hai tiến trình con `ping` và `arp -a` trong `lan_discovery.py` trước đây gọi `subprocess.run()` mà không chỉ định ẩn cửa sổ console trên Windows. Khi quét nhiều IP, Windows có thể hiển thị cửa sổ CMD chớp liên tục hoặc nổi lên trên giao diện.

## Sửa chữa
- Gọi tiến trình với `CREATE_NO_WINDOW` và `STARTUPINFO` / `SW_HIDE` trên Windows khi sẵn có.
- Giữ lại timeout, output và logic quét; không dùng `shell=True`.
- Đồng thời ẩn console cho lời gọi PowerShell trong phần bảo trì hạ tầng.
- Thêm 3 kiểm thử hồi quy kiểm tra tham số ẩn CMD trong quét ping, đọc ARP và trên hệ điều hành khác.

## Chạy thử
1. Đóng toàn bộ ứng dụng cũ. Không nên chạy các phiên bản cùng lúc.
2. Giải nén toàn bộ ZIP vào thư mục mới.
3. Chạy `CHAY_THU_WINDOWS.bat` trong thư mục ứng dụng.
4. Vào **Hạ tầng CNTT > Giám sát > Quét thiết bị LAN**, quét một dải mạng nội bộ được phép quản lý.
5. Khi chạy bằng tệp `.bat`, cửa sổ CMD của **bản thân tệp .bat** có thể tồn tại để hiển thị chương trình/nhật ký. Bản sửa này ngăn CMD **phát sinh thêm do ping/arp**, không tự động ẩn cửa sổ lệnh do chính người dùng mở.

## Kiểm thử và giới hạn
- 103/103 kiểm thử Python đạt dưới Xvfb Linux, bao gồm ba kiểm thử mới.
- Có cảnh báo callback Tkinter sau khi đóng cửa sổ trong môi trường test, chưa được xử lý ở bản sửa tập trung này.
- Chưa thử trực tiếp trên Windows thực hoặc LAN thực tế.
