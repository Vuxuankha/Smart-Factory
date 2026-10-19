# Alibaba Operations Center V16.0.9 - Dashboard 3 luong

## Giao dien
- Thanh dau trang: ten ung dung, trang thai tac vu va tim kiem nhanh.
- Cot trai: Email, quota, mang/VPN, IT Infrastructure, PMC, nhat ky va chan doan. Co the thu gon.
- Cot giua: (1) tai khoan nhan vien/quan tri, (2) bat dau/dung an toan va trang thai, (3) noi luu, luong tai va gioi han MB/s.
- Cot phai: CPU/RAM neu co `psutil`, dung luong dia con trong, canh bao dia day, cac thao tac nhanh. Chi so dia la thong tin thuc doc tai may.
- Drawer nhat ky o day: thu gon/mở rong; dong log co phan loai mau.
- Ho tro go tim chuc nang qua Ctrl+K va lua chon.

## Phim tat (chi hieu luc khi cua so ung dung dang duoc chon)
- Ctrl+Enter: bat dau sao luu (van yeu cau xac thuc).
- Ctrl+Shift+S: yeu cau dung an toan **sau email hien tai**, khong dung tuc thi.
- Ctrl+L / Ctrl+`: mo dong console.
- Ctrl+K: tim nhanh chuc nang.

## Canh bao va pham vi
- Khong co % hoan thanh / ETA / toc do thuc chuan vi backend hien co chua truyen du so lieu; thanh tien trinh chi bao dang xu ly.
- Trang thai ket noi IMAP khong tu duoc danh dau online neu chua test; khong gia lap ping hay canh bao.
- 'Kiem tra mang' su dung chan doan ket noi cua ung dung, khong ping tat ca server/camera khi chua co danh sach thiet bi.
- CPU/RAM: cai `psutil` neu muon xem chi so (khong bat buoc). Neu chua cai se hien N/A.
- Dung an toan khong dam bao huy cac ket noi dang tai tuc thi. Luon thu tren tai khoan thu nghiem.
- Giao dien PMC/IT va cac phan back-end cu duoc giu lai. Khong co AI tu dong khac phuc loi hay quyen admin moi.
- Neu can %/ETA that, can bo sung bo dem bytes/tong email va progress event tu back-end.

## Chay va kiem thu
- Windows: `CHAY_THU_WINDOWS.bat` (Python >=3.10, openpyxl).
- Unit tests: `python -m unittest discover -s tests -p "test*.py" -q` (GUI can desktop display).
- Kiem thu may chu Alibaba Mail that, gioi han man hinh/dpi 125%-150% va phien dang nhap admin can thuc hien tai may nguoi dung.
