# Phiếu quan sát — Agent harness có sẵn

Chọn **một** agent bạn đang dùng (Claude Code, ChatGPT, Cursor, Copilot...) và giao cho nó một việc nhỏ. Ghi lại những gì bạn thấy. Mục đích không phải chấm điểm agent, mà để nhận ra: agent thật cũng chỉ chạy đúng vòng lặp bạn vừa viết ở bài 06.

## Việc đã giao

> Ví dụ: "Tìm 3 file lớn nhất trong thư mục này và cho tôi biết chúng là gì."

Việc tôi giao:

```

```

## 1. Nó đã làm gì? (theo đúng thứ tự)

| Bước | Hành động quan sát được | Đây là tool gì? | Ai quyết định bước này? |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

## 2. Nó dùng tool nào?

- [ ] Đọc file
- [ ] Ghi/sửa file
- [ ] Chạy lệnh terminal
- [ ] Tìm kiếm web
- [ ] Tìm trong codebase
- [ ] Khác: ........................

## 3. Nó nhớ gì?

Hỏi tiếp một câu cần thông tin từ lượt trước ("cái thứ hai tên gì?").

- Nó có nhớ không?
- Bạn đoán nó đã gửi lại những gì trong context?

## 4. Nó dừng khi nào?

- Tự dừng khi thấy đủ thông tin?
- Hỏi lại bạn?
- Chạy quá tay (làm nhiều hơn cần thiết)?

## 5. Nó xin phép ở đâu?

Có hành động nào nó dừng lại hỏi trước khi làm không? Đó là **human-in-the-loop** — buổi 2 và buổi 8 sẽ nói kỹ.

## 6. Kết luận của tôi

Điền vào chỗ trống:

> Agent này = model .................... + harness gồm ....................
>
> Nếu chỉ được sửa **một** thứ trong harness của nó, tôi sẽ sửa .................... vì ....................
