# V16.0.14 - Smart Factory local workspace

- Added 10 source-aligned groups, a 100-item requirements/scope catalog, and 27 real data forms.
- Added plant/domain authorization, revision checks, atomic posting/audit, strict CSV imports, bounded queries and independent factory.sqlite3.
- Added FEFO issue/return, order/BOM snapshots, multi-level MRP, output/lot trace, OEE, maintenance-aware draft scheduling, IQC/PQC/OQC, CAPA and skill-checked shifts.
- Added declared sensor thresholds/incident history, manual asset topology, entered-input cost/energy/CO2e reports, per-account preferences and verified unencrypted snapshots.
- Added 126 new regression tests. Retained all 183 previous tests unchanged.
- Preserved mail/IP/VPN/IT/legacy PMC data and workflows. No automatic migration, device control or external API calls in the new workspace.
- Catalog differentiates 22 local-scoped items, 51 partial items and 27 not implemented integrations. No enterprise certification, uptime promise, 800-test claim or Windows acceptance claim.

## V16.0.9 - Dashboard 3 luong
- Sidebar thu gon; thanh dau trang va quick actions; console drawer; command palette va phim tat.
- Gia han giao dien tai khoan/quyen admin, IMAP QUOTA, IP/VPN, IT/PMC.
- CPU/RAM neu co psutil va dia that; khong gia lap % tien do/ETA.
- Them 4 bai test GUI.

## V16.0.7 - Industrial UI/UX
- Shared industrial ttk theme; navigation sidebar; reorganized email screen into four cards; dark activity log.
- Bigger PMC and IT windows, styling aligned to main app.
- No modifications to backup engine, PMC or IT business logic.

# Changelog

## V16
- Mac dinh nam / Thang MM / hop thu / nguoi gui hoac nhan / thu email.
- Giu che do V15 va cac che do cu.
- Chu y: khong tu chuyen email da backup sang cau truc moi.

## V16.0.6
- Sửa chuyển chế độ Nhân viên/Quản trị viên làm vùng đăng nhập không hiển thị đúng.
- Sửa thao tác Tkinter từ luồng phụ trong cửa sổ PMC và Hạ tầng.
- Thêm điều hướng chức năng PMC bằng hộp chọn.
- Thêm 2 bài kiểm thử giao diện, tổng 81 bài đạt trên môi trường kiểm thử.

## V16.0.8 — Mailbox Storage + UI Navigation
- Thêm `mail_quota.py` (truy vấn IMAP QUOTA chỉ đọc) và `quota_ui.py` (bảng dung lượng và CSV).
- Thêm menu Dung lượng hộp thư; ngăn nhật ký ẩn/hiện; sidebar thu gọn/mở rộng.
- Đổi bảng màu thương hiệu sang navy `#0F172A`, blue `#3B82F6`, green `#10B981`.
- Bổ sung kiểm thử quota; các tính năng nâng cao chưa triển khai được liệt kê trung thực trong hướng dẫn.

## V16.0.11 - Reliability hardening
- LAN cancellation responsiveness and isolated host probe failures.
- Validate PMC import rows before applying, CSV formula escaping and exclusive report output.
- Escape potentially active spreadsheet formulas in mailbox-quota reports.
- Avoid overwrite of LAN scan report, clarify cancelled scan.
- 100 local automated tests pass; see BAO_CAO_RA_SOAT_800_MUC_V16_0_11.md for scope and limitations.

## V16.0.12 - 2026-10-19
- Khắc phục cửa sổ CMD xuất hiện trong lúc LAN discovery: ẩn tiến trình con `ping` và `arp` trên Windows.
- Ẩn console của lệnh PowerShell kiểm tra bảo trì.
- Thêm 3 bài kiểm thử hồi quy.

## V16.0.13 — Account Login & Industrial Dashboard
- Đăng ký/đăng nhập độc lập với mật khẩu email, khởi tạo Quản trị IT ban đầu, các đăng ký sau chờ duyệt.
- Ba vai trò ứng dụng; băm scrypt + salt, giới hạn đăng nhập sai, đổi mật khẩu/đăng xuất, audit xác thực.
- Chẩn đoán máy/mạng không yêu cầu tài khoản hay mật khẩu hộp thư.
- Sửa các điểm vòng đời Tkinter/worker, reuse cửa sổ, quét LAN, CSV không ghi đè, giới hạn log.
- UI dark 3 cột có cuộn ở màn hình nhỏ, nút tác vụ chính ở vùng nhìn thấy, thống kê CPU/RAM/Disk theo máy thật, console cố định ở đáy.
- Thêm 80 kiểm thử auth/UI; 183/183 bài kiểm thử đạt trên Linux + Xvfb, chưa kiểm thử Windows thực tế.
