---
name: sql_review
description: Review một câu SQL hoặc đoạn code truy vấn trước khi chạy trên production.
when_to_use: review SQL, tối ưu query, chậm, N+1, index, EXPLAIN, deadlock, migration
---

# Review SQL trước khi chạy

## 1. Đọc được ý định
- Câu query trả lời câu hỏi gì? Có đúng bảng, đúng thời gian không?
- Có `WHERE` bắt buộc chưa? Query không `WHERE` trên bảng lớn là chặn.

## 2. Kiểm tra hiệu năng
- Chạy `EXPLAIN` (hoặc `EXPLAIN ANALYZE`) trước, đừng đoán.
- Tìm `Seq Scan` trên bảng lớn; kiểm tra index cho cột trong `WHERE` và `JOIN`.
- Tránh `SELECT *`: chỉ lấy cột cần, giảm I/O và payload.
- Phân trang bằng `LIMIT/OFFSET` có thứ tự xác định; ưu tiên keyset pagination.
- Cảnh giác hàm bọc cột (`WHERE lower(email) = ...`) làm mất index.

## 3. Kiểm tra tính đúng
- `JOIN` có thể nhân dòng? Đếm trước và sau join.
- `NULL` trong `NOT IN` trả về rỗng; dùng `NOT EXISTS`.
- Cập nhật/xoá phải có `WHERE` và nên chạy trong transaction.
- Kiểm tra khoá ngoại trước khi xoá cha.

## 4. An toàn
- Không nối chuỗi từ input người dùng; dùng tham số.
- Câu lệnh ghi phải có đường hoàn tác hoặc backup.
- Trên production: chạy trong transaction, đặt `statement_timeout`, đọc kết quả `EXPLAIN` trước.

## 5. Đầu ra
Trả về đúng ba phần: **vấn đề**, **bằng chứng** (plan/số dòng), **bản sửa**.
Nếu không có bằng chứng, nói rõ là giả thuyết cần đo.
