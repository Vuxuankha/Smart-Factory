# Bao cao tich hop quan ly IP - V16.0.2

## Da them
- Cua so "QUAN LY IP / VPN" trong giao dien ung dung, khong thay doi cac xu ly backup IMAP.
- Xem cau hinh card mang; liet ke adapter Windows; xac minh IPv4 va subnet, gateway, DNS truoc khi thiet lap IP tinh.
- Chuyen IP va DNS sang DHCP bang `netsh` voi tham so truyen dang argv (khong dung shell=True).
- Liet ke cac VPN connection Windows co san, ket noi/ngat bang `rasdial.exe` (khong luu thong tin dang nhap).
- Tra cuu IP cong cong qua HTTPS api.ipify.org.
- Xac nhan truoc thao tac thay doi va chan doi mang khi dang sao luu.

## Kiem thu
- 52 test unit/mock PASS, gom 44 test hien co va 8 test rieng cho network_manager.py.
- Python compileall PASS.
- Chua chay cac lenh thay doi IP / VPN tren Windows, chua xac minh thuc te IP public thay doi va chua dong goi EXE.

## Gioi han quan trong
- Quyền Administrator can thiet cho viec doi IP tinh/DHCP; lay thong tin va quan ly VPN phu thuoc cau hinh/permissions Windows.
- VPN can cau hinh san; IP public chi thay doi neu VPN dinh tuyen internet qua VPN. Phan mem khong cho phep tuy chon thay doi IP public cua nha mang.
- Khi dat IP LAN tinh, cau hinh cu khong duoc luu tu dong: hay ghi lai thong so truoc khi doi. DHCP la phuong an phuc hoi neu mang co DHCP.
- Doi ket noi co the lam gian doan task khac tren may. Khong doi IP trong luc backup dang chay theo trang thai ung dung.
