# Báo cáo đối chiếu 400 mục tester — V13

**Chú ý:** 400 mục dưới đây là các tuyên bố/rủi ro trong văn bản tester. Chúng không phải 400 lỗi đã được tái hiện. Không có cơ sở để khẳng định tất cả đã được sửa.

## Số liệu phân loại

- `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON`: 89 mục
- `CHUA_DU_CHUNG_CU_XAC_NHAN`: 257 mục
- `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC`: 54 mục

**Đã xử lý/kiểm tra trên mã nguồn** nghĩa là có biện pháp bảo vệ, không phải cam kết đã kiểm tra thực tế tất cả tình huống.
**Không áp dụng/không bắt buộc** không phải lỗi triển khai. **Chưa đủ chứng cứ** cần log, test hoặc môi trường thật.

## Danh sách 400 mục

| # | Nội dung tester | Phân loại | Bằng chứng hoặc điều kiện tiếp theo |
|---:|---|---|---|
| 1 | Lỗi không chuyển mã trang màn hình console (\`chcp 65001\`) làm hỏng font hiển thị tiếng Việt trong quá trình cài đặt \`openpyxl\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | TAO_EXE_WINDOWS.bat dat chcp 65001; CMD khong can hien thi tieng Viet khi chay EXE. |
| 2 | Lỗi gọi trực tiếp lệnh \`py\` khi máy trạm cài nhiều bản Python nhưng bản mặc định không phải Python 3.x. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BAT uu tien py -3, fallback python va kiem tra phien ban. |
| 3 | Không kiểm tra quyền Administrator trước khi thực thi script batch ghi tệp vào hệ thống. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 4 | Lỗi thiếu kiểm tra kết nối Internet trước khi chạy lệnh \`pip install openpyxl\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 5 | Lỗi treo tiến trình ở lệnh \`pause\` khi ứng dụng chạy ngầm qua Task Scheduler. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 6 | Lỗi vỡ đường dẫn \`%~dp0\` khi thư mục cha chứa ký tự đặc biệt hoặc dấu ngoặc đơn/kép. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 7 | Thiếu kiểm tra biến môi trường \`ERRORLEVEL\` sau khi lệnh \`py app.py\` kết thúc để báo trạng thái exit code. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BAT kiem tra ERRORLEVEL sau moi buoc build va self-test. |
| 8 | Lỗi xung đột phiên bản \`openpyxl\` nếu hệ thống đã cài bản quá cũ/quá mới không tương thích. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | requirements-build.txt ghim phien ban. |
| 9 | Thiếu tham số \`--no-cache-dir\` khi cài pip làm phình to bộ nhớ đệm máy trạm. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 10 | Không có cờ dừng khẩn cấp (Emergency Cancel) khi người dùng lỡ bật nhầm file \`.bat\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 11 | Lỗi không tìm thấy \`app.py\` do thư mục làm việc (Working Directory) bị trỏ sang \`C:\Windows\System32\` khi Run as Administrator. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BAT chuyen cd /d "%~dp0" truoc khi chay. |
| 12 | Lỗi không ghi log ra tệp riêng cho quá trình cài đặt phụ thuộc từ file \`.bat\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BUILD_V13.log ghi ket qua pip va PyInstaller. |
| 13 | Lỗi xung đột nếu người dùng nhấp đúp file \`.bat\` nhiều lần tạo ra nhiều tiến trình \`app.py\` chạy đè lên nhau. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | exclusive_backup_lock khoa thu muc dich giua cac tien trinh. |
| 14 | Không tự động phát hiện và cảnh báo nếu Python chưa được thêm vào biến môi trường \`PATH\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BAT kiem tra Python 3.10+ tren may build. |
| 15 | Lỗi dùng đường dẫn cứng không linh hoạt cho các tham số đầu vào của Python. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 16 | Lỗi thiếu cờ \`--quiet\` khi cài pip khiến màn hình console bị tràn thông báo rác. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 17 | Thiếu thông báo hướng dẫn xử lý sự cố bằng tiếng Việt khi pip bị chặn bởi Firewall công ty. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 18 | Không dọn dẹp các tệp cài đặt đệm (\`.whl\`, \`.tar.gz\`) sau khi hoàn tất. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 19 | Lỗi tương thích đường dẫn tương đối khi gọi \`SAP_XEP_EMAIL_CU.bat\` từ một thư mục khác. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Script sap xep cu khong nam trong bo phan phoi. |
| 20 | Thiếu kiểm tra dung lượng ổ đĩa \`C:\` trước khi nạp thêm thư viện Python. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 21 | Lỗi không bắt tín hiệu ngắt \`Ctrl+C\` khiến tiến trình cài đặt dở dang làm hỏng thư viện \`site-packages\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 22 | Sử dụng \`cd /d\` nhưng không kiểm tra sự tồn tại của ổ đĩa mục tiêu. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 23 | Không hiển thị banner thông tin phiên bản (\`V12\`) ở đầu cửa sổ lệnh. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | VERSION 13.0.0 va banner builder. |
| 24 | Lỗi chạy file \`.bat\` trên Windows Server do chính sách PowerShell/CMD bị chặn execution policy. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 25 | Không kiểm tra mã băm Hash (SHA256) của file \`app.py\` trước khi thực thi để tránh bị chèn mã độc. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 26 | Lỗi ghi trực tiếp tệp log ra thư mục gốc mà không có quyền ghi (\`Access Denied\`). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 27 | Thiếu cơ chế tự động thử lại (Retry Loop) nếu lệnh \`pip install\` bị ngắt kết nối giữa chừng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 28 | Lỗi ghi đè biến môi trường toàn cục gây ảnh hưởng đến các ứng dụng Python khác trên cùng máy. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 29 | Lỗi không tương thích khi máy tính cài đặt Python 32-bit trên OS 64-bit. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 30 | Không tự động đóng cửa sổ CMD khi chương trình Python kết thúc thành công. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 31 | Thiếu mã màu ANSI để phân biệt thông báo Lỗi (Đỏ) và Thành công (Xanh) trên console. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 32 | Lỗi đọc sai tham số truyền từ lệnh CMD do lệch bảng mã \`cp1252\` và \`UTF-8\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 33 | Không kiểm tra sự tồn tại của file cấu hình \`.env\` trước khi gọi \`app.py\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 34 | Lỗi thiếu tệp \`vcruntime140.dll\` khi chạy Python trên máy Windows sạch chưa cài Visual C++ Redistributable. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 35 | Thiếu kịch bản Ping kiểm tra sơ bộ máy chủ Alibaba Mail (\`imap.mxhichina.com\`) trước khi khởi chạy \`app.py\`. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong can ping; ICMP co the bi chan du IMAP 993 hoat dong. |
| 36 | Không lưu vết thời gian khởi chạy (Timestamp) vào tệp log của hệ thống batch. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Nhat ky logging co moc thoi gian. |
| 37 | Lỗi lạm dụng các lệnh CMD đã bị loại bỏ trên các bản Windows 11 mới nhất. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 38 | Lỗi không tự động tạo thư mục \`logs/\` trước khi thực thi \`app.py\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Tao thu muc _NHAT_KY truoc khi ghi log. |
| 39 | Thiếu kiểm tra xem cổng mạng nội bộ có bị chiếm dụng bởi ứng dụng khác hay không. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong mo local listening TCP port. |
| 40 | Lỗi đơ màn hình console khi Windows Defender bật hộp thoại quét file \`.bat\` thời gian thực. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 41 | Tệp \`TEST_V12.py\` thiếu kiểm tra ranh giới dữ liệu (Edge Cases) đối với email có dung lượng 0 byte. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 42 | Dữ liệu giả lập trong test không phản ánh đúng cấu trúc Header phức tạp của Alibaba Mail. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 43 | Thiếu xử lý ngoại lệ khi thử nghiệm kết nối với hòm thư thử nghiệm bị khóa hoặc hết hạn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 44 | Lỗi đếm sai số lượng email đã phân loại thành công trong \`TEST_V11.py\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 45 | Không xóa dữ liệu rác phát sinh sau khi chạy \`TEST_V12.py\` làm bẩn thư mục lưu trữ thật. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Toan bo bai thu mock tao du lieu tai thu muc tempfile.TemporaryDirectory. |
| 46 | Lỗi phân tích cú pháp chuỗi trả về từ \`TEST_TEN_DUONG_DAN.py\` khi đường dẫn chứa ký tự Unicode đặc biệt. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 47 | Thiếu ca test kiểm tra hòm thư có chứa hơn 100.000 email (Scale Test). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 48 | Vòng lặp chờ phản hồi trong file test không có Timeout khiến file test bị treo vĩnh viễn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 49 | Không ghi Stack Trace chi tiết ra file khi bài test gặp lỗi bất ngờ (\`Unexpected Crash\`). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 50 | Lỗi so sánh kiểu dữ liệu giữa \`str\` và \`int\` trong các hàm assert tự động của file test. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 51 | Không hỗ trợ xuất báo cáo kết quả test ra định dạng HTML hoặc JUnit XML. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 52 | Lỗi rò rỉ RAM sau khi chạy liên tiếp các ca test trong \`TEST_V12.py\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 53 | Trùng tên hàm test giữa \`TEST_V11.py\` và \`TEST_V12.py\` khi import chung vào một runner. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 54 | Lỗi kiểm tra sai bảng mã mã hóa của file \`KET_QUA_TEST.txt\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 55 | Giả lập độ trễ mạng quá ngắn (1ms) trong file test không phản ánh đúng độ trễ máy chủ Alibaba (100-300ms). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 56 | Thiếu ca test xử lý tên file đính kèm chứa khoảng trắng liên tiếp hoặc dấu chấm đúp (\`..\`). | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | test_v13.py kiem thu ten tep trung lap va Unicode. |
| 57 | Lỗi vỡ đường dẫn dài vượt quá 260 ký tự (\`MAX_PATH\`) trong \`TEST_TEN_DUONG_DAN.py\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | test_v10.py test gioi han duong dan Windows. |
| 58 | Thiếu ca test mất kết nối Internet đột ngột giữa chừng khi đang tải attachment trong \`TEST_KHONG_CAN_EMAIL.py\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | test_v13.py test OSError do gian doan ghi file. |
| 59 | Không tự động khôi phục trạng thái hệ thống trước khi test (Test Clean Teardown). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 60 | Không có cơ chế so sánh sai lệch kết quả (Diffing) giữa báo cáo V11 và V12. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 61 | Sử dụng thư viện test cũ (\`unittest\` cơ bản) thiếu các tính năng nâng cao của \`pytest\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 62 | Không test trường hợp file cấu hình \`.env\` bị hỏng cấu trúc syntax. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 63 | Lỗi parse sai định dạng ngày tháng ISO 8601 trong file log của bài test. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 64 | Lộ mật khẩu/token dùng thử trực tiếp trong mã nguồn của file \`TEST_V12.py\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 65 | Không kiểm tra hạn ngạch ổ đĩa khi chạy bài test tạo tệp dung lượng lớn. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | test_v13.py test noi luu khong du SHA la khong duoc skip. |
| 66 | Vòng lặp test tiêu tốn 100% CPU do dùng \`while True\` không nghỉ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 67 | Thiếu Docstring giải thích mục tiêu của từng hàm test trong \`TEST_V12.py\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 68 | Lỗi xung đột tên biến toàn cục khi \`TEST_V12.py\` import trực tiếp từ \`app.py\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 69 | Không test trường hợp quyền truy cập file output bị đặt là Read-Only. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | test_v13.py test tep thieu va cap nhat lai. |
| 70 | Lỗi lệch lệch múi giờ UTC vs Local khi ghi mốc thời gian chạy test. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 71 | Thiếu kiểm tra cấu trúc định dạng file báo cáo Markdown \`BAO_CAO_SUA_LOI_V12.md\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 72 | Lỗi không bắt được ngoại lệ \`PermissionError\` khi file test cố gắng đọc file đang bị Excel mở. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 73 | Cấu trúc câu lệnh \`if/else\` lồng nhau quá 5 cấp trong \`kiem_tra.py\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 74 | Không loại bỏ email trùng lặp (Duplicate Message-ID) trong bộ dữ liệu test. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 75 | Thiếu phân loại mức độ nghiêm trọng (Severity Level) cho các lỗi test phát hiện. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 76 | Kết quả test không được đẩy tự động vào hệ thống quản lý log tập trung. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 77 | Giả lập phản hồi API Alibaba Mail không cập nhật các mã lỗi mới từ Aliyun SDK. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong su dung Alibaba Cloud REST API cho danh ba. |
| 78 | Không test trường hợp hệ thống thiếu RAM khi chạy ứng dụng trên máy ảo cấu hình yếu. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 79 | Lỗi lệch cột khi in kết quả test dạng bảng ra giao diện dòng lệnh. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 80 | Không test tính năng tự động sắp xếp thư cũ (\`sap_xep_email_cu.py\`) với các file mail định dạng \`.eml\` bị lỗi cấu trúc. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 81 | Thư mục dự án chứa tới 9 file hướng dẫn rác (\`HUONG_DAN_V4\` đến \`V12\`), gây rối loạn cho người bảo trì. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Release chi giu README.md; tai lieu lich su khong dong goi. |
| 82 | Mã nguồn ứng dụng chính (\`app.py\`), script test, file batch và báo cáo audit nằm lẫn lộn ở root directory. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Backend app va tests tach thu muc. |
| 83 | Tài liệu cập nhật bị phân tán, không gộp chung vào một tệp \`DOCUMENTATION.md\` thống nhất. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | README.md gom huong dan hien hanh. |
| 84 | Tên file trong gói trộn lẫn tiếng Việt không dấu, có dấu, viết hoa, viết thường và từ tiếng Anh. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 85 | Thiếu file \`__init__.py\` ở thư mục gói khiến Python không nhận diện đây là một module chuẩn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 86 | Phụ thuộc vòng tròn giữa \`app.py\` và các module tiện ích con. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 87 | Tham số cấu hình kết nối mạng bị hardcode trong \`app.py\` thay vì đọc hoàn toàn từ \`config.json\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 88 | Các file kết quả test (\`KET_QUA_TEST.txt\`) xả trực tiếp ra thư mục gốc thay vì thư mục \`logs/\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 89 | Thiếu file \`README.md\` mô tả cách cài đặt và kiến trúc hệ thống chuẩn. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | README.md cung cap setup va scope. |
| 90 | Đóng gói dư thừa các file tạm, file log cũ vào tệp nén \`.zip\` phân phối cho khách hàng. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | File ZIP bo cac goi EXE/test du lieu cu. |
| 91 | Mã nguồn không tuân thủ quy chuẩn đặt tên và định dạng của PEP 8. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 92 | Sử dụng quá nhiều biến toàn cục (\`global\`) trong \`app.py\` gây rò rỉ trạng thái giữa các phiên chạy. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 93 | Thiếu cơ chế Semantic Versioning (ví dụ: \`v12.0.1\`) trong mã nguồn ứng dụng. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | VERSION trong mail_backend.py. |
| 94 | Các file báo cáo \`.md\` không được tích hợp công cụ tự động cập nhật số liệu khi build. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 95 | Thiếu sự phân tách giữa tầng logic xử lý mail (Business Logic) và tầng giao diện console (UI). | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | app.py tach GUI voi mail_backend.py. |
| 96 | Thiếu file \`requirements.txt\` ghim rõ phiên bản các thư viện phụ thuộc (\`openpyxl==3.1.2\`). | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | requirements-build.txt ghim phien ban. |
| 97 | Script \`sap_xep_email_cu.py\` đứng độc lập, không thể gọi trực tiếp từ giao diện chính của \`app.py\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 98 | Thiếu file \`.gitignore\` chuẩn cho dự án Python khi đưa lên Git. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | .gitignore duoc bo sung. |
| 99 | File \`HUONG_DAN_SUA_DUONG_DAN.txt\` phản ánh thiết kế đường dẫn tĩnh thiếu linh hoạt ngay từ đầu. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 100 | Thiếu sơ đồ kiến trúc luồng dữ liệu (Data Flow Diagram) trong tài liệu kỹ thuật. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 101 | Lặp lại cùng một đoạn mã xử lý file Excel ở 3 file khác nhau (\`app.py\`, \`TEST_V11.py\`, \`TEST_V12.py\`). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 102 | Không có lớp quản lý ngoại lệ riêng (\`Custom Exceptions\`) cho ứng dụng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 103 | Phụ thuộc vào các thư viện bên ngoài mà không có phương án thay thế bằng thư viện chuẩn (Standard Library). | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong co HTTP REST XML/JSON input parser. |
| 104 | Thiếu Namespace cô lập cho các hàm tiện ích xử lý chuỗi. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 105 | File thực thi Batch và file mã nguồn Python để chung một thư mục gây nhầm lẫn khi thao tác. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 106 | Không có script tự động kiểm tra cấu hình phần cứng trước khi cài đặt. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 107 | File \`HUONG_DAN_CHAY_MAY_KHAC.txt\` nội dung quá ngắn, thiếu hướng dẫn khắc phục sự cố mạng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 108 | Không quy định bảng mã mã hóa thống nhất (UTF-8 No BOM) cho toàn bộ file nguồn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 109 | Thiếu file \`.env.example\` hướng dẫn người dùng khai báo biến môi trường. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 110 | Mật khẩu và thông tin tài khoản vẫn bị lưu dạng văn bản thô nếu người dùng cấu hình sai. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 111 | Thiếu file cấu hình đóng gói \`.spec\` cho PyInstaller. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | SaoLuuAlibabaMailV13.spec co trong ZIP. |
| 112 | File \`CHANGELOG.md\` không được duy trì để theo dõi các thay đổi qua từng phiên bản. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | CHANGELOG.md theo doi nhung thay doi. |
| 113 | Chứa các file script thử nghiệm cũ không còn giá trị sử dụng nhưng không được xóa bỏ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 114 | Thiếu hàm kiểm tra tính toàn vẹn của thư mục tài nguyên khi ứng dụng bắt đầu chạy. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 115 | Tổng dung lượng các file tài liệu hướng dẫn văn bản thô chiếm tỉ lệ quá lớn trong gói ZIP. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 116 | Không đồng bộ cách đặt tên hàm (vừa camelCase vừa snake_case). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 117 | Không có quy hoạch cấu trúc thư mục chứa file đầu ra (\`output/emails/\`, \`output/excel/\`). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 118 | Thiếu công cụ quét an toàn mã nguồn tự động (Bandit) tích hợp trong gói. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 119 | Phụ thuộc quá nhiều vào tài liệu dạng text thay vì xây dựng giao diện CLI trợ giúp (\`--help\`). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 120 | Thiếu cơ chế tự động khôi phục file cấu hình mặc định khi file cấu hình bị hỏng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 121 | Mật khẩu email doanh nghiệp lưu trữ dạng Plaintext trong file cấu hình cục bộ. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Khong luu mat khau ra config; nhap qua hop thoai bao mat. |
| 122 | Thiếu cơ chế mã hóa AES-256 cho các dữ liệu nhạy cảm lưu đĩa. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong bat buoc ma hoa AES-256: khac yeu cau va dung luong co the can BitLocker. |
| 123 | Ghi toàn bộ Header và Body email chứa thông tin cá nhân vào file log không mã hóa. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Nhat ky khong ghi email body hay attachment bytes. |
| 124 | Không hỗ trợ phương thức xác thực OAuth2 / App Password mã hóa của Alibaba Cloud. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | OAuth2 Alibaba Mail khong duoc su dung trong phuong thuc IMAP app password. |
| 125 | Sử dụng tùy chọn vô hiệu hóa kiểm tra SSL (\`verify=False\`) khi gọi API kết nối. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | ssl.create_default_context xac minh chung chi. |
| 126 | Dữ liệu tài khoản truyền qua kênh mạng nội bộ không được mã hóa TLS. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | IMAP SSL/TLS cong 993; minimum TLS 1.2. |
| 127 | Không có cơ chế giới hạn số lần thử đăng nhập (Rate Limiting) chống brute-force mật khẩu. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Dung thong tin hop le; rate limit dang nhap phia server kiem soat. |
| 128 | Dữ liệu từ email (Subject, Sender) không được làm sạch trước khi đưa vào câu lệnh SQL/File. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | clean() loc ky tu cam va ten Windows dac biet. |
| 129 | Báo cáo kiểm toán tiết lộ cấu trúc đường dẫn thư mục nội bộ của máy phát triển. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 130 | Biến chứa mật khẩu trong Python RAM không được chủ động xóa sạch khỏi bộ nhớ sau khi dùng. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong the xoa hoan toan chuoi Python immutable khoi RAM. |
| 131 | Bỏ qua việc xác thực x509 Certificate của máy chủ Alibaba Mail. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Khong tat xac thuc chung chi x509. |
| 132 | Dùng thư viện \`random\` để tạo chuỗi ngẫu nhiên thay vì \`secrets\` bảo mật. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 133 | Phân quyền file cấu hình nhạy cảm ở mức \`777\` hoặc \`Everyone\` trên Windows. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 134 | Thiếu kiểm tra quyền thực thi script đối với user hệ thống hiện tại. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 135 | File log giao dịch mail lưu thông tin kinh doanh bí mật nhưng không đặt mật khẩu bảo vệ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 136 | Không tự động đăng xuất phiên làm việc khi ứng dụng treo ở trạng thái chờ quá lâu. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung sao luu theo phien, khong giu IMAP IDLE dai han. |
| 137 | Trả về thông tin phiên bản chi tiết của thư viện Python khi phát sinh ngoại lệ mạng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 138 | Tệp đính kèm nén (\`.zip\`, \`.rar\`) tải về không được quét virus hoặc kiểm tra Zip Bomb. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung tai tep, khong giai nen hay thuc thi file dinh kem. |
| 139 | Mở cổng kết nối ra ngoài mà không giới hạn địa chỉ IP được phép truy cập. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Client chi ket noi outbound, khong mo port listen. |
| 140 | Tệp thực thi \`app.py\` không được kiểm tra chữ ký số trước khi thực thi. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ky EXE la buoc phan phoi cua don vi, khong co secret key de self-sign. |
| 141 | Bản sao lưu email cũ không được mã hóa đặt trong thư mục công cộng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 142 | Không yêu cầu mật khẩu xác thực người dùng khi mở ứng dụng giao diện. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Mat khau email da la co che xac thuc; mat khau mo app la yeu cau them. |
| 143 | Token phiên làm việc bị ghi tạm ra file không mã hóa trong thư mục \`%TEMP%\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 144 | Không phát hiện và cảnh báo khi có hoạt động đăng nhập song song từ IP lạ vào Alibaba Mail. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Phat hien IP la la dich vu quan tri email, khong thuoc client IMAP. |
| 145 | Sử dụng giao thức kết nối SSL v3 / TLS 1.0 đã bị loại bỏ vì lỗ hổng bảo mật. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | SSL context minimum TLS 1.2. |
| 146 | Không gửi cảnh báo về email quản trị khi tài khoản bị khóa do nghi ngờ bị tấn công. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung khong gui SMTP canh bao. |
| 147 | Lộ IP nội bộ và tên máy trạm trong thông điệp nhật ký gửi đi. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 148 | Các đường dẫn URL trong email không được kiểm tra an toàn trước khi tự động truy cập. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung khong tu dong truy cap link trong email. |
| 149 | Phân quyền thư mục chứa file SQLite lịch sử quá lỏng lẻo. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 150 | Không kiểm tra chữ ký SHA256 khi ứng dụng tự động tải bản vá từ xa. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung khong tu dong tai ban cap nhat. |
| 151 | Khóa mã hóa file được lưu nằm ngay cạnh file dữ liệu mã hóa. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 152 | Không bắt ngoại lệ an toàn khi Aliyun API trả về lỗi xác thực \`InvalidAccessKeyId\`. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung khong goi Aliyun Cloud AccessKey API. |
| 153 | Lộ tên tài khoản Admin trên màn hình console khi ứng dụng gặp sự cố. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 154 | Thiếu cơ chế kiểm tra file cấu hình có bị chỉnh sửa bởi phần mềm độc hại hay không. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 155 | Dùng thuật toán băm yếu (MD5/SHA1) để tạo ID kiểm tra dữ liệu mail. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 156 | Không kiểm tra và chặn các thao tác can thiệp phần cứng trái phép. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung khong tuong tac phan cung nhung. |
| 157 | Chuỗi chứa thông tin đăng nhập bị lưu trong đĩa swap (\`pagefile.sys\`) của Windows. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Quan ly pagefile thuoc Windows, khong the bao dam xoa RAM Python. |
| 158 | Lỗi Path Traversal: Tiêu đề mail chứa \`../\` có thể ghi đè file hệ thống ngoài thư mục sao lưu. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | metadata saved_name va duong dan tao ra duoc kiem tra. |
| 159 | Biến môi trường chứa secret key không được mã hóa trong bộ nhớ tiến trình. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 160 | Thiếu tài liệu hướng dẫn quy trình tuân thủ an toàn thông tin doanh nghiệp. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 161 | Không đóng kết nối IMAP/POP3 sau khi hoàn thành tiến trình quét thư làm rò rỉ Socket Handle. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | _close() dong ket noi ngay ca khi loi. |
| 162 | Đọc toàn bộ nội dung file log dung lượng lớn vào RAM bằng \`.read()\` thay vì duyệt theo dòng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 163 | Không giải phóng dung lượng của các biến danh sách chứa hàng nghìn đối tượng email. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 164 | Sử dụng danh sách (\`list\`) thay vì tập hợp (\`set\`) để tìm kiếm email trùng lặp, gây giảm hiệu năng từ $O(1)$ xuống $O(n)$. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | UID duoc doi chieu bang set/dict. |
| 165 | Tràn bộ nhớ RAM khi tải file đính kèm email dung lượng lớn (trên 500MB). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 166 | Mở file ghi log trong vòng lặp mà không dùng bộ quản lý ngữ cảnh \`with\`, gây hết File Descriptor. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 167 | Vòng lặp chờ phản hồi từ máy chủ tiêu tốn 100% CPU do thiếu khoảng nghỉ \`time.sleep()\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 168 | Không giới hạn số lượng luồng chạy đồng thời khi tải email, gây sập bộ nhớ máy trạm. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | UI cho toi da 5 worker; tung worker co IMAP rieng. |
| 169 | Không dọn dẹp các Thread đã kết thúc khiến bộ nhớ RAM bị phình to liên tục. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | ThreadPoolExecutor tat worker truoc khi return. |
| 170 | Không xóa các file tạm \`.tmp\` sinh ra trong quá trình sắp xếp mail cũ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 171 | Tạo chuỗi ký tự lặp đi lặp lại trong vòng lặp bằng toán tử \`+\` thay vì \`join()\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 172 | Không gọi hàm \`gc.collect()\` để thu gom rác sau khi xử lý xong một khối email lớn. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Python co GC; goi gc.collect moi email khong bat buoc va gay cham. |
| 173 | Ghi từng dòng dữ liệu xuống ổ đĩa thay vì sử dụng bộ đệm (Buffer) làm giảm tuổi thọ SSD. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 174 | Thiếu kiểm tra dung lượng ổ đĩa còn trống trước khi thực hiện sao lưu hàng loạt. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | _save_one kiem tra disk free truoc khi ghi. |
| 175 | Bộ phân tích cú pháp HTML (BeautifulSoup/lxml) bị tràn bộ nhớ khi gặp file email HTML dị dạng. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung khong phan tich HTML bang BeautifulSoup/lxml. |
| 176 | Không đóng kết nối cơ sở dữ liệu SQLite sau khi tra cứu xong lịch sử sao lưu. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 177 | Không giới hạn băng thông tải xuống làm nghẽn toàn bộ đường truyền mạng nội bộ nhà máy. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | RateLimiter dung chung cac worker theo tai khoan. |
| 178 | Không đánh Index cho bảng dữ liệu SQLite khiến tốc độ tra cứu email cũ bị chậm. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 179 | Tiến trình bị treo và giữ nguyên các file bị khóa khi người dùng tắt đột ngột ứng dụng. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Dang dong cua so -> set stop; cho worker ket thuc. |
| 180 | Chạm giới hạn số lượng file mở đồng thời của Windows (\`1024\` file handle). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 181 | Phân mảnh bộ nhớ do cấp phát liên tục các mảng \`bytearray\` kích thước lớn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 182 | Không bật chế độ ghi đệm (\`buffering\`) cho các thao tác ghi file log dung lượng lớn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 183 | Tiến trình con vẫn chạy ngầm chiếm tài nguyên CPU sau khi cửa sổ ứng dụng chính đã đóng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 184 | Tệp nhật ký phình to quá 10GB làm ngưng trệ toàn bộ hệ thống do đĩa bị đầy. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | RotatingFileHandler 3MB x 5 files. |
| 185 | Các đối tượng thư viện bên thứ ba không giải phóng bộ nhớ C-Extension sau khi dùng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 186 | Không đo độ trễ mạng để điều chỉnh số lượng kết nối đồng thời cho phù hợp. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 187 | Chuyển đổi qua lại vô ích giữa \`bytes\` và \`str\` gây tốn năng lượng xử lý của CPU. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 188 | Sử dụng các biểu thức chính quy Regex không tối ưu gây ra Catastrophic Backtracking. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 189 | Tràn RAM khi xuất báo cáo danh sách email ra file Excel lớn bằng \`openpyxl\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 190 | Không làm sạch DNS Cache khiến ứng dụng kết nối tới IP máy chủ cũ khi IP đổi. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | DNS cache do he dieu hanh quan ly, khong co custom cache. |
| 191 | Khóa đồng bộ \`threading.Lock()\` bị treo vĩnh viễn do một luồng bị Crash mà không nhả Lock. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | exclusive_backup_lock va safe_write co with/finally. |
| 192 | Không kiểm tra tài nguyên CPU/RAM hiện tại trước khi bắt đầu tác vụ nặng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 193 | Cấp phát bộ nhớ thất bại (\`MemoryError\`) nhưng không có cơ chế bắt ngoại lệ để lưu dữ liệu dở dang. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 194 | Duyệt qua toàn bộ file email từ đầu đến cuối thay vì chỉ quét các thư phát sinh mới. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Chi tai lai UID chua co ban xac minh. |
| 195 | Rò rỉ Socket khi kết nối mạng bị Reset giữa chừng do tường lửa ngắt. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Socket IMAP dong trong finally va khi retry. |
| 196 | Trình biên dịch Bytecode Python ngốn bộ nhớ trên các máy tính cấu hình RAM dưới 2GB. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung nhung Python runtime, khong bien dich bytecode luc chay moi lan. |
| 197 | Không tự dọn dẹp bộ nhớ đệm tạm tại thư mục \`C:\Users\Username\AppData\Local\Temp\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 198 | Tốc độ ghi đĩa bị nghẽn do ghi nhiều file kích thước cực nhỏ (vài KB) liên tục. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 199 | Rò rỉ Handle tiến trình khi gọi lệnh \`subprocess.Popen\` mà không gọi \`.communicate()\` hay \`.wait()\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 200 | Không chuyển ứng dụng sang trạng thái rảnh rỗi (Low Power Mode) khi không có tác vụ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 201 | In chữ tiếng Việt ra cửa sổ CMD bị lỗi hiển thị ký tự rác do chưa đổi sang bảng mã \`65001\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BAT chcp 65001; GUI Unicode Tk. |
| 202 | Xảy ra ngoại lệ \`UnicodeDecodeError\` khi đọc file cấu hình lưu bằng mã hóa \`ANSI\`/\`Windows-1252\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 203 | Mất hoàn toàn dấu tiếng Việt khi lưu tiêu đề email vào file/CSDL không đặt mã hóa \`UTF-8\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Metadata JSON UTF-8; CSV utf-8-sig. |
| 204 | Cắt chuỗi tiếng Việt có dấu bị hỏng ký tự do tính độ dài theo \`bytes\` thay vì số ký tự. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 205 | Đường dẫn thư mục lưu trữ chứa tiếng Việt có dấu làm các hàm \`os.path\` cũ bị lỗi \`FileNotFoundError\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 206 | File cấu hình chứa ký tự lạ (BOM \`\ufeff\`) làm khóa cấu hình đầu tiên bị đọc sai. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 207 | Gọi hàm \`.decode('utf-8')\` trên chuỗi dữ liệu byte bị lỗi mà không dùng tham số \`errors='ignore'\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 208 | Mật khẩu chứa ký tự đặc biệt (\`#\`, \`&\`, \`%\`, \`\\`) bị lỗi cú pháp khi đưa vào URL kết nối. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 209 | Biểu thức Regex không nhận diện được ký tự xuống dòng dạng Windows (\`\r\n\`). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 210 | Định dạng ngày tháng hiển thị dạng \`MM/DD/YYYY\` gây nhầm lẫn cho người Việt quen dùng \`DD/MM/YYYY\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 211 | Tên file đính kèm chứa các ký tự cấm của Windows (\`\\`, \`/\`, \`:\`, \`*\`, \`?\`, \`"\`, \`<\`, \`>\`, \`\|\`) gây lỗi lưu file. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | clean() loai ky tu filename khong hop le. |
| 212 | Không đọc được file email lưu ở dạng mã hóa UTF-16 LE/BE. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 213 | So sánh chuỗi địa chỉ email không đưa về dạng chữ thường (\`.lower()\`), làm sót dữ liệu trùng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 214 | Cắt cụt tiêu đề mail quá dài làm vỡ cấu trúc chuỗi UTF-8 đa byte ở vị trí giữa ký tự. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 215 | File log chứa các mã màu ANSI (\`\033[92m\`) làm file log văn bản thuần bị bẩn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 216 | Truy vấn URL chứa chữ tiếng Việt có dấu không qua hàm \`urllib.parse.quote()\`. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung khong goi HTTP URL. |
| 217 | Parse số thực bị lỗi do lệch dấu chấm \`.\` và dấu phẩy \`,\` giữa chuẩn Việt Nam và Quốc tế. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 218 | Đường dẫn file Windows bị lỗi Escape Character do thiếu tiền tố Raw String \`r"..."\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 219 | File JSON cấu hình chứa ký tự Tab/Xuống dòng thuần túy làm bộ parse JSON báo lỗi Syntax Error. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 220 | Giá trị cấu hình rỗng \`""\` khi convert sang kiểu số bị ném ngoại lệ \`ValueError\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 221 | Xuất file CSV tiếng Việt mở bằng Excel bị lỗi font do thiếu thẻ Unicode BOM (\`\xef\xbb\xbf\`). | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | CSV bao cao dung utf-8-sig. |
| 222 | Thông báo lỗi hiển thị dịch ngữ vụng về, pha trộn giữa tiếng Anh và tiếng Việt. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 223 | Tên thư mục trong Alibaba Mail chứa tiếng Trung phồn thể/giản thể bị đọc thành ký tự \`???\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | readable_mailbox() giai ma IMAP modified UTF-7. |
| 224 | Không đọc được các định dạng email cổ mã hóa theo chuẩn TCVN3 hoặc VNI-Windows. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Tep .eml duoc luu nguyen ban, khong can chuyen TCVN3 sang Unicode. |
| 225 | Ép kiểu dữ liệu chuỗi sang số nguyên không bắt ngoại lệ khi dữ liệu bị lẫn chữ cái. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 226 | Độ dài đường dẫn tệp sao lưu vượt quá giới hạn 260 ký tự của hệ điều hành Windows cổ điển. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | named_destination() gioi han duong dan va giu UID khi rut gon. |
| 227 | Không gọt dũa khoảng trắng thừa (\`.strip()\`) ở hai đầu tài khoản/mật khẩu do người dùng nhập vào. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 228 | Biểu tượng tiền tệ (\`₫\`, \`$\`, \`¥\`) trong email bị biến thành ký tự lạ khi xuất báo cáo. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 229 | Regex kiểm tra email bị bỏ sót các TLDs tên miền mới (như \`.tech\`, \`.furniture\`, \`.online\`). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 230 | Giao diện ứng dụng không hỗ trợ chuyển đổi đa ngôn ngữ (Việt - Anh - Trung). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 231 | Tiêu đề email mã hóa dạng MIME RFC 2047 (\`=?UTF-8?B?...?=\`) giải mã ra bị mất khoảng trắng giữa các từ. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | decoded() su dung email.header.make_header. |
| 232 | Mở file ghi log bằng hàm \`open()\` mặc định của hệ thống mà không khai báo \`encoding='utf-8'\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | RotatingFileHandler encoding=UTF-8. |
| 233 | Biểu tượng Emoji trong tiêu đề mail làm sập hệ thống lưu trữ không hỗ trợ UTF-8 4-byte (\`utf8mb4\`). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 234 | Hàm \`datetime.strptime()\` bị sập khi gặp tên tháng bằng tiếng Anh trên hệ điều hành cài ngôn ngữ tiếng Việt. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 235 | Dữ liệu sao chép từ Web chứa ký tự Zero-Width Space (\`\u200b\`) làm sai lệch mật khẩu nhập vào. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 236 | Văn bản thông báo tiếng Việt dài làm tràn vỡ các ô khung hiển thị trên giao diện Console. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 237 | Tên biến cấu hình dùng lẫn lộn giữa dấu gạch ngang \`-\` và gạch dưới \`_\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 238 | Ký tự mã hóa HTML (\`&lt;\`, \`&gt;\`, \`&amp;\`) trong body email không được Unescape khi lưu ra text. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 239 | Đường dẫn truyền qua CLI chứa khoảng trắng không được bao bọc trong dấu câu kép \`""\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BAT quote tat ca duong dan co khoang trang. |
| 240 | Bảng mã file Batch (\`cp1252\`) và file Python (\`UTF-8\`) lệch nhau làm truyền tham số bị lỗi font. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 241 | Không có cơ chế tự động thử lại (Retry) với độ trễ tăng dần (Exponential Backoff) khi kết nối mạng ngắt. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | _worker toi da 4 lan thu, co backoff exponential. |
| 242 | Không đặt tham số \`timeout\` cho lệnh kết nối Socket, khiến chương trình bị treo vô thời hạn. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | IMAP4_SSL dat timeout 45 giay. |
| 243 | Bỏ qua không bắt ngoại lệ \`socket.gaierror\` khi máy trạm bị mất kết nối DNS. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 244 | Thiếu cơ chế Circuit Breaker dừng gửi yêu cầu khi máy chủ Alibaba báo lỗi liên tục \`500 Internal Server Error\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 245 | Bỏ qua không xử lý mã lỗi HTTP \`429 Too Many Requests\` từ máy chủ API Aliyun. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong su dung Aliyun HTTP API. |
| 246 | Không hỗ trợ kết nối qua máy chủ Proxy NTLM/SOCKS5 của mạng doanh nghiệp. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 247 | Mất kết nối IMAP IDLE do không gửi gói tin Keep-Alive (\`NOOP\`) sau mỗi 29 phút. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong dung IMAP IDLE. |
| 248 | Không tự động thử kết nối lại khi địa chỉ IP máy trạm bị thay đổi (đổi Wifi/mạng LAN). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 249 | Tràn bộ đệm nhận dữ liệu khi máy chủ trả về danh sách 50.000 email cùng một lúc. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 250 | Thiếu cờ \`SO_REUSEADDR\` làm cổng kết nối bị khóa trong trạng thái \`TIME_WAIT\` sau khi tắt ứng dụng. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong mo local TCP listening socket. |
| 251 | Bỏ qua ngoại lệ \`ConnectionResetByPeer\` làm chương trình dừng đột ngột không lưu vệt lỗi. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | _worker retry OSError/socket/SSL; dong socket cu. |
| 252 | Gửi dữ liệu yêu cầu khi bắt tay SSL/TLS chưa hoàn tất hoàn toàn. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | imaplib.IMAP4_SSL dam bao bat tay TLS truoc khi gui command. |
| 253 | Truyền tài khoản và mật khẩu qua cổng kết nối không mã hóa (Port 110 POP3 / Port 25 SMTP). | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong su dung POP3/SMTP plaintext. |
| 254 | Không đối chiếu kích thước file tải về với trường \`Content-Length\` trong HTTP Header. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong tai qua HTTP Content-Length. |
| 255 | Bị kẹt trong vòng lặp chuyển hướng HTTP (\`Too many redirects\`) khi gọi API. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong su dung HTTP redirect. |
| 256 | Báo lỗi không rõ ràng khi người dùng cấu hình sai cổng kết nối IMAP SSL (nhầm 993 thành 143). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 257 | Tải file đính kèm trực tiếp vào bộ nhớ thay vì ghi luồng (\`stream=True\`) xuống ổ đĩa. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 258 | Lệch đồng hồ hệ thống (\`System Clock Skew\`) quá 15 phút làm chữ ký API Aliyun bị từ chối. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong goi Aliyun signed HTTP API. |
| 259 | Không bắt ngoại lệ khi tài khoản bị khóa tính năng POP3/IMAP trong trang quản trị Alibaba Mail. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 260 | Không ghi nhận chi tiết thông điệp lỗi HTTP Response Body vào log để phục vụ gỡ lỗi. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 261 | Không kiểm tra trạng thái cáp mạng (Network Interface Status) trước khi gửi yêu cầu. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 262 | Không tự chuyển sang máy chủ dự phòng khi máy chủ chính \`imap.mxhichina.com\` bị sự cố. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong co ha tang IMAP failover duoc nha cung cap cam ket. |
| 263 | Gửi email báo cáo lỗi qua SMTP bị từ chối do thiếu chuẩn mã hóa DKIM/SPF. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong gui SMTP. |
| 264 | Không xử lý ngoại lệ khi hòm thư người nhận bị đầy (\`Mailbox full / Quota exceeded\`). | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong gui email/SMTP. |
| 265 | Hai luồng tiến trình cùng truy cập một hòm thư IMAP làm máy chủ ngắt kết nối do trùng phiên. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Moi worker ket noi doc lap. |
| 266 | Không đo và cảnh báo khi tốc độ mạng quá chậm (dưới 10 KB/s). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 267 | Không xử lý ngoại lệ SSL Certificate Expired khi chứng chỉ máy chủ hết hạn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 268 | Cổng mạng bị chặn bởi tường lửa Windows nhưng ứng dụng không đưa ra hướng dẫn khắc phục. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 269 | Parse dữ liệu JSON từ API bị sập do cấu trúc JSON thay đổi từ phía Alibaba Cloud. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong goi REST API JSON. |
| 270 | Bị khóa IP tạm thời do gửi quá 100 yêu cầu/giây tới máy chủ mail. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 271 | Không lưu lại điểm dừng (Checkpoint) khiến việc tải 10GB email phải bắt đầu lại từ đầu khi đứt mạng. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | UID da xac minh duoc skip; thu thieu duoc tai tiep. |
| 272 | Độ trễ kết nối (Ping) quá cao làm ứng dụng liên tục bị sập do quá thời gian chờ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 273 | Sai chính tả tên miền máy chủ Alibaba (\`imap.mxhichna.com\`) nhưng chỉ báo lỗi kết nối chung chung. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 274 | Không giải phóng kết nối rảnh rỗi làm cạn kiệt tài nguyên Connection Pool của máy chủ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 275 | Bỏ qua ngoại lệ \`PermissionDenied\` khi tài khoản không có quyền truy cập hòm thư dùng chung (Shared Mailbox). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 276 | Không tương thích với giao thức mã hóa TLS 1.3 trên các dòng Windows cũ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 277 | File đính kèm bị hỏng dữ liệu trong quá trình truyền tải nhưng không báo lỗi cho người dùng. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | _fetch_message doi chieu RFC822.SIZE. |
| 278 | Thiếu biểu tượng cảnh báo ngắt kết nối mạng trên giao diện người dùng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 279 | Lỗi phân giải tên miền ngược (Reverse DNS Lookup Failure) làm chậm tiến trình kết nối. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong dung reverse DNS. |
| 280 | Thiếu bộ kịch bản Mock Server giả lập mạng chập chờn để kiểm thử tự động. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | test_v13.py dung fake IMAP va gia lap SSL EOF. |
| 281 | Tệp log duy nhất phình to hàng trăm MB mà không có cơ chế cắt file (\`RotatingFileHandler\`). | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | RotatingFileHandler dat maxBytes va backupCount. |
| 282 | Không chia tệp nhật ký theo ngày (\`TimedRotatingFileHandler\`) gây khó khăn khi tra cứu lịch sử sự cố. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 283 | Nhiều luồng cùng ghi vào một file log làm các dòng thông báo bị chèn đè lên nhau. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Python logging va CSV journal dung khoa de ghi da luong. |
| 284 | Không đăng ký hàm \`sys.excepthook\` khiến các lỗi bất ngờ không được ghi vệt vào file log. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 285 | Ghi mật khẩu và Token xác thực dưới dạng Plaintext vào file nhật ký hệ thống. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | UI bao mat khau [REDACTED] truoc khi ghi log. |
| 286 | Đặt Log Level ở mức \`DEBUG\` làm tệp log tràn ngập thông tin chi tiết không cần thiết. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 287 | Không gọi lệnh \`logging.shutdown()\` trước khi tắt tiến trình làm mất các dòng log cuối cùng trong Buffer. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | _stop_file_logging flush/close. |
| 288 | Định dạng mốc thời gian trong log không đồng nhất (lẫn lộn giữa \`YYYY-MM-DD\` và \`DD/MM/YYYY\`). | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | logging.Formatter giu timestamp nhat quan. |
| 289 | Không có cờ \`TraceID\` cho từng phiên chạy khiến không thể phân biệt log của các hòm thư khác nhau. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 290 | Vòng lặp ghi log bị lỗi liên tục sinh ra tệp log nặng hàng GB chỉ trong vài phút. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 291 | Tiếp tục ghi log khi ổ đĩa đã đầy 100% làm ứng dụng bị sập liên tục. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 292 | Dùng toán tử chuỗi \`%\` trong lệnh \`logging.debug()\` làm giảm hiệu năng ngay cả khi tắt mức Debug. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Python logging dung tham so lazy theo khuyen nghi, khong can f-string. |
| 293 | Ghi log dạng văn bản thô khó phân tích bằng các công cụ quản lý log tập trung (ELK, Splunk). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 294 | Khai báo trùng lặp Logger Name làm thông báo log bị in ra 2-3 lần cho một sự kiện. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 295 | Thiếu tính năng tự động xóa các file log cũ hơn 30 ngày để tiết kiệm bộ nhớ đĩa. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 296 | In toàn bộ chuỗi Byte nhị phân của file đính kèm vào file log làm đơ trình đọc file text. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 297 | File log lưu thông tin cá nhân khách hàng nhưng không được phân quyền bảo mật đúng cách. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Nhat ky luu trong thu muc user da chon, khong gui qua mang. |
| 298 | Gọi hàm \`logging.info()\` bên trong Signal Handler làm tiến trình bị treo cứng (Deadlock). | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong cai signal handler phuc tap. |
| 299 | Ứng dụng chạy ngầm không có tín hiệu Heartbeat báo trạng thái "Còn sống" cho hệ thống giám sát. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 300 | Không có tính năng nén file log cũ thành dạng file \`.zip\` để tiết kiệm lưu trữ. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Nhat ky file rotate; zip nen la tinh nang tuy chon. |
| 301 | Không bắt ngoại lệ khi thư mục lưu file log bị đặt ở chế độ Read-Only. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 302 | File log thiếu thông tin về phiên bản ứng dụng, bản Python và tên hệ điều hành ở dòng đầu tiên. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 303 | Ghi nhận sai trạng thái "Thành công" vào log trong khi tác vụ sao lưu bị lỗi một nửa. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | partial_errors khi con UID loi. |
| 304 | Lỗi \`FileNotFoundError\` khi hệ thống cố ghi log vào thư mục \`logs/\` chưa được khởi tạo. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Tu tao thu muc _NHAT_KY. |
| 305 | Thông điệp log chứa ký tự tiếng Việt có dấu làm sập trình ghi log trên môi trường CMD mã cũ. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Console chcp 65001 va log file UTF-8. |
| 306 | Thiếu công cụ CLI để lọc nhanh các dòng log có mức độ \`ERROR\` hoặc \`CRITICAL\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 307 | Ghi log lặp đi lặp lại hàng triệu lần cho cùng một lỗi trong vòng lặp \`while\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 308 | Thiếu tính năng tự động gửi email thông báo sự cố cho IT Admin khi gặp lỗi nghiêm trọng. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong co SMTP alert do nguoi dung yeu cau. |
| 309 | Tệp log bị khóa hoàn toàn khi có một chương trình khác (như Notepad) đang mở nó. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 310 | Không lưu vết thông tin dung lượng RAM/CPU còn trống trước khi thực hiện tác vụ lớn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 311 | Mất toàn bộ log trong bộ nhớ đệm khi máy tính bị mất điện đột ngột. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 312 | Bảng mã tra cứu mã lỗi (Error Code Table) không được đính kèm trong tài liệu vận hành. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 313 | Mốc thời gian trong log bị sai lệch khi hệ thống tự động đổi giờ mùa hè/mùa đông. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 314 | Cấu hình định dạng Log Format bị sai cú pháp gây ra ngoại lệ \`ValueError\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 315 | Ký tự xuống dòng \`\n\` trong dữ liệu email làm phá vỡ cấu trúc từng dòng của file log. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 316 | Không có màn hình giao diện xem log theo thời gian thực (Log Viewer) trên app. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | GUI hien thi nhat ky real-time. |
| 317 | Ghi đè file log của phiên chạy cũ mà không tạo file sao lưu lịch sử. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 318 | Thiếu tích hợp thông báo sự cố qua Webhook (Telegram Bot, Teams, Slack). | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong co thong bao qua webhook; khong truyen log/email ra ngoai. |
| 319 | Log ghi quá chi tiết cấu trúc CSDL nội bộ tạo rủi ro an toàn thông tin khi lộ file log. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 320 | Hệ thống ghi log không được kiểm thử khả năng chịu tải khi sinh log tốc độ cao. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 321 | Thiếu tham số \`--add-data\` trong file \`.spec\` làm ứng dụng \`.exe\` không tìm thấy file cấu hình/giao diện. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | SaoLuuAlibabaMailV13.spec co khai bao hiddenimports. |
| 322 | Không tự xóa thư mục tạm giải nén \`C:\Users\User\AppData\Local\Temp\_MEIxxxxxx\` sau khi đóng app. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 323 | File \`.exe\` bị Windows Defender chặn và xóa do thiếu chữ ký số xác thực (False Positive). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 324 | Thiếu file icon \`.ico\` làm ứng dụng hiển thị biểu tượng mặc định không chuyên nghiệp. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 325 | Quên tắt màn hình đen Console (\`--noconsole\`) khi đóng gói ứng dụng giao diện đồ họa GUI. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | PyInstaller console=False. |
| 326 | Thiếu khai báo \`hiddenimports\` cho các thư viện được import động, gây lỗi \`ModuleNotFoundError\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Spec khai bao mail_backend, usage_stats, kiem_tra, issue_journal. |
| 327 | Thiếu các file DLL hệ thống (\`msvcp140.dll\`) khi chạy file \`.exe\` trên máy Windows mới cài lại. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | May EXE don le nhung runtime; khong cam ket DLL cua moi Windows. |
| 328 | Dùng \`__file__\` để lấy đường dẫn tệp bị sai vị trí khi ứng dụng chạy dưới dạng đóng gói PyInstaller. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 329 | Lỗi từ chối truy cập (\`PermissionDenied\`) khi file \`.exe\` cố ghi log vào thư mục \`C:\Program Files\\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Log luu duoi thu muc user da chon, khong ghi Program Files. |
| 330 | Trình Bootloader của PyInstaller bị lỗi tương thích trên các bản Windows 11 Insider Build. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 331 | Tiến trình con ngầm không tự tắt khi người dùng bấm đóng cửa sổ \`.exe\` chính. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 332 | Mã nguồn Python bên trong file \`.exe\` dễ dàng bị giải mã ngược bằng \`pyinstxtractor\` và \`uncompyle6\`. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | PyInstaller khong phai co che bao mat ma nguon, giai ma khong la bug runtime. |
| 333 | Tệp Runtime Hook bị cấu hình sai làm hỏng quá trình khởi tạo môi trường Python nhúng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 334 | Lỗi vỡ ứng dụng khi chạy file \`.exe\` từ thư mục có đường dẫn dài vượt 260 ký tự. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 335 | Tiến trình tự cập nhật phần mềm không thể ghi đè file \`.exe\` do file đang được hệ điều hành mở. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung khong tu update EXE. |
| 336 | Thiếu lệnh \`multiprocessing.freeze_support()\` ở đầu file làm file \`.exe\` nhân bản tiến trình liên tục gây treo máy. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung dung ThreadPoolExecutor, khong dung multiprocessing. |
| 337 | Thiếu bộ mã hóa ký tự (\`encodings\`) trong gói nén làm app bị sập khi xử lý tiếng Việt. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 338 | Thư mục làm việc hiện tại bị đổi về \`C:\Windows\System32\` khi chạy file \`.exe\` qua chế độ Administrator. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BAT cd /d %%~dp0 truoc khi build. |
| 339 | Dung lượng file \`.exe\` phình to quá 200MB do đóng gói thừa các thư viện đồ họa không dùng tới. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 340 | Thiếu file log ghi lại chi tiết quá trình Build file \`.exe\` từ tệp \`.spec\`. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BUILD_V13.log giu traceback loi dong goi. |
| 341 | Đặt tên file \`.exe\` trùng với tên tiến trình chuẩn của Windows (\`svchost.exe\`) bị phần mềm diệt virus cách ly. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 342 | Không mua và tích hợp chứng chỉ số Code Signing Certificate (EV SSL) cho file \`.exe\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 343 | Thiếu tệp hướng dẫn cài đặt thư viện Visual C++ Redistributable đi kèm gói phân phối. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 344 | Sử dụng bản PyInstaller quá cũ có chứa các lỗ hổng bảo mật thực thi mã từ xa. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 345 | Đóng gói lẫn cả thư mục chứa dữ liệu test rác vào trong file nhị phân phân phối. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 346 | Phân phối gói chạy cho Linux nhưng quên cấp quyền thực thi \`chmod +x\` cho file binary. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | San pham la EXE Windows, khong phan phoi Linux. |
| 347 | Không có script dọn dẹp sạch sẽ Registry và File tạm khi người dùng gỡ bỏ ứng dụng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 348 | Không kiểm tra mã SHA256 của file \`.exe\` sau khi đóng gói xong để đảm bảo tính toàn vẹn. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | BAT tao SHA256 bang certutil. |
| 349 | Thời gian khởi động ứng dụng \`.exe\` quá chậm (mất 10-15 giây) do phải giải nén gói nén tạm thời. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 350 | Không nhận được các tham số truyền từ dòng lệnh CLI vào file \`.exe\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 351 | Trùng tên module nội bộ với thư viện chuẩn của Python nhúng bên trong gói PyInstaller. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 352 | File \`.exe\` 64-bit không thể khởi chạy trên các máy trạm chạy Windows 32-bit cũ ở xưởng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 353 | Thiếu file hướng dẫn đặt vị trí file \`.env\` nằm ngang hàng với file \`.exe\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 354 | File \`.exe\` bị hỏng cấu trúc nén khi tải qua đường truyền mạng không ổn định. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 355 | Không đọc được file cấu hình do sai đường dẫn tương đối khi chạy dưới dạng file \`.exe\`. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 356 | Không đủ bộ nhớ RAM để giải nén thư mục \`_MEIPASS\` trên các máy tính cấu hình yếu. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 357 | Windows Defender thực hiện quét file \`.exe\` lúc khởi động làm ứng dụng bị hoãn chạy 30 giây. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 358 | Không có tính năng tự đối chiếu phiên bản \`.exe\` hiện tại với bản mới nhất trên server. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Khong co server phan phoi ban update. |
| 359 | Mất file \`.spec\` gốc khiến việc đóng gói lại bản vá sau này mất nhiều thời gian cấu hình lại. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Phat hanh kem file spec nguon. |
| 360 | Thiếu bộ kịch bản kiểm thử tự động dành riêng cho việc test file \`.exe\` sau khi build. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 361 | Phụ thuộc vào gói thư viện mã nguồn mở đã ngừng phát triển hơn 3 năm trên PyPI. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 362 | Xung đột phiên bản giữa \`openpyxl\` và các thư viện xử lý dữ liệu khác khi cài đặt chung. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | openpyxl pinned. |
| 363 | Tệp \`requirements.txt\` không ghim phiên bản (\`openpyxl\` thay vì \`openpyxl==3.1.2\`) gây lỗi khi thư viện ra bản mới. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | requirements-build.txt pin giai phap build. |
| 364 | Tải phụ thuộc từ nguồn không chính thống bị kẻ xấu chèn mã độc vào gói thư viện. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 365 | Lệnh \`pip install\` không sử dụng tham số \`--require-hashes\` để xác thực tính toàn vẹn gói tải về. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 366 | Thư viện phụ thuộc yêu cầu phải cài đặt C++ Compiler mới build được trên máy khách. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | May nhan EXE khong phai cai cac package C++. |
| 367 | Import cả thư viện lớn chỉ để dùng 1 hàm đơn giản làm tăng dung lượng mã nguồn không cần thiết. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 368 | Sử dụng thư viện dính giấy phép GPLv3 trong ứng dụng thương mại gây rủi ro pháp lý về bản quyền. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 369 | Sử dụng các hàm nội bộ không công khai (\`_private_func\`) của thư viện bên thứ ba, bị mất khi thư viện update. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 370 | Bộ nhớ đệm Pip trên máy phát triển bị hỏng dẫn đến đóng gói sai bản thư viện vào app. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 371 | Hai thư viện phụ thuộc tạo ra hai thư mục trùng tên trong \`site-packages\` gây ghi đè mã nguồn. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 372 | Không loại bỏ thư mục \`tests/\` và \`docs/\` của các thư viện phụ thuộc ra khỏi gói phân phối. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | PyInstaller loai bo test dir du an khoi goi EXE mac dinh. |
| 373 | Thư viện giả lập Server Mail không phản ánh đúng các thay đổi mới của hệ thống Alibaba Mail real. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 374 | Đóng gói trên máy Mac/Linux nhưng bàn giao cho khách hàng chạy trên máy Windows. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | BAT build bat buoc Windows de tao EXE Windows. |
| 375 | Thiếu công cụ quét kiểm tra lỗ hổng bảo mật tự động (SCA - Software Composition Analysis). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 376 | Dùng các bản thư viện thử nghiệm (\`Beta\`, \`RC\`) thiếu ổn định cho dự án vận hành chính thức. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 377 | Bắt buộc máy khách phải có kết nối Internet để tải phụ thuộc mỗi khi cài mới ứng dụng. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | File EXE nhung runtime; khong can pip tren may nhan. |
| 378 | Xung đột giữa vòng lặp sự kiện của thư viện GUI (Tkinter/PyQt) và thư viện Asyncio. | `KHONG_AP_DUNG_HOAC_KHONG_BAT_BUOC` | Ung dung Tkinter+thread, khong dung asyncio. |
| 379 | Dung lượng các gói phụ thuộc chiếm tới 90% tổng dung lượng của toàn bộ ứng dụng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 380 | Thiếu bộ kịch bản Regression Test để test lại toàn bộ hệ thống sau khi update thư viện. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | tests/test_v9..v13 regressions. |
| 381 | Script file Batch không tương thích giữa các bản Windows 7, Windows 10 và Windows 11. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 382 | Thiếu quy trình tích hợp và triển khai tự động CI/CD (GitHub Actions/GitLab CI). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 383 | Không quản lý vết các thay đổi cấu hình riêng cho từng chi nhánh/nhà máy sử dụng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 384 | Thiếu biên bản nghiệm thu kỹ thuật và kiểm thử chất lượng phần mềm (QA Sign-off). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 385 | Không có kênh tiếp nhận và quản lý các báo cáo sự cố (Bug Tracking System) từ người dùng. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 386 | Thiếu tài liệu hướng dẫn gỡ rối các sự cố kết nối phần cứng và mạng LAN nhà máy. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 387 | Các phiên bản cũ từ V4 đến V11 không được dọn dẹp khỏi kho lưu trữ chính thức. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | Khong dong goi huong dan cu V4-V12. |
| 388 | Mỗi lập trình viên viết mã theo một phong cách khác nhau do thiếu quy chuẩn coding style. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 389 | Các đường dẫn liên kết tài liệu tham khảo trong file \`.txt\` bị hỏng hoặc không thể truy cập. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 390 | Thiếu báo cáo đánh giá tải và hiệu năng định kỳ của hệ thống sao lưu tự động. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 391 | Không có môi trường Chạy thử (Staging Environment) giống hệt môi trường Sản xuất (Production). | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 392 | Tài liệu hướng dẫn sử dụng quá phức tạp đối với nhân viên vận hành không thuộc ngành IT. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 393 | Số liệu thống kê số lượng mail đã sao lưu bị lệch so với thực tế trên Server Alibaba. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | kiem_tra.py doi chieu UID tren server voi file duoc verify. |
| 394 | Không sao lưu lại dữ liệu hiện tại trước khi thực hiện cập nhật bản vá ứng dụng mới. | `DA_XU_LY_HOAC_KIEM_TRA_TREN_MA_NGUON` | README khuyen cao sao luu thu muc cu truoc nang cap. |
| 395 | Thiếu kênh hỗ trợ kỹ thuật trực tiếp (Hotline/Chat) khi ứng dụng gặp sự cố dừng hoạt động. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 396 | Tệp dữ liệu lịch sử sao lưu không được kiểm tra và tối ưu hóa dung lượng định kỳ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 397 | Quy trình bàn giao phần mềm thủ công qua USB dễ làm lây nhiễm virus vào hệ thống nhà máy. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 398 | Thiếu kế hoạch đánh giá rủi ro an toàn thông tin khi tích hợp ứng dụng vào mạng nội bộ. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 399 | Thiếu phương án khôi phục dữ liệu khẩn cấp (Disaster Recovery) khi máy chủ sao lưu bị hỏng ổ đĩa. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
| 400 | Bỏ qua bước tổng kết và đánh giá hiệu quả tiết kiệm thời gian sau khi triển khai dự án tự động hóa. | `CHUA_DU_CHUNG_CU_XAC_NHAN` | Can testcase tai hien tu tester hoac kiem thu tren Alibaba Mail/Windows thuc te. |
