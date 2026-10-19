# BÁO CÁO RÀ SOÁT DANH SÁCH “800 MỤC” — V16.0.11

## Giới hạn của tài liệu đầu vào
Tài liệu 800 mục thực tế **không liệt kê đầy đủ 800 nội dung**. Đa số phần có các đoạn `(... tiếp tục chi tiết ...)`, nên không thể kiểm tra độc lập từng tiêu chí chưa được cung cấp. Nhiều nội dung là tình huống giả định cho các hệ thống chưa được kết nối như SAP/Digiwin/SQL Server/PLC/MQTT/WMS/OTA/SNMP. Không được suy ra rằng các lỗi đó tồn tại trong mã nguồn hoặc đã được sửa.

## Sửa lỗi và tăng độ an toàn có thể xác minh
- LAN discovery: quét theo số lượng tác vụ giới hạn, không dồn tất cả IP vào hàng đợi ngay khi bắt đầu; hỗ trợ hủy quét nhanh hơn, không đánh dấu lượt hủy là hoàn tất; lỗi trên một IP không làm hỏng toàn bộ lượt quét; giữ giới hạn mạng IPv4 private tối đa /24.
- IMAP QUOTA: nhận cả biến thể capability `QUOTA=...` nếu máy chủ trả về; ngăn dữ liệu nhập bắt đầu bằng ký tự công thức khi xuất CSV.
- PMC: xác thực số lượng, ngày tháng và khóa trùng của toàn bộ dữ liệu CSV trước khi bắt đầu ghi, giảm trường hợp nhập dở vì một dòng lỗi ở cuối tệp. Báo cáo CSV từ chối ghi đè file cũ, chống công thức nguy hiểm trong các ô đầu ra.
- Quét LAN: báo rõ khi lượt quét bị hủy; báo cáo quét không ghi đè tệp CSV đã tồn tại.
- Đồng bộ tiêu đề giao diện và nhãn sidebar lên V16.0.11.

## Kết quả
- 100/100 bài `unittest` chạy trong môi trường Linux có màn hình ảo (Xvfb) đạt.
- Các bài này kiểm tra logic Python, mock IMAP, xử lý mạng mô phỏng và một số luồng UI Tkinter. Chúng KHÔNG chứng minh không còn lỗi.
- Chưa thử nghiệm kết nối Alibaba Mail thật, quyền quản trị IMAP, cấu hình mạng vật lý, Windows 10/11, EXE PyInstaller, tải lớn 72 giờ, khôi phục thảm họa, phần cứng Camera/NAS/PLC hoặc ERP thật.
- Một số callback Tkinter sau khi hủy cửa sổ xuất hiện cảnh báo trong môi trường test; không làm fail bài test nhưng cần tiếp tục đánh giá vòng đời UI trên Windows.

## Phạm vi an toàn
Không tự động thao tác DHCP/AD, dừng chuyền, xóa email, thay đổi dữ liệu ERP hoặc mạng doanh nghiệp. Bảo toàn mô hình lưu trữ và dữ liệu gốc. Hãy sao lưu trước khi triển khai chính thức và kiểm tra trên máy Windows thử nghiệm.

## Điều cần làm trước triển khai doanh nghiệp
Thử trên mạng LAN được phép, chạy IMAP QUOTA với tài khoản mẫu, kiểm tra mỗi chức năng trên Windows, test dung lượng đĩa đầy và khôi phục sao lưu, kiểm thử thiết bị/ERP và rà soát bảo mật bởi người có quyền quản trị.
