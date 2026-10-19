# Alibaba Mail V16.0.3 - IT Infrastructure Workbench

## Menu
- **Email / Sao luu**: bat dau/dung sao luu, IMAP, mo noi luu, bao cao, danh sach loi.
- **Mang**: LAN / IP / VPN (tu V16.0.2), IPAM.
- **Ha tang CNTT**: 7 nhom chuc nang, moi nhom mo dung tab tuong ung.
- **Cong cu**: chan doan may.

## Muc do hoan thanh va gioi han
| Nhom | Co the dung ngay | Chua trien khai / can tich hop them |
|---|---|---|
| 1. Giam sat | Khai bao tai san, TCP heartbeat thu cong, log lich su | Lich 24/7, SNMP, cam bien nhiet do / do am, bieu do |
| 2. Canh bao | Tong hop canh bao thiet bi DOWN | Telegram, Zalo, email, retry, escalation, periodic worker |
| 3. Sao luu | Sao chep thu muc cuc bo vao dich moi, kiem SHA-256 | SQL Server/Digiwin online backup, Synology API, cloud, daily/weekly scheduling, automated restore |
| 4. AD/LDAP | Sinh script Add/Remove AD group voi `-WhatIf` (KHONG THUC THI) | Quyen ghi AD/LDAP, dong bo HR, password policy GPO |
| 5. IPAM/DHCP | Quan ly IP IPv4 da giu trong SQLite, kiem tra IP trung noi bo | Cau hinh DHCP server, VLAN, QoS, IP conflict detection network-wide |
| 6. Bao tri | Xem trang thai Windows Update service, xem truoc tep log cu | Tu dong cai patch, xoa file, dat lich cap nhat |
| 7. Helpdesk | Tao, giao, cap nhat trang thai ticket, xuat CSV | Web portal, email ingestion, auto assignment, SLA |

## An toan
1. Phan he ha tang khong tu khoi dong quet mang, sua DHCP/AD, xoa tap tin hoac cai ban va khi khoi dong.
2. Xu ly IP LAN va VPN tu V16.0.2 co the ngat ket noi; can quyen Administrator va kiem tra truc tiep tren Windows.
3. IPAM la so dang ky cuc bo, khong the dam bao khong trung IP voi DHCP server khi chua dong bo.
4. Giam sat thiet bi thong qua ket noi TCP (khong phai ICMP ping) va khong xac nhan thiet bi co hoat dong dung tinh nang.
5. Sao luu thu muc khong phai transaction-consistent cho co so du lieu dang chay; dung cong cu backup SQL Server phu hop.
6. Backup dich phai la thu muc **chua ton tai**, khong nam trong thu muc nguon. File `backup_manifest.json` duoc dung de kiem chung.
7. SQLite nam tai `%LOCALAPPDATA%\\AlibabaMailIT\\infrastructure.sqlite3` tren Windows. Sao luu file nay de giu ticket va so IPAM. Khong luu password hay token trong DB.
8. De ket noi Telegram/Zalo, mail SMTP, ERP, SQL Server, Synology, AD, QoS can tai khoan, phan quyen, thong so va API chinh thuc tu IT doanh nghiep; chua duoc bat san.

## Cai dat va thu nghiem
- Windows 10/11, Python 3 va dependency trong `requirements-build.txt`.
- `python app.py` de mo GUI. `python app.py --self-test` de tu kiem tra local.
- `python -m unittest discover -s tests -q` chay 61 bai kiem thu tai moi truong phat trien.
- Dung `TAO_EXE_WINDOWS.bat` de dong goi tai Windows; da bo sung `infra_manager`, `infra_ui` vao PyInstaller spec.

## Phien ban / test
- Version: 16.0.3 - prototype IT Infrastructure (khong phai he thong quan tri 24/7 hoan chinh).
- 61/61 automated tests PASS tren Linux container, khong co may Windows, may chu mail hay ha tang KCN that de integration test.
- Gui email/IMAP, ket noi VPN, tac vu Windows, giao dien GUI chua duoc kiem chung end-to-end trong moi truong KCN.
