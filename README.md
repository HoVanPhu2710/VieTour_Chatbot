# VieTour Chatbot

## Hướng dẫn chạy chatbot sau khi pull về

### 1. Cài đặt Python và các thư viện cần thiết

- Yêu cầu Python 3.8.10
- Cài đặt các thư viện:

```bash
pip install rasa
```

### 2. Cài đặt các package bổ sung (nếu có)

- Nếu sử dụng action server (Python), cài thêm:

```bash
pip install rasa-sdk requests
```

### 3. Train model chatbot

```bash
rasa train
```

### 4. Chạy chatbot

- Chạy server Rasa:

```bash
rasa run --enable-api --cors "*"
```

- (Tùy chọn) Chạy action server nếu có custom action:

```bash
rasa run actions
```

### 5. Kết nối với client/web

- Đảm bảo client/web gọi đúng endpoint Rasa (mặc định: http://localhost:5005)
- Có thể dùng Rasa Webchat hoặc tự xây UI chat

### 6. Lưu ý

- **Không push thư mục `models/` lên git** (đã .gitignore)
- Mỗi lần cập nhật dữ liệu/nlu/stories, cần train lại model
- Nếu lỗi, kiểm tra lại version Python, package, và log lỗi

---

## Thư mục cấu trúc

- `actions/` : Custom action Python
- `data/` : NLU, stories, rules
- `models/` : Model đã train (không push lên git)
- `domain.yml` : Định nghĩa intent, entity, slot, response
- `config.yml` : Cấu hình pipeline

---

## Liên hệ hỗ trợ

- Gặp lỗi hoặc cần hướng dẫn thêm, liên hệ team dev VieTour.
