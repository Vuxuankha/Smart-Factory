# Đối chiếu 100 hạng mục - V16.0.14

Bản yêu cầu gốc được giữ trong `docs/REQUIREMENTS_100_ORIGINAL.txt`. Tên, số thứ tự và mô tả gốc trong bảng dưới là yêu cầu, không phải lời xác nhận đã hoàn thành.

**22 mục có nghiệp vụ trong phạm vi cục bộ, 51 mục mới là một phần, 27 mục chưa triển khai.** Không có nhãn nào đồng nghĩa đã nghiệm thu đủ yêu cầu enterprise. Ngay cả mục cục bộ cũng có giới hạn nêu rõ.

Các cụm 500 triệu VNĐ, 24-48 giờ, 100%, 99.99%, ISO 27001/NIST và 800 tiêu chí thuộc tài liệu đề xuất; không phải báo giá, chứng nhận, SLA hay bảo đảm của bản mã nguồn này.


## I. Quản trị đa nhà máy & chuỗi cung ứng

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 1 | **Multi-Plant Centralized Control**<br>Quản lý tập trung đa chi nhánh / đa phân xưởng sản xuất trên một hệ thống. | Một phần / chưa tự động | Nhiều nhà máy trong cùng CSDL cục bộ, phân quyền tách riêng; chưa có máy chủ đồng bộ nhiều chi nhánh. |
| 2 | **Real-time Multi-Language & Currency**<br>Chuyển đổi đa ngôn ngữ (Việt - Trung - Anh) và tự động quy đổi tỷ giá ngoại tệ tức thì. | Một phần / chưa tự động | Lưu mã tiền tệ theo nhà máy. Chưa chuyển ngôn ngữ Việt/Trung/Anh hay cập nhật tỷ giá. |
| 3 | **VMI / EDI Integration**<br>Đồng bộ chuỗi cung ứng tự động với nhà cung cấp (Vendor Managed Inventory). | Chưa triển khai tích hợp | Chưa có VMI/EDI. Cần đặc tả thông điệp, đối tác, mã vật tư và môi trường kết nối thử. |
| 4 | **Private Mesh VPN Tunneling**<br>Mạng riêng mã hóa kết nối an toàn tuyệt đối giữa trụ sở và các nhà máy vệ tinh. | Chưa triển khai tích hợp | Chưa tạo Mesh VPN. Cửa sổ VPN cũ chỉ dùng profile Windows đã cấu hình; không cam kết an toàn tuyệt đối. |
| 5 | **Order Quota Allocation**<br>Quản lý hạn ngạch phân phối đơn hàng tự động giữa các nhà máy thành viên. | Một phần / chưa tự động | Đề xuất chia số lượng theo năng lực nhà máy do người dùng khai báo. Chỉ bản nháp, không tự chuyển đơn. |
| 6 | **Global Shipment Tracking**<br>Đồng bộ hóa lịch trình và tiến độ giao hàng toàn cầu. | Một phần / chưa tự động | Sổ theo dõi chuyến hàng, hạn giao và trạng thái nhập tay. Chưa kết nối hãng vận chuyển. |
| 7 | **Subcontractor Portal**<br>Quản lý nhà thầu phụ và gia công ngoài tập trung. | Một phần / chưa tự động | Quản lý hồ sơ nhà cung cấp/gia công. Chưa có cổng web cho nhà thầu. |
| 8 | **Global DRP**<br>Hoạch định nguồn lực phân phối toàn cầu (Distribution Requirements Planning). | Chưa triển khai tích hợp | Chưa có bộ máy DRP phân phối toàn cầu. |
| 9 | **Supply Chain Risk Mitigation**<br>Tự động đánh giá và cảnh báo rủi ro đứt gãy chuỗi cung ứng. | Một phần / chưa tự động | Quy tắc cảnh báo nhà cung cấp rủi ro cao và chuyến hàng trễ; không phải AI dự báo. |
| 10 | **Client VIP Portal**<br>Cổng thông tin tương tác dành riêng cho đối tác và khách hàng VIP. | Chưa triển khai tích hợp | Chưa có cổng khách hàng VIP. Không mở dịch vụ web ra Internet. |

## II. IoT biên, cảm biến & AI dự báo

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 11 | **Predictive Maintenance AI**<br>AI dự báo hỏng hóc máy móc trước **24–48 giờ**. | Chưa triển khai tích hợp | Chưa huấn luyện hay kết nối mô hình AI; không cam kết dự báo hỏng trước 24-48 giờ. |
| 12 | **Edge Computing Gateway**<br>Bộ điều khiển xử lý dữ liệu biên, chống mất dữ liệu khi gián đoạn mạng LAN/Internet. | Một phần / chưa tự động | Lưu mẫu đo cục bộ từ biểu mẫu/CSV. Chưa có gateway hay hàng đợi đồng bộ thiết bị biên. |
| 13 | **Industrial Protocol Integration**<br>Tích hợp đa dạng giao thức (PLC, Modbus TCP/RTU, OPC UA, MQTT, Siemens, Omron, Mitsubishi). | Chưa triển khai tích hợp | Chưa có driver PLC/Modbus/OPC UA/MQTT. Cần model thiết bị, bản đồ thanh ghi và kiểm thử tại hiện trường. |
| 14 | **Cleanroom Environment Monitoring**<br>Giám sát môi trường phòng sạch (nhiệt độ, độ ẩm, áp suất, hạt bụi). | Một phần / chưa tự động | Khai báo cảm biến, đơn vị, ngưỡng và mẫu đo có thời gian. Không tự thu thập hay chứng nhận phòng sạch. |
| 15 | **Vibration & Thermal Analytics**<br>Thu thập và phân tích tự động dữ liệu rung động, nhiệt độ động cơ. | Một phần / chưa tự động | Theo dõi các giá trị đo đã nhập; chưa phân tích phổ rung hay ảnh nhiệt. |
| 16 | **Air Leak & Power Detection**<br>Phân tích tiêu thụ khí nén và phát hiện rò rỉ đường ống tự động. | Chưa triển khai tích hợp | Chưa phát hiện rò khí tự động. Cần dữ liệu lưu lượng/áp suất và đường cơ sở. |
| 17 | **Real-time Threshold Alerts**<br>Cảnh báo thời gian thực khi thông số cảm biến vượt ngưỡng an toàn. | Một phần / chưa tự động | Tạo sự cố cục bộ khi mẫu đo được ghi và vượt ngưỡng. Mẫu cũ hiển thị STALE, không giả trạng thái online. |
| 18 | **IoT Calibration Control**<br>Tự động hiệu chuẩn thiết bị đo lường thông qua mạng IoT. | Chưa triển khai tích hợp | Chưa gửi lệnh hiệu chuẩn IoT. Cần quy trình và quyền được nhà sản xuất cho phép. |
| 19 | **Edge Asset Management**<br>Quản lý vòng đời cảm biến và phần cứng thiết bị biên. | Một phần / chưa tự động | Sổ tài sản biên, trạng thái và lịch bảo trì nhập tay; không điều khiển firmware. |
| 20 | **Digital Twin Factory Simulation**<br>Mô phỏng số song sinh hạ tầng và trạng thái nhà máy thời gian thực. | Chưa triển khai tích hợp | Chưa có Digital Twin mô phỏng vật lý hay đồng bộ trạng thái nhà máy. |

## III. WMS kho vận & Robot AGV

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 21 | **AGV & AMR Fleet Control**<br>Điều hướng tự động xe tự hành AGV và Robot cấp phát nguyên vật liệu. | Chưa triển khai tích hợp | Chưa điều khiển AGV/AMR. Không phát lệnh chuyển động; cần hệ thống an toàn và API nhà sản xuất. |
| 22 | **Auto-CAD/CAM & Auto-Nesting**<br>Tự động bóc tách bản vẽ kỹ thuật và lập trình sơ đồ cắt phôi tối ưu phế liệu. | Chưa triển khai tích hợp | Chưa đọc CAD/CAM hay tối ưu nesting; không tạo chương trình cắt CNC. |
| 23 | **ABC Smart Binning System**<br>Gợi ý vị trí xếp kho thông minh dựa trên phân tích tần suất xuất hàng. | Một phần / chưa tự động | Phân hạng ABC theo lượng đã xuất, tách theo đơn vị tính. Chưa tự xếp vị trí kệ. |
| 24 | **2D Barcode & RFID Inventory**<br>Quản lý kiểm kê kho tự động bằng mã vạch Zebra và thẻ RFID. | Một phần / chưa tự động | Nhập mã lô qua bàn phím/CSV; chưa kết nối SDK RFID/Zebra hay xác minh máy quét thật. |
| 25 | **FIFO / FEFO Expiry Lock**<br>Quản lý hạn sử dụng nguyên vật liệu và tự động khóa mã vật tư hết hạn. | Cục bộ - cần đọc phạm vi | Xuất FEFO theo lô; chặn lô hết hạn, HOLD/BLOCKED và không cho tồn âm. Ngày hết hạn được coi là không còn khả dụng. |
| 26 | **Auto Material Requisition**<br>Tự động tạo phiếu xuất kho nguyên vật liệu theo lệnh sản xuất PMC. | Cục bộ - cần đọc phạm vi | Ghi phiếu cấp vật tư cho lệnh RELEASED theo BOM chốt; trừ kho cục bộ nguyên tử, không ghi ERP. |
| 27 | **Virtual Stock Reconciliation**<br>Kiểm soát tồn kho ảo và đối soát sai lệch kho thời gian thực. | Một phần / chưa tự động | Báo cáo chênh lệch kiểm kê với tồn sổ tại lúc ghi phiếu; chưa tự điều chỉnh kho/ERP. |
| 28 | **Consignment Inventory**<br>Quản lý kho hàng ký gửi trực tiếp với nhà cung cấp. | Một phần / chưa tự động | Lưu chủ sở hữu trên lô ký gửi; chưa hạch toán công nợ nhà cung cấp. |
| 29 | **Auto Palletizing & Labeling**<br>Tự động hóa quá trình đóng gói, dán nhãn pallet sản phẩm. | Chưa triển khai tích hợp | Chưa điều khiển máy đóng pallet/dán nhãn. |
| 30 | **Yard & Dock Management**<br>Quản lý bãi đỗ xe và điều phối xe vận chuyển hàng hóa ra vào cổng nhà máy. | Một phần / chưa tự động | Đặt khung giờ cửa kho/xe, chặn trùng lịch; chưa kết nối barie hay cổng kiểm soát. |

## IV. MES & PMC sản xuất nâng cao

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 31 | **Advanced APS & CRP**<br>Thuật toán lập lịch sản xuất tự động nâng cao và cân đối năng lực thiết bị. | Một phần / chưa tự động | Lập lịch nháp theo công suất một máy đã chọn, tránh lịch bảo trì. Không phải APS tối ưu công nghiệp. |
| 32 | **What-if Scenario Simulation**<br>Mô phỏng phương án sản xuất khi chen đơn hàng khẩn hoặc thay đổi máy chạy. | Một phần / chưa tự động | So sánh chi phí thường/tăng ca/gia công theo đơn giá nhập vào; không mô phỏng toàn dây chuyền. |
| 33 | **Multi-level MRP Real-time**<br>Tính toán nhu cầu vật tư ròng đa cấp (BOM 5–10 cấp) theo thời gian thực. | Một phần / chưa tự động | BOM tối đa 10 cấp; kiểm tra vòng lặp, cân đối tồn và hàng về đúng hạn tại một ngày nhu cầu. Chưa có MRP theo kỳ/đồng bộ ERP. |
| 34 | **Real-time OEE Tracking**<br>Theo dõi chỉ số hiệu suất tổng thể thiết bị (Khả dụng, Hiệu suất, Chất lượng). | Cục bộ - cần đọc phạm vi | Tính A x P x Q từ bản ghi ca đã kiểm tra; hiệu suất vượt 100% được cảnh báo, không che giấu. Chưa lấy dữ liệu PLC. |
| 35 | **Andon Real-time System**<br>Quản lý trạng thái máy chạy, dừng, chờ nguyên liệu thời gian thực. | Một phần / chưa tự động | Khai báo trạng thái máy thủ công; chưa có nút/đèn Andon trực tuyến. |
| 36 | **Bottleneck Analysis**<br>Tự động cân đối năng lực dây chuyền và phát hiện cổ chai sản xuất. | Một phần / chưa tự động | Hiển thị công suất/hạn hoàn thành trong lịch nháp; chưa cân bằng tự động toàn dây chuyền. |
| 37 | **Paperless e-MO**<br>Quản lý lệnh sản xuất điện tử không giấy tờ trên phân xưởng. | Cục bộ - cần đọc phạm vi | Lệnh sản xuất cục bộ DRAFT/RELEASED/HOLD/CLOSED/CANCELLED, chốt BOM khi phát hành. Chưa phát hành ERP. |
| 38 | **Hourly Output Tracking**<br>Theo dõi tiến độ hoàn thành sản phẩm theo từng giờ / từng ca làm việc. | Một phần / chưa tự động | Chứng từ sản lượng tốt/phế có thời gian, mã giao dịch; chưa tự thu từ máy quét. |
| 39 | **Mould & Tooling Lifecycle**<br>Quản lý vòng đời khuôn đúc, đồ gá bảo trì định kỳ. | Một phần / chưa tự động | Hồ sơ khuôn/đồ gá và bảo trì; chưa tối ưu tranh chấp khuôn giữa nhiều máy. |
| 40 | **CNC/Press Dispatching**<br>Tự động điều phối thứ tự ưu tiên gia công trên các máy CNC/máy dập. | Một phần / chưa tự động | Gợi ý thứ tự chạy lệnh trên máy đã chọn; không gửi lệnh CNC/máy dập. |

## V. Bảo mật công nghiệp & lưu trữ

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 41 | **OT/IT Network Security**<br>Giám sát an ninh mạng công nghiệp toàn diện, tự động chặn thiết bị lạ cắm chui. | Chưa triển khai tích hợp | Chưa có NAC/IDS hay tự chặn thiết bị lạ. Quét LAN cũ không phải bộ kiểm soát an ninh OT. |
| 42 | **Multi-layer Encrypted Backup**<br>Sao lưu đa lớp tự động (Local + Synology NAS + Cloud) mã hóa AES-256. | Một phần / chưa tự động | Snapshot SQLite + SHA-256 ZIP cục bộ, KHÔNG mã hóa. Chưa AES-256, NAS/cloud hay sao lưu tất cả phân hệ. |
| 43 | **1-Click Disaster Recovery**<br>Tính năng khôi phục thảm họa 1-Click khi sập máy chủ. | Một phần / chưa tự động | Kiểm tra gói và khôi phục vào TỆP MỚI; không thay CSDL đang chạy, không failover tự động. |
| 44 | **100% Comprehensive Audit Trail**<br>Ghi vết kiểm toán toàn diện 100% mọi thao tác người dùng. | Cục bộ - cần đọc phạm vi | Ghi thay đổi/xuất dữ liệu Smart Factory cùng giao dịch, có người thao tác. Không phủ 100% các phân hệ cũ. |
| 45 | **ISO 27001 & NIST Compliance**<br>Tuân thủ các tiêu chuẩn bảo mật và kiểm toán quốc tế. | Chưa triển khai tích hợp | Chưa được đánh giá/chứng nhận ISO 27001 hay NIST. Tên mục là yêu cầu, không phải chứng nhận. |
| 46 | **Failover Cluster 99.99% Uptime**<br>Hệ thống dự phòng nóng đảm bảo vận hành liên tục không gián đoạn. | Chưa triển khai tích hợp | Chưa có cluster dự phòng. Không cam kết uptime 99.99% hay vận hành không gián đoạn. |
| 47 | **RBAC Fine-grained Access**<br>Quản lý phân quyền người dùng chi tiết theo từng vai trò công việc. | Cục bộ - cần đọc phạm vi | Phân quyền vai trò + nhà máy + nhóm nghiệp vụ ở lớp xử lý mới. Nhân viên mặc định chưa có quyền. |
| 48 | **Internal/External TLS Encryption**<br>Mã hóa dữ liệu truyền tải SSL/TLS nội bộ và ngoại vi. | Chưa triển khai tích hợp | Giữ TLS của kết nối mail hiện có. Chưa có dịch vụ nội bộ TLS/mTLS cho các nhà máy. |
| 49 | **Automated Vulnerability Scanner**<br>Tự động quét lỗ hổng bảo mật hệ thống định kỳ hằng tuần. | Chưa triển khai tích hợp | Chưa có máy quét CVE theo lịch. Quét IP/TCP không phải quét lỗ hổng bảo mật. |
| 50 | **Brute-force Protection**<br>Cơ chế tự động khóa tài khoản khi phát hiện đăng nhập dò mật khẩu. | Cục bộ - cần đọc phạm vi | Giữ cơ chế khóa tạm sau nhiều lần sai mật khẩu của tài khoản cục bộ; chưa phải SSO/IdP doanh nghiệp. |

## VI. AI & Executive Dashboard

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 51 | **AI Diagnostic & Log Analysis**<br>Trợ lý AI chẩn đoán sự cố vận hành và phân tích tệp nhật ký hệ thống. | Một phần / chưa tự động | Sổ sự cố và bằng chứng do người dùng nhập; chưa có trợ lý AI phân tích log. |
| 52 | **Executive BI Dashboard**<br>Bảng điều khiển quản trị chiến lược dành riêng cho Ban Giám đốc. | Cục bộ - cần đọc phạm vi | Thẻ KPI và biểu đồ từ bản ghi thật trong CSDL cục bộ; làm mới theo thao tác, không dựng số liệu giả. |
| 53 | **Multi-channel Real-time Alerts**<br>Cảnh báo sự cố đa kênh (Telegram, Zalo ZNS, Email, SMS, Còi hú). | Chưa triển khai tích hợp | Chưa gửi Telegram/Zalo/SMS/còi. Cần kênh đã được cấp quyền và chính sách chống gửi lặp. |
| 54 | **Automated Daily Management Report**<br>Tự động tổng hợp và gửi báo cáo quản trị vào 08:00 sáng hằng ngày. | Một phần / chưa tự động | Xuất báo cáo HTML/CSV theo yêu cầu; chưa hẹn 08:00 hay tự gửi email. |
| 55 | **Role-based Widget Customization**<br>Giao diện tùy chỉnh widget linh hoạt theo từng phòng ban chức năng. | Một phần / chưa tự động | Ghi nhớ nhà máy/nhóm đang chọn theo tài khoản; chưa có trình bố trí widget theo vai trò. |
| 56 | **AI Cost & Productivity Trends**<br>Phân tích xu hướng năng suất và chi phí sản xuất bằng thuật toán AI. | Một phần / chưa tự động | Công cụ tính chi phí từ số nhập vào; chưa dự báo xu hướng AI. |
| 57 | **Voice/Chat Knowledge Base**<br>Trợ lý ảo tra cứu thông tin quy trình, BOM, tài liệu kỹ thuật qua Chatbot. | Chưa triển khai tích hợp | Chưa có chatbot/giọng nói hay kho tri thức tìm kiếm ngữ nghĩa. |
| 58 | **Interactive Network Topology Map**<br>Bảng điều khiển trực quan trạng thái kết nối mạng lưới thiết bị. | Một phần / chưa tự động | Vẽ quan hệ thiết bị cha-con do người dùng khai báo. Không suy đoán cổng switch hay kết nối vật lý. |
| 59 | **Live CCTV Stream Monitoring**<br>Theo dõi trực tiếp camera an ninh và luồng video giám sát phân xưởng. | Chưa triển khai tích hợp | Chưa phát RTSP/CCTV. Cần player, camera được cấp quyền và kiểm tra codec/tải mạng. |
| 60 | **System Incident History Log**<br>Quản lý danh mục thông báo và lưu trữ lịch sử sự cố toàn hệ thống. | Cục bộ - cần đọc phạm vi | Sổ sự cố cục bộ lâu dài với người phụ trách, mức độ và kết quả xử lý. |

## VII. Thiết bị mạng IT / OT

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 61 | **Auto-Discovery Network Topology**<br>Tự động phát hiện và vẽ sơ đồ kết nối thiết bị mạng LAN/VLAN. | Một phần / chưa tự động | Mở lại quét LAN đã có. Sơ đồ Smart Factory dùng liên kết khai báo, chưa tự dò LLDP/CDP/VLAN. |
| 62 | **Smart PDU Remote Power Control**<br>Điều khiển nguồn điện thiết bị thông minh từ xa (Remote Reboot) cho máy chủ/switch. | Chưa triển khai tích hợp | Chưa gửi lệnh PDU hay khởi động lại thiết bị. Không cắt nguồn từ giao diện này. |
| 63 | **QoS & Traffic Shaping**<br>Định hình lưu lượng mạng và ưu tiên băng thông cho hệ thống ERP/MES. | Chưa triển khai tích hợp | Chưa cấu hình QoS/traffic shaping trên router/switch. |
| 64 | **IT Asset Management (ITAM)**<br>Quản lý tài sản và bản quyền phần mềm tự động trong toàn nhà máy. | Một phần / chưa tự động | Hồ sơ tài sản, vị trí, bản quyền và hạn dùng; chưa triển khai agent tự kiểm kê. |
| 65 | **ISP & VPN Tunnel Monitoring**<br>Giám sát trạng thái đường truyền Internet / VPN chính và dự phòng. | Một phần / chưa tự động | Mở cửa sổ IP/VPN hiện có để kiểm tra theo yêu cầu; chưa giám sát ISP 24/7. |
| 66 | **IP Address & Conflict Management**<br>Quản lý dải địa chỉ IP nội bộ, tự động phát hiện xung đột IP. | Một phần / chưa tự động | Chặn IP trùng trong sổ thiết bị một nhà máy; chưa xác định xung đột IP ngoài mạng thật. |
| 67 | **Centralized Firewall Integration**<br>Cấu hình và quản lý tường lửa trung tâm tập trung. | Chưa triển khai tích hợp | Chưa thay đổi firewall trung tâm; cần adapter nhà sản xuất, phê duyệt và rollback. |
| 68 | **Industrial Guest WiFi Isolation**<br>Quản lý thiết bị phát sóng WiFi công nghiệp và phân vùng mạng khách. | Chưa triển khai tích hợp | Chưa quản lý SSID/VLAN/cách ly WiFi khách. |
| 69 | **Latency & Packet Loss Check**<br>Kiểm tra độ trễ và chất lượng đường truyền đến các trạm máy biên. | Một phần / chưa tự động | Dùng quét ping/TCP hiện có; chưa đo mất gói liên tục hay xác nhận SLA. |
| 70 | **Group Device Management**<br>Tự động gom nhóm thiết bị theo khu vực và phân xưởng quản lý. | Một phần / chưa tự động | Phân loại thiết bị theo nhà máy, vị trí và loại tài sản. |

## VIII. Chất lượng & truy xuất

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 71 | **End-to-End 2-way Traceability**<br>Truy xuất nguồn gốc sản phẩm lỗi 2 chiều (từ linh kiện đến thành phẩm và ngược lại). | Một phần / chưa tự động | Truy xuất hai chiều lô đầu vào -> lệnh -> lô thành phẩm từ giao dịch mới; không bao gồm lịch sử PMC cũ/ERP. |
| 72 | **AI Vision Quality Inspection**<br>AI Vision kiểm tra bề mặt sản phẩm và phát hiện lỗi ngoại quan trên băng chuyền. | Chưa triển khai tích hợp | Chưa có mô hình AI Vision hay kết nối băng chuyền; cần dữ liệu lỗi gán nhãn và nghiệm thu. |
| 73 | **CAPA Management**<br>Quản lý quy trình xử lý khiếu nại và hành động khắc phục/phòng ngừa. | Cục bộ - cần đọc phạm vi | CAPA OPEN -> IN_PROGRESS -> VERIFY -> CLOSED; bắt buộc nguyên nhân, hành động và bằng chứng trước khi đóng. |
| 74 | **Equipment Calibration Control**<br>Quản lý lịch kiểm định, hiệu chuẩn thiết bị đo lường định kỳ. | Cục bộ - cần đọc phạm vi | Hồ sơ hiệu chuẩn và cảnh báo quá hạn; không thực hiện hiệu chuẩn vật lý. |
| 75 | **IQC (Incoming Quality Control)**<br>Kiểm soát chất lượng nguyên vật liệu đầu vào. | Cục bộ - cần đọc phạm vi | Phiếu IQC cục bộ; lô có mẫu lỗi bị BLOCKED. Không tự duyệt hàng trong ERP. |
| 76 | **PQC (Process Quality Control)**<br>Kiểm soát chất lượng trong quá trình sản xuất real-time. | Cục bộ - cần đọc phạm vi | Phiếu PQC qua biểu mẫu/CSV; chưa thu thập trực tiếp từ dây chuyền. |
| 77 | **OQC (Outgoing Quality Control)**<br>Kiểm soát chất lượng thành phẩm trước khi xuất kho. | Cục bộ - cần đọc phạm vi | Phiếu OQC cục bộ; không tự phê duyệt giao hàng trên hệ thống khác. |
| 78 | **Electronic e-Checklist**<br>Quản lý biểu mẫu kiểm tra chất lượng điện tử trên thiết bị di động/Panel PC. | Một phần / chưa tự động | Biểu mẫu kiểm tra chất lượng desktop; chưa có web/mobile checklist tùy biến. |
| 79 | **Defect Root Cause Analytics**<br>Thống kê tỷ lệ lỗi hỏng theo từng công đoạn và nguyên nhân gốc rễ. | Cục bộ - cần đọc phạm vi | Thống kê tỷ lệ/mã nguyên nhân từ phiếu kiểm tra; không tự suy luận quan hệ nhân quả. |
| 80 | **SOP Digital Integration**<br>Quản lý mẫu chuẩn và tài liệu tiêu chuẩn kỹ thuật sản phẩm kỹ thuật số. | Một phần / chưa tự động | Sổ SOP có revision, ngày hiệu lực và tham chiếu; chưa có phê duyệt/phân phối tài liệu kiểm soát. |

## IX. Nhân sự & ca sản xuất

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 81 | **Automated Shift Scheduling**<br>Xếp lịch ca kíp sản xuất tự động dựa trên năng lực và tải trọng đơn hàng. | Một phần / chưa tự động | Phân công ca thủ công có kiểm tra trùng giờ/chứng chỉ/bảo trì; chưa tối ưu nhân lực tự động. |
| 82 | **Barcode Labor Productivity**<br>Liên kết dữ liệu quét mã vạch cá nhân với sản lượng hoàn thành để tính năng suất. | Một phần / chưa tự động | Gắn mã nhân sự vào phiếu sản lượng; chưa đồng bộ đầu đọc barcode. |
| 83 | **Skills Matrix Management**<br>Quản lý ma trận kỹ năng và chứng chỉ vận hành máy của nhân sự. | Cục bộ - cần đọc phạm vi | Ma trận kỹ năng theo nhân sự và khoảng hiệu lực; kiểm tra khi phân ca. |
| 84 | **Safety Certificate Warning**<br>Cảnh báo tự động khi nhân sự chưa có chứng chỉ được phân công vận hành máy nguy hiểm. | Cục bộ - cần đọc phạm vi | Từ chối phân ca khi thiếu chứng chỉ bắt buộc còn hạn suốt ca; không thay khóa liên động an toàn máy. |
| 85 | **Operator Presence Tracking**<br>Theo dõi thời gian hiện diện và hiệu suất làm việc thực tế tại trạm máy. | Một phần / chưa tự động | Lịch ca dự kiến, không đo sự hiện diện thật tại trạm. |
| 86 | **Electronic Shift Handover Log**<br>Quản lý phân quyền ca trực và bàn giao ca sản xuất điện tử. | Cục bộ - cần đọc phạm vi | Nhật ký bàn giao ca cục bộ có người ghi và thời gian. |
| 87 | **Biometric Attendance Integration**<br>Tích hợp hệ thống chấm công sinh trắc học (Khuôn mặt / Vân tay). | Chưa triển khai tích hợp | Chưa tích hợp chấm công sinh trắc; không thu thập ảnh mặt/vân tay. |
| 88 | **Internal Training & Qualification**<br>Quản lý đào tạo nội bộ và đánh giá tay nghề định kỳ cho công nhân. | Cục bộ - cần đọc phạm vi | Sổ đào tạo và kết quả; chứng chỉ vận hành được khai báo riêng, không tự cấp. |
| 89 | **Piece-rate Wage Calculation**<br>Tính toán lương sản phẩm tự động dựa trên dữ liệu MES hoàn thành. | Một phần / chưa tự động | Chỉ tính chi phí/đơn giá nhập vào; chưa có payroll, thuế hay bảng lương theo MES. |
| 90 | **HSE Equipment Assignment**<br>Quản lý an toàn vệ sinh lao động và phân công trang thiết bị bảo hộ. | Cục bộ - cần đọc phạm vi | Sổ cấp phát PPE theo nhân sự, số lượng và ngày; không phải chứng nhận HSE. |

## X. Tài chính, ESG & trải nghiệm

| Mục | Tính năng / yêu cầu gốc | Trạng thái | Phạm vi thực tế V16.0.14 |
|---|---|---|---|
| 91 | **Real-time Product Costing**<br>Tính giá thành sản phẩm theo thời gian thực (Cộng dồn NVL, điện, nhân công, khấu hao). | Một phần / chưa tự động | Cộng NVL, nhân công, điện, chi phí chung cho lô theo số nhập; không tự hạch toán ERP. |
| 92 | **Scrap & Waste Analytics**<br>Phân tích chi tiết phế liệu, lãng phí vật tư và nguyên nhân tổn thất. | Một phần / chưa tự động | Ghi sản lượng tốt/phế và thống kê chất lượng; chưa có định mức phế nhiều công đoạn. |
| 93 | **Equipment ROI Analytics**<br>Đánh giá hiệu quả đầu tư trang thiết bị và máy móc sản xuất. | Một phần / chưa tự động | Tính ROI và thời gian hoàn vốn giản đơn từ vốn/tiết kiệm nhập vào; không dự báo tài chính. |
| 94 | **Smart Energy Metering**<br>Giám sát tiêu thụ điện năng chi tiết theo từng máy móc, đơn hàng. | Một phần / chưa tự động | Bản ghi kWh theo máy và khoảng giờ; chưa lấy số tự động từ công tơ. |
| 95 | **Idle Power Waste Detection**<br>Phát hiện lãng phí năng lượng khi máy móc để chế độ không tải quá lâu. | Một phần / chưa tự động | Cảnh báo bản ghi IDLE vượt ngưỡng kWh do người dùng đặt; không tự ngắt thiết bị. |
| 96 | **Carbon Footprint Tracking / ESG**<br>Tự động tính toán lượng phát thải khí nhà kính theo tiêu chuẩn ESG. | Một phần / chưa tự động | Ước tính CO2e theo hệ số, nguồn và ngày do người dùng cung cấp. Thiếu hệ số: UNKNOWN. Chưa chứng nhận ESG. |
| 97 | **Drag-and-Drop Custom Dashboard**<br>Giao diện bảng điều khiển kéo-thả tùy chỉnh linh hoạt. | Chưa triển khai tích hợp | Chưa có kéo-thả widget. Dashboard bố cục cố định, có cuộn và tab. |
| 98 | **Industrial Night Mode**<br>Chế độ giao diện tối chuyên biệt cho phòng trực vận hành ban đêm. | Cục bộ - cần đọc phạm vi | Giao diện tối đồng bộ với ứng dụng hiện có; chưa có nút đổi Light/Dark. |
| 99 | **User Preference Sync**<br>Đồng bộ và lưu trữ thiết lập cá nhân hóa gắn liền với tài khoản người dùng. | Cục bộ - cần đọc phạm vi | Lưu lựa chọn nhà máy/nhóm theo tài khoản trên máy này; không đồng bộ cloud/thiết bị khác. |
| 100 | **E2E Automated Test Suite**<br>Bộ kiểm thử tự động toàn diện quét toàn bộ 800 tiêu chí hệ thống sau mỗi bản update. | Một phần / chưa tự động | Có unit, integration và GUI regression tests. Không tương đương 800 tiêu chí hay nghiệm thu EXE Windows. |
