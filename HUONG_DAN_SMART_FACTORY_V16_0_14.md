# Alibaba Operations Center V16.0.14 - Smart Factory

## 1. Bản bàn giao và cách mở

Bản này mở rộng V16.0.13 bằng một workspace Smart Factory cục bộ, giữ lại Email, IMAP QUOTA, IP/VPN, Hạ tầng IT, PMC cũ và đăng nhập ứng dụng.

Giải nén vào thư mục mới, mở `alibaba_mail_app`, chạy `CHAY_THU_WINDOWS.bat`. Cần Python 3.10+ với Tkinter và openpyxl; psutil là tùy chọn cho CPU/RAM. Bản ZIP chưa có EXE. `TAO_EXE_WINDOWS.bat` cài môi trường riêng và dự kiến tạo `dist/AlibabaOperationsCenter.exe` trên Windows; cần tự kiểm thử bản build đó.

Đăng nhập bằng **tài khoản ứng dụng**, sau đó chọn **09 Smart Factory** trên sidebar hoặc menu **Smart Factory**. Lần đầu trên máy chưa có dữ liệu tài khoản, giữ quy trình tạo Quản trị IT của V16.0.13. Không có mật khẩu mặc định.

**Smart Factory không hỏi tài khoản/mật khẩu mail.** Chỉ các tác vụ IMAP cũ thực sự kết nối hộp thư mới cần thông tin mail.

## 2. Giao diện và 10 nhóm

Sidebar Smart Factory giữ đúng thứ tự 10 nhóm trong tệp yêu cầu. Mỗi nhóm có các tab Dashboard, Dữ liệu & nghiệp vụ, Công cụ & báo cáo, Danh mục & phạm vi. Tab phạm vi hiển thị 10 yêu cầu gốc của nhóm, ghi rõ phần đã có và phần chưa tích hợp. Nút mở bị vô hiệu với mục chưa có nghiệp vụ.

Có 27 loại biểu mẫu nhập/sửa dữ liệu thật, không phải nút minh họa. Bảng có phân trang 100 dòng, tìm kiếm, cuộn ngang/dọc. `Ctrl+F` đưa con trỏ vào ô tìm kiếm; `F5` làm mới. Biểu mẫu dùng `Ctrl+Enter` để ghi và `Esc` để đóng khi chưa ghi.

KPI và biểu đồ chỉ dùng dữ liệu cục bộ. Chưa có dữ liệu/chưa được cấp quyền sẽ hiện thông báo, không điền số giả. Ảnh trong `preview/` sử dụng bộ dữ liệu DEMO tổng hợp, không phải nhà máy của bạn. Mở app không tự nạp DEMO.

## 3. Nhà máy, tài khoản và phân quyền

Quản trị IT chọn **+ Nhà máy**, nhập mã, tên, mã tiền tệ và công suất quy ước. UTC offset tính bằng phút; Việt Nam mặc định +420. Đây là múi giờ cố định, chưa xử lý DST tự động. Công suất giữa các nhà máy phải do người dùng quy về cùng đơn vị trước khi phân bổ.

Nhóm 1 cho sửa tên/công suất. Sau khi có bản ghi, không đổi tiền tệ/múi giờ để tránh sai lịch sử.

Quản trị IT có quyền toàn workspace. Kiểm toán viên được đọc, không ghi. Nhân viên mặc định không thấy nhà máy; cần tài khoản đã phê duyệt và cấp quyền trong **nhóm 5 -> Công cụ -> Phân quyền**. Quyền đọc/ghi theo nhà máy và nhóm; thu hồi có hiệu lực ở lần thao tác kế tiếp.

Các hồ sơ nhân sự, chứng chỉ, ca làm, đào tạo, bản quyền và số điện chỉ Quản trị IT được ghi. Báo cáo liên phân hệ cần quyền trên nhóm dữ liệu liên quan. Quyền này không thay Windows ACL và không ngăn quản trị hệ điều hành sửa trực tiếp tệp CSDL.

## 4. Quy trình thử kho -> sản xuất -> chất lượng

Tạo nhà máy riêng `DEMO`. Trong `samples/smart_factory_demo`, 5 CSV ghi rõ là dữ liệu giả lập. Nhập lần lượt vào đúng loại: `01_materials` (nhóm 3), `02_bom` (nhóm 4), `03_lots` (nhóm 3), `04_orders` (nhóm 4), `05_assets` (nhóm 7). Hạn năm 2099 chỉ phục vụ ví dụ, không áp dụng cho hàng thật.

Lệnh `DEMO-MO` cần 10 thành phẩm, mỗi cái dùng 2 `DEMO-RM`. Sửa trạng thái từ DRAFT sang RELEASED để chốt BOM. Trong nhóm 3, chọn cấp vật tư FEFO: mã giao dịch `DEMO-ISSUE-01`, lệnh `DEMO-MO`, vật tư `DEMO-RM`, số lượng 20. Kho giảm từ 100 còn 80; nhập lại đúng mã/nội dung sẽ trả kết quả cũ, không trừ hai lần.

Nhóm 4 ghi sản lượng với giao dịch `DEMO-OUTPUT-01`, lệnh `DEMO-MO`, 10 tốt, 0 phế, lô mới `DEMO-FG-LOT`. Lô thành phẩm ban đầu HOLD. Nhóm 8 cho ghi IQC/PQC/OQC và thay trạng thái chất lượng theo quyền, bắt buộc lý do. Phiếu có lỗi sẽ chặn lô. Dùng công cụ truy xuất trong nhóm 8 để xem quan hệ nguyên liệu - lệnh - thành phẩm.

Chỉ đóng lệnh khi đủ thành phẩm. Lệnh đã đóng/hủy không được sửa. Hoàn trả hiện chỉ hỗ trợ toàn bộ phiếu xuất, một lần, trước khi lệnh có sản lượng. Chưa hỗ trợ trả một phần, phế-only, hủy thành phẩm hay backflush hao hụt nhiều công đoạn.

## 5. Tính toán và kiểm soát quan trọng

MRP tính cho một sản phẩm/số lượng/ngày nhu cầu, tối đa 10 cấp BOM. Có cân tồn bán thành phẩm, tồn an toàn, PO OPEN về kịp hạn; không lấy PO về sau ngày cần. Lô hết hạn/không RELEASED không khả dụng. Đây không phải MRP theo kỳ cân toàn bộ nhu cầu/đặt giữ WIP. Cần quy đổi BOM về đúng đơn vị trước khi nhập.

Lịch sản xuất là gợi ý cho một máy đã chọn, tránh bảo trì đã khai báo, không tự ghi lệnh điều khiển. OEE dùng planned_min, run_min, cycle_sec, total, good; giá trị hiệu suất vượt 100% có cảnh báo để kiểm tra chu kỳ máy.

Dữ liệu cảm biến nhập tay/CSV; có trạng thái NO_DATA/STALE/ALERT/IN_RANGE. Sơ đồ thiết bị chỉ phản ánh quan hệ cha-con nhập vào, không xác nhận cổng/vật lý. Quét LAN và IP/VPN cũ vẫn tách biệt.

Phân ca kiểm tra nhân sự hoạt động, kỹ năng bắt buộc còn hiệu lực suốt ca, trùng ca và lịch bảo trì đã nhập. Không thay thế chứng chỉ pháp lý hay interlock an toàn.

Điện năng là kWh trong khoảng giờ, không phải chỉ số công tơ tích lũy. Chi phí = kWh x đơn giá; CO2e = kWh x hệ số do người dùng cung cấp, bắt buộc nguồn/ngày. Thiếu hệ số hiện UNKNOWN, không coi bằng 0. Báo cáo không có chứng nhận ESG.

## 6. CSV, báo cáo và dữ liệu

Mẫu trống nằm trong `samples/smart_factory_templates/` hoặc nút Mẫu CSV. Xem `docs/FACTORY_DATA_DICTIONARY.md` để biết tên cột, đơn vị, trạng thái và tham chiếu. Nhập master trước chứng từ: vật tư trước BOM/lô, tài sản trước sensor, nhân sự trước chứng chỉ/ca.

CSV nhập tối đa 5 MB/2.000 dòng; cần đúng cột, không cột lạ, mã trùng. Cả lượt nhập được rollback khi một dòng sai. Nhập CSV là tạo bản ghi mới, không tự cập nhật mã cũ. Xuất UTF-8 BOM, phòng công thức CSV, không ghi đè tệp cũ. Tệp xuất báo cáo có thể có cột tính toán; không dùng thay mẫu nhập.

Xử lý tổng hợp cục bộ giới hạn 20.000 bản ghi mỗi loại/mỗi nhà máy; bản này không thế CSDL máy chủ cho tập đoàn. Không có xóa chứng từ trực tiếp; lô, mẫu đo, phiếu sản lượng/kiểm tra đã ghi sổ được bảo vệ khỏi sửa tùy ý.

## 7. Nơi lưu, sao lưu và khôi phục

`factory.sqlite3` nằm cùng thư mục `accounts.sqlite3`. Windows mặc định: `%LOCALAPPDATA%\AlibabaOperationsCenter`. Biến `ALIBABA_OPERATIONS_DATA` có thể đặt thư mục riêng trước khi mở ứng dụng. Không tự sao chép tài khoản giữa các máy.

**Smart Factory dùng CSDL mới, KHÔNG tự nhập, đồng bộ hay thay thế dữ liệu PMC cũ, Email hay ERP.** Chọn đúng workspace khi làm việc, tránh coi hai sổ là một nguồn tồn kho.

Nhóm 5 tạo snapshot SQLite cùng manifest/schema/SHA-256, kiểm tra toàn vẹn trước khi báo thành công. ZIP này **KHÔNG mã hóa** và chỉ chứa Smart Factory; không gồm tài khoản/mail/PMC cũ. Lưu trong vùng đã bảo vệ. Sao lưu hệ thống tài khoản và các phân hệ khác phải có quy trình riêng khi ứng dụng đã đóng.

Khôi phục chỉ tạo bản CSDL mới để kiểm tra, không thay CSDL hiện hành. Gói sai checksum, sai schema, có tệp lạ hoặc snapshot vượt 512 MB bị từ chối. Chỉ dùng bản sao tin cậy do mình tạo; checksum không thay chữ ký số. Việc đưa bản khôi phục vào vận hành cần dừng app, sao lưu bản hiện có và kiểm tra tài khoản/quyền tương ứng trước.

Audit có chuỗi SHA-256 để phát hiện thay đổi thông thường; chưa có neo bên ngoài, chưa mã hóa và không chống được người có toàn quyền hệ điều hành viết lại cả chuỗi.

## 8. Kiểm thử và phạm vi chưa nghiệm thu

Chạy `python -m unittest discover -s tests -v` trong thư mục ứng dụng. Các test GUI cần màn hình (hoặc Xvfb trên Linux). Báo cáo lần build này ghi rõ số bài, môi trường và giới hạn. `python app.py --self-test` kiểm tra khởi động/I/O/xác thực/CSDL mới bằng dữ liệu tạm, không kết nối mạng.

Chưa kiểm thử trên Windows/DPI 125%-150%, thiết bị/mạng nhà máy, ERP, mail thật hay build EXE. Chưa stress test 72 giờ, chưa có 800 test tiêu chí, SLA 99.99% hoặc chứng nhận ISO/NIST/ESG. Tên gói 500 triệu trong tài liệu yêu cầu không phải giá bán hay giá trị định giá bản này.

AI dự báo/Vision/chatbot, PLC/AGV, Mesh VPN, EDI, cloud, firewall/PDU, cảnh báo đa kênh, lịch gửi báo cáo, mobile/web và kéo-thả widget chưa được triển khai đầy đủ. Xem `DOI_CHIEU_100_PHAN_HE_V16_0_14.md` để kiểm tra từng mục. Không dùng bản này làm hệ thống liên động/an toàn thiết bị.
