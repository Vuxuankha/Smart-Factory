# Alibaba Operations Center V16.0.10 - Quet LAN

## Sua loi
- Ban V16.0.9 chi kiem tra TCP den cac thiet bi **da nhap thu cong**; khong the tu dong tim may trong mang.
- V16.0.10 bo sung tab Ha tang CNTT > 1. Giam sat > **Quet thiet bi LAN**.
- Co the de xuat mang `/24` hien hanh, cho phep sua lai CIDR, xac nhan truoc khi quet, quet nen (khong treo giao dien), dung quet, bang IP/MAC/cong TCP, xuat CSV.
- Kiem tra thu ping mot lan/host va mot so cong TCP pho bien (80,443,445,22,3389,554). MAC chi hien thi neu bang ARP cua he dieu hanh cung cap.
- Gioi han /24 hoac nho hon (toi da 256 dia chi), chi IP private. Khong dong vao thong so mang, khong thay doi router, khong luu mat khau.

## Cach dung
1. Giai nen, chay `CHAY_THU_WINDOWS.bat`.
2. Mo **Ha tang CNTT > 1. Giam sat thiet bi**.
3. Kiem tra dai LAN. Vi du 192.168.1.0/24. Dia chi duoc goi y theo giao dien mang dang chon; neu may co VPN hoac nhieu card mang, can kiem tra va sua lai cho dung.
4. Bam **Quet thiet bi LAN** va xac nhan. Ket qua hien dia chi IP, MAC neu co, cong TCP phan hoi va cach phat hien.
5. Xuat CSV neu can. Neu muon theo doi thiet bi theo thoi gian, nhap IP o muc 'Giam sat thiet bi da luu'.

## Gioi han
- Khong phat hien duoc moi thiet bi: thiet bi tat ping va khong mo cac cong duoc kiem tra, bi VLAN/firewall ngan, hoac khac subnet co the khong hien.
- Khong suy dien ten thiet bi/hang san xuat tu MAC neu khong co nguon du lieu co kiem chung.
- Ping/TCP tu may Windows co the bi firewall hoac chinh sach doanh nghiep chan.
- Khong tu dong quet mang cua don vi khac; chi su dung tren mang co quyen kiem tra.
- Chua duoc thu truc tiep tren mang doanh nghiep thuc te. Kiem thu unit/UI trong man hinh ao khong thay the thu nghiem tren Windows.
