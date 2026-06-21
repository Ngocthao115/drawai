# 🎨 Drawing → Video AI Prompt Generator

Ứng dụng giúp **giáo viên mầm non** biến hình vẽ của trẻ thành prompt video AI — không cần biết kỹ thuật, không cần nhập API key.

---

## 🚀 Deploy lên Streamlit Cloud (miễn phí)

### Bước 1 — Đẩy code lên GitHub

```bash
git init
git add .
git commit -m "Drawing to Video AI"
git remote add origin https://github.com/TEN_THAO/drawing2video.git
git push -u origin main
```

### Bước 2 — Tạo app trên Streamlit Cloud

1. Vào [share.streamlit.io](https://share.streamlit.io) → đăng nhập GitHub
2. **New app** → chọn repo `drawing2video` → file `app.py` → **Deploy**

### Bước 3 — Cài API Key (quan trọng — làm 1 lần duy nhất)

> Sau bước này, giáo viên chỉ cần mở link và dùng, không cần nhập gì cả.

1. Vào [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) → tạo key
2. Trên Streamlit Cloud, vào **App → Settings → Secrets**
3. Dán nội dung sau vào ô Secrets:

```toml
GEMINI_API_KEY = "AIza...key_của_bạn"
```

4. Nhấn **Save** → app tự khởi động lại

**Xong!** Chia sẻ link `https://....streamlit.app` cho toàn bộ giáo viên.

---

## 💻 Chạy trên máy tính cá nhân

```bash
pip install -r requirements.txt

# Cài API key local (bỏ dấu # trong file .streamlit/secrets.toml):
# GEMINI_API_KEY = "AIza..."

streamlit run app.py
```

---

## 📁 Cấu trúc project

```
drawing2video/
├── app.py                        # Ứng dụng chính
├── requirements.txt              # Thư viện
├── README.md                     # Hướng dẫn
└── .streamlit/
    ├── secrets.toml              # API key (local, không đẩy lên GitHub)
    └── config.toml               # Giao diện màu sắc
```

---

## ✨ Tính năng

- Giáo viên chỉ cần tải ảnh lên và nhấn nút — không cần biết gì về AI
- Gemini Vision tự phân tích nội dung hình vẽ
- Tạo prompt tối ưu cho: Sora, Runway, Kling, Pika, Veo, Luma
- 6 phong cách: Cinematic, Hoạt hình 2D, Pixar 3D, Màu nước, Stop Motion, Tài liệu
- Output tiếng Anh hoặc tiếng Việt
