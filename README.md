# Alibaba Operations Center V16.0.14

## Smart Factory - 10 nhóm, danh mục 100 yêu cầu

Mở rộng bản V16.0.13 với workspace dữ liệu cục bộ, 27 biểu mẫu và các nghiệp vụ kho/sản xuất/chất lượng/nhân sự/năng lượng. Danh mục 100 mục không đồng nghĩa đã hoàn thành 100 tích hợp enterprise.

Giữ lại Email / IMAP QUOTA / IP-VPN / Hạ tầng IT / PMC / tài khoản ứng dụng. Phân hệ Smart Factory không hỏi mật khẩu mail. CSDL mới không tự đồng bộ với PMC cũ/ERP.

### Chạy trên Windows

Giải nén toàn bộ, mở `alibaba_mail_app`, chạy `CHAY_THU_WINDOWS.bat`. Cần Python 3.10+, Tkinter và openpyxl. Đăng nhập ứng dụng -> menu **Smart Factory** hoặc sidebar **09 Smart Factory** -> tạo nhà máy thử.

`TAO_EXE_WINDOWS.bat` có thể được dùng để build trên Windows. Đích: `dist/AlibabaOperationsCenter.exe`. Bản bàn giao này **chưa chứa EXE, chưa nghiệm thu Windows/thiết bị thật**.

### Tài liệu chính

- `HUONG_DAN_SMART_FACTORY_V16_0_14.md`: cách dùng, ví dụ xuất kho/sản xuất, phân quyền, sao lưu và giới hạn.
- `DOI_CHIEU_100_PHAN_HE_V16_0_14.md`: đối chiếu 100/100 mục yêu cầu, không gộp phần chưa có thành đã hoàn thành.
- `TEST_REPORT_V16_0_14.md`, `TEST_RUN_V16_0_14.txt`: kết quả kiểm thử thực tế.
- `docs/FACTORY_DATA_DICTIONARY.md`, `samples/smart_factory_templates/`: 27 mẫu CSV và từ điển trường.
- `samples/smart_factory_demo/`: 5 CSV giả lập để tự nhập vào nhà máy DEMO; không nạp tự động.

### Kiểm thử mã nguồn

```sh
python -m unittest discover -s tests -v
python app.py --self-test
```

GUI tests cần màn hình. Trên Linux headless: `xvfb-run -a python -m unittest discover -s tests -v`.

Các báo cáo V13/V14/V15/V16.0.1-13 là lịch sử bản cũ. Dùng báo cáo V16.0.14 cho bản này. `mail_backend.VERSION` được giữ để không đổi cấu trúc metadata sao lưu mail; phiên bản giao diện/phần mềm là V16.0.14.
