# Từ điển dữ liệu Smart Factory

27 loại bản ghi. Mã `code` duy nhất theo nhà máy và loại, 1-64 ký tự không dấu: chữ, số, dấu chấm, gạch dưới, gạch ngang. Số tối đa 6 chữ số thập phân, dùng dấu chấm; không dấu phân cách hàng nghìn.

`date`: YYYY-MM-DD. `datetime`: ISO 8601 có múi giờ, ví dụ 2026-10-19T08:00:00+07:00. Mọi tham chiếu chỉ tới bản ghi cùng nhà máy.


## suppliers - Nhà cung cấp / gia công

Nhóm 1. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| name | Tên | text | Có |  |
| risk | Mức rủi ro | choice | Có | LOW / LOW, MEDIUM, HIGH |
| contact | Liên hệ | text | Không |  |
| notes | Ghi chú | text | Không |  |

## shipments - Theo dõi giao hàng

Nhóm 1. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| supplier | Nhà cung cấp | text | Có |  -> suppliers |
| reference | Mã đơn / vận đơn | text | Có |  |
| due | Hạn giao | date | Có |  |
| status | Trạng thái | choice | Có | PLANNED / PLANNED, IN_TRANSIT, DELIVERED, CANCELLED |
| notes | Mốc giao nhận | text | Không |  |

## assets - Tài sản / máy / thiết bị

Nhóm 7. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| name | Tên thiết bị | text | Có |  |
| type | Loại | choice | Có | MACHINE / MACHINE, TOOL, SERVER, SWITCH, ROUTER, CAMERA, NAS, SENSOR, OTHER |
| location | Khu vực | text | Không |  |
| state | Trạng thái khai báo | choice | Có | UNKNOWN / UNKNOWN, RUN, IDLE, STOP, MAINTENANCE |
| ip | IP (tùy chọn) | ip | Không |  |
| parent | Thiết bị cha | text | Không |  -> assets |
| capacity | Sản phẩm / giờ | decimal | Có | 0 |
| skill | Kỹ năng bắt buộc | text | Không |  |
| maintenance_due | Hạn bảo trì | date | Không |  |

## sensors - Cảm biến & ngưỡng

Nhóm 2. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| asset | Thiết bị | text | Có |  -> assets |
| unit | Đơn vị | text | Có |  |
| low | Ngưỡng dưới | signed | Có | 0 |
| high | Ngưỡng trên | signed | Có | 100 |
| stale_minutes | Quá hạn sau (phút) | positive | Có | 60 |

## readings - Mẫu đo cảm biến

Nhóm 2. Quyền ghi theo nhóm/nhà máy. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| sensor | Cảm biến | text | Có |  -> sensors |
| value | Giá trị đo | signed | Có |  |
| at | Thời gian ISO + múi giờ | datetime | Có |  |

## materials - Danh mục vật tư / sản phẩm

Nhóm 3. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| name | Tên vật tư | text | Có |  |
| unit | Đơn vị | text | Có | pcs |
| type | Nguồn cung | choice | Có | BUY / BUY, MAKE |
| safety | Tồn an toàn | decimal | Có | 0 |

## lots - Lô hàng / FIFO / FEFO

Nhóm 3. Quyền ghi theo nhóm/nhà máy. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| material | Vật tư | text | Có |  -> materials |
| quantity | Số lượng nhập | decimal | Có |  |
| received | Ngày nhập | date | Có |  |
| expiry | Hạn dùng | date | Không |  |
| quality | Trạng thái chất lượng | choice | Có | HOLD / HOLD, RELEASED, BLOCKED |
| location | Vị trí kho | text | Có | MAIN |
| owner | Chủ hàng ký gửi | text | Không |  |

## inbound - Hàng đang về (kế hoạch)

Nhóm 3. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| material | Vật tư | text | Có |  -> materials |
| quantity | Số lượng | positive | Có |  |
| eta | Dự kiến đến | date | Có |  |
| status | Trạng thái | choice | Có | OPEN / OPEN, RECEIVED, CANCELLED |

## counts - Phiếu kiểm kê

Nhóm 3. Quyền ghi theo nhóm/nhà máy. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| lot | Mã lô | text | Có |  -> lots |
| counted | Số lượng đếm | decimal | Có |  |
| at | Thời điểm đếm | datetime | Có |  |

## docks - Lịch cửa kho / bến bãi

Nhóm 3. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| dock | Cửa / bến | text | Có |  |
| vehicle | Biển số / xe | text | Có |  |
| start | Bắt đầu (ISO + múi giờ) | datetime | Có |  |
| end | Kết thúc | datetime | Có |  |

## bom - BOM đa cấp

Nhóm 4. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| parent | Mã cha (MAKE) | text | Có |  -> materials |
| component | Linh kiện | text | Có |  -> materials |
| per | Định mức / 1 sản phẩm | positive | Có |  |

## orders - Lệnh sản xuất điện tử

Nhóm 4. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| product | Thành phẩm | text | Có |  -> materials |
| quantity | Số lượng | positive | Có |  |
| due | Hạn giao | date | Có |  |
| priority | Ưu tiên (5 cao nhất) | choice | Có | 1 / 1, 2, 3, 4, 5 |
| state | Trạng thái | choice | Có | DRAFT / DRAFT, RELEASED, HOLD, CLOSED, CANCELLED |

## maintenance - Lịch bảo trì

Nhóm 4. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| asset | Thiết bị | text | Có |  -> assets |
| start | Bắt đầu (ISO + múi giờ) | datetime | Có |  |
| end | Kết thúc | datetime | Có |  |
| reason | Nội dung | text | Có |  |

## oee - Nhật ký ca / OEE

Nhóm 4. Quyền ghi theo nhóm/nhà máy. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| asset | Máy | text | Có |  -> assets |
| date | Ngày | date | Có |  |
| planned_min | Thời gian kế hoạch (phút) | positive | Có | 480 |
| run_min | Thời gian chạy (phút) | decimal | Có |  |
| cycle_sec | Chu kỳ lý tưởng (giây) | positive | Có |  |
| total | Tổng sản lượng | integer | Có |  |
| good | Sản lượng đạt | integer | Có |  |

## incidents - Sự cố & theo dõi xử lý

Nhóm 6. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| title | Sự cố | text | Có |  |
| severity | Mức độ | choice | Có | WARNING / INFO, WARNING, CRITICAL |
| state | Trạng thái | choice | Có | OPEN / OPEN, ACKNOWLEDGED, RESOLVED |
| owner | Người xử lý | text | Không |  |
| notes | Nguyên nhân / biện pháp | text | Không |  |

## licenses - Bản quyền phần mềm

Nhóm 7. Chỉ Quản trị IT được ghi. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| asset | Máy / thiết bị | text | Có |  -> assets |
| software | Phần mềm | text | Có |  |
| seats | Số lượng | integer | Có | 1 |
| expires | Hạn bản quyền | date | Không |  |
| reference | Mã hợp đồng (không lưu license key) | text | Không |  |

## inspections - Kiểm tra IQC / PQC / OQC

Nhóm 8. Quyền ghi theo nhóm/nhà máy. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| stage | Công đoạn | choice | Có | IQC / IQC, PQC, OQC |
| lot | Lô kiểm tra | text | Có |  -> lots |
| sampled | Số lượng kiểm | positive | Có |  |
| rejected | Số lượng lỗi | decimal | Có | 0 |
| reason | Loại lỗi / nguyên nhân | text | Không |  |
| date | Ngày kiểm | date | Có |  |

## capa - CAPA - khắc phục / phòng ngừa

Nhóm 8. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| title | Vấn đề | text | Có |  |
| owner | Người phụ trách | text | Có |  |
| due | Hạn xử lý | date | Có |  |
| state | Trạng thái | choice | Có | OPEN / OPEN, IN_PROGRESS, VERIFY, CLOSED |
| cause | Nguyên nhân gốc | text | Không |  |
| action | Hành động | text | Không |  |
| verification | Bằng chứng xác minh | text | Không |  |

## calibrations - Kiểm định / hiệu chuẩn

Nhóm 8. Quyền ghi theo nhóm/nhà máy. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| asset | Thiết bị | text | Có |  -> assets |
| calibrated | Ngày hiệu chuẩn | date | Có |  |
| due | Hạn hiệu chuẩn | date | Có |  |
| certificate | Mã chứng thư | text | Có |  |
| result | Kết quả | choice | Có | PASS / PASS, FAIL |

## sops - SOP / tài liệu kỹ thuật

Nhóm 8. Quyền ghi theo nhóm/nhà máy. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| title | Tiêu đề | text | Có |  |
| revision | Phiên bản | text | Có |  |
| reference | Tham chiếu tài liệu | text | Có |  |
| effective | Ngày hiệu lực | date | Có |  |
| owner | Người kiểm soát | text | Có |  |

## staff - Hồ sơ nhân sự tối thiểu

Nhóm 9. Chỉ Quản trị IT được ghi. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| name | Họ tên | text | Có |  |
| team | Tổ / bộ phận | text | Có |  |
| active | Đang làm việc | choice | Có | YES / YES, NO |

## skills - Ma trận kỹ năng & chứng chỉ

Nhóm 9. Chỉ Quản trị IT được ghi. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| staff | Nhân sự | text | Có |  -> staff |
| skill | Mã kỹ năng | text | Có |  |
| valid_from | Có hiệu lực từ | date | Có |  |
| valid_to | Hết hạn | date | Có |  |
| certificate | Mã chứng chỉ | text | Có |  |

## shifts - Phân ca & kiểm tra kỹ năng

Nhóm 9. Chỉ Quản trị IT được ghi. Sửa qua revision; không ghi đè bản sửa mới của người khác.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| staff | Nhân sự | text | Có |  -> staff |
| asset | Máy | text | Có |  -> assets |
| start | Bắt đầu (ISO + múi giờ) | datetime | Có |  |
| end | Kết thúc | datetime | Có |  |

## handovers - Nhật ký bàn giao ca

Nhóm 9. Quyền ghi theo nhóm/nhà máy. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| asset | Máy | text | Có |  -> assets |
| at | Thời điểm bàn giao | datetime | Có |  |
| outgoing | Người bàn giao | text | Có |  -> staff |
| incoming | Người nhận | text | Có |  -> staff |
| notes | Nội dung bàn giao | text | Có |  |

## ppe - Cấp phát bảo hộ lao động

Nhóm 9. Quyền ghi theo nhóm/nhà máy. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| staff | Nhân sự | text | Có |  -> staff |
| item | Vật dụng | text | Có |  |
| quantity | Số lượng | positive | Có |  |
| date | Ngày cấp | date | Có |  |

## energy - Năng lượng & ước tính CO2e

Nhóm 10. Chỉ Quản trị IT được ghi. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| asset | Máy / công tơ | text | Có |  -> assets |
| start | Đầu kỳ (ISO + múi giờ) | datetime | Có |  |
| end | Cuối kỳ | datetime | Có |  |
| kwh | Điện TIÊU THỤ trong kỳ (kWh) | decimal | Có |  |
| state | Trạng thái | choice | Có | RUN / RUN, IDLE |
| tariff | Đơn giá / kWh | decimal | Có | 0 |
| factor | Hệ số kgCO2e/kWh | decimal | Không |  |
| factor_source | Nguồn hệ số | text | Không |  |
| factor_date | Ngày hiệu lực hệ số | date | Không |  |

## training - Đào tạo & đánh giá

Nhóm 9. Chỉ Quản trị IT được ghi. Chứng từ bất biến sau khi ghi; không sửa trực tiếp.

| Trường CSV | Nhãn | Kiểu | Bắt buộc | Mặc định / lựa chọn / tham chiếu |
|---|---|---|---|---|
| staff | Nhân sự | text | Có |  -> staff |
| course | Khóa đào tạo | text | Có |  |
| date | Ngày | date | Có |  |
| result | Kết quả | choice | Có | PENDING / PENDING, PASS, FAIL |
