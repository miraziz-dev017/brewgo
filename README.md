# BrewGo Telegram Bot (Free Server)

Bu loyiha sizning `BrewGo` ilovangiz uchun alohida Telegram bot backendi.
Bot YouTube/Instagram linkni qabul qilib, video fayl yuborishga harakat qiladi.

## 1) Ishga tushirish (lokal)

1. Python 3.11+ o'rnating.
2. Virtual env yarating va paketlarni o'rnating:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. `.env` yarating (`.env.example` asosida):

```env
BOT_TOKEN=...
PUBLIC_BASE_URL=https://your-public-url
WEBHOOK_SECRET=...
PORT=8000
```

4. Serverni ishga tushiring:

```bash
uvicorn bot_server:app --host 0.0.0.0 --port 8000

Yoki Windows'da bitta fayl bilan:

```bash
start_bot.bat
```

## VS Code / Android Studio

- **VS Code**:
  - Loyihani `d:\brewgo` sifatida oching.
  - `Python` extension o'rnating.
  - `Run and Debug` -> `Run BrewGo Bot (uvicorn)` ni bosing.
  - Yoki terminalda `start_bot.bat` ishga tushiring.

- **Android Studio**:
  - `d:\brewgo` papkasini oching (yoki terminaldan shu papkaga kiring).
  - Pastki terminalda `start_bot.bat` ni ishga tushiring.
  - Android Studio Python IDE emas, lekin terminal orqali bot normal ishlaydi.
```

## 2) Tekin serverga deploy (Render)

1. Loyihani GitHub'ga joylang.
2. Render'da **New Web Service** tanlang va repo ulang.
3. Root'da `render.yaml` bor, Render avtomatik o'qiydi.
4. Environment variables kiriting:
   - `BOT_TOKEN`
   - `PUBLIC_BASE_URL` (`https://service-name.onrender.com`)
   - `WEBHOOK_SECRET`
5. Deploy qiling.

`/health` endpoint ishlasa, bot ham ishlaydi.

## 3) Muhim eslatmalar

- Bot faqat **public** linklardan yuklaydi.
- Platforma siyosatlari va mualliflik huquqiga rioya qiling.
- Juda katta videolar Telegram limitiga tushmasligi mumkin.
- `yt-dlp` ba'zi manbalarda vaqtincha ishlamasligi normal holat.

## 4) Flutter bilan bog'lash (oddiy)

Sizning Flutter ilovangiz ichida "Bot" tugmasidan quyidagi linkni ochsangiz bo'ladi:

`https://t.me/<SIZNING_BOT_USERNAME>`

Shunda foydalanuvchi ilova ichidan botga o'tib ishlata oladi.
