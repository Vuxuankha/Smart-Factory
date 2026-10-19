# PMC V16.0.4 – Hướng dẫn và phạm vi

Menu **PMC** chia ba phân nhóm: **I. PP** (1–5), **II. MC** (6–11), **III. Báo cáo & đối soát** (12–14). Các màn hình thao tác tương ứng nằm ở tab cửa sổ PMC.

## Dữ liệu
Lưu mặc định tại `%LOCALAPPDATA%\AlibabaMailIT\pmc.sqlite3` trên Windows (SQLite cục bộ, khác database email). Hãy sao lưu file SQLite trước khi cập nhật phần mềm. Mọi ngày dùng `YYYY-MM-DD`, số lượng cùng đơn vị nhất quán.

- **1. SO:** nhập mới hoặc CSV `id,product,qty,due,priority,customer`; ưu tiên 1–5, 5 là cao nhất.
- **2. Công suất:** tên chuyền + sản phẩm/ngày, hoặc CSV `name,units_per_day`.
- **3/5. APS tham chiếu:** xếp lần lượt đơn theo ngày giao và ưu tiên lên chuyền kết thúc sớm nhất; xem trước trước khi lưu. Thao tác lập lịch lại sau sự cố là thủ công; **không phải APS công nghiệp đầy đủ** (không xét lịch nghỉ, ca, thời gian setup, routing).
- **4. Lệnh SX:** sinh bản nháp mã `WO-<SO>` và chuỗi QR payload JSON; chưa có ảnh QR in hoặc lệnh ERP.
- **6. BOM:** CSV `product,material,per_unit`, nhân với sản lượng còn phải sản xuất. Mã hàng thiếu BOM được liệt kê.
- **7/8. MRP/cảnh báo thiếu:** dữ liệu tồn CSV `material,onhand,inbound,counted`; công thức nhu cầu ròng tối giản `max(0, yêu cầu - tồn - hàng về)`. Chỉ thông báo trên màn hình; chưa gửi đa kênh.
- **9. PR:** tạo nháp PR theo thiếu hụt, không phát hành PO.
- **10. Xuất kho:** trừ tồn trong SQLite sau xác nhận, không trừ tồn ERP; không kết nối barcode scanner trực tiếp.
- **11. Phế liệu:** chênh lệch tiêu hao thực tế so với BOM và % hao hụt.
- **12. Dashboard:** KPI tiến độ từ dữ liệu cục bộ; cần cập nhật sản lượng thủ công, không phải thời gian thực từ MES.
- **13. Đối soát:** so sánh tồn sổ và tồn kiểm kê.
- **14. Báo cáo:** xuất CSV UTF-8 BOM (`orders`, `mrp`, `shortages`, `reconcile`, `scrap`, `schedule`); **chưa có lịch tự gửi email**.

## Lưu ý
Chưa liên kết Digiwin iGP/SAP, SQL Server, email doanh nghiệp, kho thật, MES hoặc cấp duyệt điện tử. Tuyệt đối không sử dụng dữ liệu bản nháp để phát hành lệnh sản xuất/mua hàng nếu chưa đối chiếu ERP, BOM hiệu lực, lead time, đơn vị tính, lịch máy, mức tồn an toàn và luồng phê duyệt. Việc nhập CSV diễn ra lần lượt; khi một dòng lỗi, các dòng trước có thể đã được lưu – hãy nhập thử trên bản sao cơ sở dữ liệu. Các chức năng Email, VPN/IP và Hạ tầng CNTT trước đây giữ nguyên trong mã nguồn, nhưng phải thử trên Windows thực tế.

## Kiểm thử
`python -m unittest discover -s tests -q`; 71 bài đã chạy đạt trong môi trường phát triển; chưa có kiểm thử GUI Windows/ERP thực tế.
