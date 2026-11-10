---
name: refund
description: Xử lý yêu cầu hoàn tiền hoặc đổi trả cho đơn hàng của SoundHouse.
when_to_use: khách hỏi hoàn tiền, trả lại tiền, đổi trả, trả hàng, refund, bị rè, lỗi sản phẩm
---

# Quy trình hoàn tiền

## 1. Xác minh trước khi hứa
- Lấy mã đơn, tên người nhận và ngày nhận hàng.
- Tra đơn bằng `get_order`. Chỉ tiếp tục khi trạng thái là `đã giao`.
- Tra bảo hành bằng `check_warranty` nếu khách nói lỗi kỹ thuật.
- Không xác nhận hoàn tiền trước khi có kết quả kiểm tra kỹ thuật.

## 2. Phân loại
| Trường hợp | Xử lý |
|---|---|
| Lỗi nhà sản xuất trong 7 ngày | Đổi mới, không cần duyệt |
| Lỗi sau 7 ngày, còn bảo hành | Chuyển kỹ thuật, hẹn 3–5 ngày |
| Đổi ý, sản phẩm còn nguyên hộp | Đổi trả nếu trong 7 ngày |
| Rơi vỡ, vào nước | Từ chối bảo hành, báo giá sửa |

## 3. Ngưỡng tiền
- Dưới 500.000đ: tạo yêu cầu bằng `issue_refund`.
- Từ 500.000đ trở lên: tạo ticket, xin duyệt quản lý, chưa gọi `issue_refund`.
- Không bao giờ chia nhỏ khoản hoàn để lách ngưỡng.

## 4. Câu trả lời mẫu
"Đơn {order_id} đủ điều kiện {đổi mới/hoàn tiền}. Mình đã tạo {mã ticket}. "
"Thời gian xử lý dự kiến {N} ngày làm việc. Bạn cần giữ {hộp/phụ kiện}."

## 5. Sai sót thường gặp
- Hứa hoàn tiền khi chưa kiểm tra kỹ thuật.
- Bỏ sót mã đơn trong câu trả lời.
- Gộp hai đơn vào một yêu cầu hoàn tiền.
- Quên ghi nguồn khi trích chính sách.
