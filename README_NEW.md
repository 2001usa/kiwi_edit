# Media Platform Bot (Redesign)

Bu loyiha eski botni yangi, masshtablashuvchan arxitekturaga o'tkazilgan versiyasidir.

## 🚀 Texnologiyalar
- **Language**: Python 3.11
- **Bot**: Aiogram 3.x
- **API**: FastAPI
- **Database**: PostgreSQL (Async SQLAlchemy)
- **Cache**: Redis
- **Infra**: Docker & Docker Compose

## 🛠 O'rnatish

1. **Virtual muhit yaratish**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt (yoki poetry install)
   ```

2. **Docker Servislarini ishga tushirish**:
   PostgreSQL va Redisni ishga tushirish uchun:
   ```bash
   docker-compose up -d
   ```
   *Agar docker bo'lmasa, mahalliy PostgreSQL o'rnatib, `.env` faylda sozlashingiz kerak.*

3. **Migratsiya (Bazani yaratish)**:
   ```bash
   alembic upgrade head
   ```

4. **Botni ishga tushirish**:
   ```bash
   python run_bot.py
   ```

5. **Admin Panelni (API) ishga tushirish**:
   ```bash
   python run_admin.py
   ```
   API hujjati: http://localhost:8000/docs

## 📁 Fayl Tuzilishi
- `app/bot`: Telegram bot logikasi (Handlers, Keyboards).
- `app/web`: Admin panel API (FastAPI).
- `app/infrastructure`: Baza va tashqi servislar bilan ishlash.
- `app/core`: Sozlamalar (`config.py`).
- `alembic`: Baza migratsiyasi.
