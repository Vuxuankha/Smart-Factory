# Alibaba Operations Center V16.0.9

Dashboard 3 cot va phim tat nhanh, ke thua V16.0.8. Xem `HUONG_DAN_V16_0_9_DASHBOARD.md` de biet gioi han va cach chay.

# Sao Luu Alibaba Mail V16

## Thu muc sao luu mac dinh

`Noi_luu / Tai_khoan / Nam / Thang MM / Hop_thu / Ten_lien_he / Thu_email / email.eml`

- Inbox, Deleted Items, Junk Email: nhom theo nguoi GUI (From).
- Sent Items, Drafts: nhom theo nguoi NHAN (To; neu thieu se dung Cc).
- Thang 01 den Thang 12 duoc tinh theo ngay gui (Date) cua email. Neu thieu hoac sai Date, phan mem su dung thoi diem he thong tai luc sao luu (khong phai ngay nhan may chu).
- Moi thu luu o thu muc rieng, co email.eml, metadata.json va attachments; nhom lien he duoc them hash ngan va email co UID/UIDVALIDITY de tranh trung ten.
- Tai khoan moi se co ten nhom rieng dua tren noi dung email, khong dung ten gia dinh Outlook.
- File cu da sao luu day du duoc bo qua tai vi tri cu, KHONG tu chuyen sang cay V16. Neu muon toan bo theo V16, chon thu muc goc moi; giu nguyen backup cu.

## Tao EXE

Tren Windows 10/11 co Python 3.10+, chay `TAO_EXE_WINDOWS.bat` de tao `dist/SaoLuuAlibabaMailV16.exe`. May su dung EXE khong can Python. Can thu nghiem tren Windows va tai khoan Alibaba Mail that truoc khi trien khai.

## Test

Tu thu muc `alibaba_mail_app`: `python -m unittest discover -s tests -p 'test_v*.py'` (mot so test cu co the khong phu hop voi bao ve metadata moi).

## Ban ra soat V16.0.1

Xem `BAO_CAO_RA_SOAT_100_MUC_V16_1.md` ve ket qua doi chieu 100 muc, cac gioi han kiem thu va nhung thay doi. Ban nay chua duoc kiem thu voi IMAP that tren Windows.

## Ban V16.0.2 - Quan ly IP LAN va IP cong cong

- Nhan **QUAN LY IP / VPN** trong cua so chinh de mo cua so dieu khien rieng.
- IP LAN: liet ke card mang dang ket noi, xem cau hinh, dat IPv4 tinh (IP / subnet / gateway / DNS) va chuyen ve DHCP. Can Windows 10/11, chay ung dung voi quyen Administrator neu muon doi cau hinh IP.
- IP cong cong: xem IP public qua HTTPS (`api.ipify.org`), ket noi/ngat mot profile VPN **da duoc tao trong Windows**. Khong co tinh nang tu tao VPN, khong doi IP WAN cua router, khong thay doi IP public neu VPN khong dinh tuyen luu luong qua VPN.
- Khong yeu cau/luu mat khau VPN. Ket noi VPN bang thong tin cau hinh tren Windows; profile chua co thong tin dang nhap co the khong ket noi duoc.
- Canh bao/xac nhan truoc khi doi cau hinh. Chan thao tac neu sao luu dang hoat dong. Doi IP/VPN co the lam ngat ket noi mail; khong tu dong doi IP theo vong lap.
- **Canh bao**: dat IP LAN sai co the mat ket noi. Chuyen lai DHCP bang nut trong phan mem hoac Windows Network Settings. DHCP khong khoi phuc IP tinh ban dau; can ghi lai thong so truoc khi doi.
- Khong bao dam ket noi VPN thanh cong tren moi he thong, khong the test Windows/netsh/rasdial/IMAP thuc te tu moi truong Linux. Chuc nang cong cong va LAN chua duoc xac nhan end-to-end tren Windows.

## V16.0.3 - Menu va ha tang CNTT
Mo thanh menu **Email / Sao luu**, **Mang**, **Ha tang CNTT**, **Cong cu**. Cua so ha tang co 7 tab; doc `HUONG_DAN_HA_TANG_CNTT_V16_0_3.md` de biet chuc nang da hoat dong va phan can tich hop them. Cac thay doi he thong nguy hiem khong tu duoc thuc thi.

## PMC (V16.0.4)
Menu mới **PMC** > PP / MC / Báo cáo & đối soát, gồm 14 hạng mục theo danh sách người dùng. Xem `HUONG_DAN_PMC_V16_0_4.md` để biết cách nhập dữ liệu và giới hạn hệ thống.

## V16.0.5 – PMC nâng cao
Bổ sung 9 màn hình chức năng quản lý PMC: FIFO/FEFO lô, tồn kho an toàn, kitting,
lịch bảo trì, gia công ngoài, đối chiếu ba chứng từ, nguyên nhân trễ, ECO, nhật ký.
Xem `HUONG_DAN_PMC_NANG_CAO_V16_0_5.md` để phân biệt chức năng hoạt động
và các tích hợp ERP/APS chưa triển khai.

### V16.0.8
Xem `HUONG_DAN_V16_0_8_QUOTA_UI.md` để dùng màn hình IMAP QUOTA và biết phạm vi UI/UX đã thực hiện. Chưa có tích hợp quản trị quota tất cả hộp thư chỉ bằng một mật khẩu Admin.

## Bản V16.0.13 — Đăng ký, đăng nhập riêng & Dashboard 3 cột

Xem `HUONG_DAN_V16_0_13_DANG_NHAP_UI_UX.md` và `BAO_CAO_RASOAT_45_VAN_DE_V16_0_13.md`.

- Lần đầu chạy tạo tài khoản Quản trị IT **riêng**; mật khẩu đó không phải mật khẩu Alibaba Mail.
- Các đăng ký sau chỉ có hiệu lực khi Quản trị IT phê duyệt. Mọi thao tác IMAP có nhu cầu xác thực hộp thư vẫn dùng mật khẩu IMAP **riêng**.
- Kiểm tra mạng, Mạng/VPN, Hạ tầng IT và PMC không hỏi thông tin tài khoản email.
- Giao diện theo phong cách dashboard tối, thao tác nhanh, kết hợp `psutil` để hiển thị CPU/RAM.
- Đóng gói qua `TAO_EXE_WINDOWS.bat`; dự kiến tạo `dist/AlibabaOperationsCenter.exe` (`console=False`). Chưa xác nhận build Windows thành công trong môi trường này.
