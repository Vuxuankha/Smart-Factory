# Alibaba Mail V16.0.5 – Bổ sung quản lý PMC nâng cao

## Nguyên tắc
Giữ nguyên module email, IP/VPN, IT Infrastructure, PMC 14 mục trước đó. Menu **PMC** nay có 4 nhóm: PP, MC, Báo cáo & đối soát, Kỹ thuật & gia công. Mở từng mục con để nhập hoặc xem dữ liệu.

## Chức năng có xử lý dữ liệu mới
- (7) Lịch bảo trì: ghi lịch máy/chuyền, phát hiện xung đột với lịch sản xuất đã lưu; **chưa tự tối ưu lại lịch**.
- (13) Kitting: ghi phân bổ vật tư theo đơn và ngăn phân bổ vượt BOM còn lại; **không giữ tồn kho vật lý**.
- (14) Lô & FIFO/FEFO: nhập lô, hạn dùng, gợi ý lấy lô theo hạn dùng rồi ngày nhận, cảnh báo sắp hết hạn; **chưa tự xuất kho bằng quét mã**.
- (15) Tồn kho an toàn: tính tồn dự phòng và điểm đặt lại từ đầu vào người dùng; **chưa dự báo bằng dữ liệu lịch sử**.
- (16) ECO: ghi phiên bản thay đổi và liệt kê đơn hàng cần xét duyệt; **chưa tự khóa sản xuất**.
- (17) Gia công ngoài: tạo phiếu theo dõi và xem quá hạn; **chưa đồng bộ giao hàng nhà thầu**.
- (22) Nguyên nhân trễ: ghi các nguyên nhân theo nhóm và tổng hợp tần suất; **không suy luận nguyên nhân tự động**.
- (24) 3-Way Matching: ghi PO, GR, hóa đơn trong dữ liệu cục bộ và đánh dấu các trường hợp vượt PO, vượt nhận hoặc sai đơn giá; trạng thái REVIEW cần con người kiểm tra.
- (30) Nhật ký thao tác mới: lưu hành động của mô-đun nâng cao. **Chưa triển khai tài khoản và danh tính nhân viên/nhật ký bất biến**.

## Chức năng chưa tự động hóa hoàn toàn
(1) đồng bộ SO ERP; (3) thuật toán APS công nghiệp; (4) phát hành trực tiếp ERP và in QR thật; (5) điều độ thời gian thực; (6) tối ưu đa nhà máy; (10) gửi cảnh báo đa kênh; (12) quét mã; (18) nesting; (19) khuôn/đồ gá; (20) mô phỏng chi phí; (21) tự dừng chuyền/hủy PO; (23) VMI/EDI; (25) dashboard thời gian thực qua MES; (28) tối ưu vận tải; (29) gửi báo cáo theo lịch. Các mục chưa có kết nối hoặc engine sẽ không được trình bày như đã hoàn thiện.

## Dữ liệu, kiểm thử và triển khai
- Dữ liệu PMC cục bộ: `%LOCALAPPDATA%\\AlibabaMailIT\\pmc.sqlite3` (Windows); sao lưu trước khi thử.
- Phiên bản này cập nhật schema SQLite bổ sung qua `CREATE TABLE IF NOT EXISTS`. Không ghi dữ liệu sang ERP, SQL Server, PLC hay máy quét.
- Chạy `python -m unittest discover -s tests` từ thư mục `alibaba_mail_app`.
- 79 bài kiểm thử đạt trên môi trường phát triển. Chưa kiểm thử trực tiếp GUI trên Windows hoặc tích hợp hệ thống doanh nghiệp.
- Không nhập mật khẩu ERP/SMTP vào mã nguồn. Kết nối thật cần thiết kế phân quyền, sao lưu, giao dịch và kiểm thử riêng.
