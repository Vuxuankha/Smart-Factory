# Báo cáo kiểm thử V16.0.14

## Kết quả đã chạy

- Toàn bộ: **309/309 bài đạt**, 48.966 giây, 0 fail, 0 error, không skip trong lượt chạy này.
- 183 bài kế thừa từ V16.0.13, tệp kiểm thử cũ không bị sửa.
- 126 bài mới: 98 backend/domain và 28 GUI Smart Factory.
- Python 3.13.5, Linux x86_64, Tk 8.6, SQLite 3.46.1. GUI chạy bằng Xvfb, không phải Windows.

Lệnh từ thư mục ứng dụng:

```sh
xvfb-run -a python -u -m unittest discover -s tests -v
python -m compileall -q .
python app.py --self-test
```

Nhật ký nguyên văn: `TEST_RUN_V16_0_14.txt`. Self-test: `SELF_TEST_V16_0_14.txt`, kết quả OK.

## Nhóm trường hợp mới đã xác minh

| Phạm vi | Kiểm tra thực tế |
|---|---|
| Danh mục | 100 số thứ tự duy nhất, 10 nhóm, mục chưa tích hợp không có nút thực thi. |
| Phân quyền | Phiên không hợp lệ, tài khoản bị khóa, nhân viên mặc định deny, read/write grant, revoke, auditor chỉ đọc, dữ liệu tách nhà máy. |
| Validation | Số NaN/Infinity/âm/quá lớn, số lẻ quá 6 chữ số, ngày sai, timestamp thiếu múi giờ, IP/mã trùng, SQL injection trong tìm kiếm. |
| Transaction | Revision cũ bị từ chối, rollback dữ liệu và audit cùng nhau, hai luồng cấp vật tư không trừ kho âm. |
| BOM/MRP | BOM 10 cấp, chặn cấp 11/vòng lặp/cặp trùng, cân tồn bán thành phẩm, PO về đúng hạn và linh kiện dùng chung không trừ tồn hai lần. |
| Kho/sản xuất | Xuất FEFO, chặn hết hạn/HOLD/BLOCKED, snapshot BOM, giao dịch idempotent, hoàn trả, lệnh đóng, thiếu vật tư, giới hạn sản lượng, truy xuất hai chiều. |
| MES/IoT | Lịch nháp tránh bảo trì, OEE đúng công thức, cảnh báo chu kỳ bất hợp lý, ngưỡng cảm biến/STALE. |
| QMS/nhân sự | Cỡ mẫu/lỗi hợp lệ, quarantine, chuyển trạng thái CAPA, chứng chỉ hết hạn, ca qua mốc ngày theo múi giờ. |
| Năng lượng | Khoảng giờ không trùng, hệ số CO2e phải có nguồn, UNKNOWN khi thiếu. |
| Sao lưu | SQLite snapshot, checksum, schema, ZIP sai tệp/thay đổi/nén, cấm ghi đè và khôi phục vào tệp mới. |
| CSV/HTML | Header, batch rollback, BOM tiếng Việt, chống công thức, escape HTML và không ghi đè. |
| Giao diện | Mở/tái sử dụng cửa sổ, 10 nhóm, 27 form, không hỏi mật khẩu mail, worker/main-thread callback, chặn bấm lặp, chờ ghi xong trước khi đóng/đăng xuất, thử lại sau lỗi, resize/empty state. |

## Kiểm tra bổ sung ngoài số 309

Đã nhập thực tế 5 CSV DEMO vào CSDL tạm, phát hành lệnh, xuất 20/100 vật tư, ghi 10 thành phẩm, đối chiếu tồn còn 80, kiểm audit, tạo snapshot và khôi phục bản mới: OK.

Chụp và xem lại giao diện Tkinter trên màn hình ảo 1366x768, cửa sổ Smart Factory 1326x700; ảnh sử dụng dữ liệu DEMO và được ghi rõ. Compileall và self-test đạt.

## Chưa xác minh

Không có Windows/EXE, DPI 125%-150%, PLC/AGV/ERP/SAP/Digiwin, camera thật, mạng sản xuất, mail/API thật, stress 72 giờ, cụm HA, đánh giá ISO/NIST/ESG hay 800 test tiêu chí. Kết quả test không bảo đảm không còn lỗi; cần nghiệm thu môi trường thật.

## Tệp cũ đã đổi trong bản này

- `CHANGELOG.md`
- `README.md`
- `SaoLuuAlibabaMailV16.spec`
- `TAO_EXE_WINDOWS.bat`
- `app.py`
- `auth_local.py`
- `dashboard_layout.py`
- `preview/README.txt`

64 tệp từ ZIP cũ giữ nguyên nội dung. Chi tiết SHA-256 trong `SOURCE_MANIFEST_SHA256.txt`.
