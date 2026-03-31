import asyncio
import os
import re
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, Message
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from yt_dlp import YoutubeDL


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()
RUN_MODE = os.getenv("RUN_MODE", "webhook").strip().lower()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi. .env ichida BOT_TOKEN kiriting.")
if RUN_MODE == "webhook":
    if not PUBLIC_BASE_URL:
        raise RuntimeError("PUBLIC_BASE_URL topilmadi. .env ichida URL kiriting.")
    if not WEBHOOK_SECRET:
        raise RuntimeError("WEBHOOK_SECRET topilmadi. .env ichida secret kiriting.")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
app = FastAPI(title="BrewGo Free Bot Server")
polling_task: asyncio.Task | None = None

URL_RE = re.compile(r"(https?://[^\s]+)", re.IGNORECASE)


def extract_url(text: str) -> str | None:
    match = URL_RE.search(text or "")
    return match.group(1) if match else None


def download_video(url: str) -> tuple[Path, Path]:
    """
    URL dan mp4 video yuklaydi.
    Qaytadi: (temp_dir_path, video_file_path)
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="brewgo_"))
    output_tpl = str(temp_dir / "%(title).80s-%(id)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_tpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        # Telegramga yuborish uchun odatda o'rtacha sifat yetarli
        "format": "bv*[height<=720]+ba/b[height<=720]/b",
        "merge_output_format": "mp4",
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    candidates = sorted(temp_dir.glob("*.mp4"), key=lambda p: p.stat().st_size, reverse=True)
    if not candidates:
        # Ba'zi hollarda ext boshqa bo'lishi mumkin
        any_file = sorted(temp_dir.glob("*"), key=lambda p: p.stat().st_size, reverse=True)
        if not any_file:
            raise RuntimeError("Video fayl topilmadi.")
        return temp_dir, any_file[0]
    return temp_dir, candidates[0]


@dp.message(F.text == "/start")
async def start_handler(message: Message) -> None:
    await message.answer(
        "Salom! Men BrewGo yordamchi botiman.\n\n"
        "Menga YouTube yoki Instagram video havolasini yuboring, "
        "men uni oddiy video fayl qilib yuborishga harakat qilaman.\n\n"
        "<b>Eslatma:</b> Faqat ochiq (public) linklar ishlaydi."
    )


@dp.message(F.text)
async def text_handler(message: Message) -> None:
    url = extract_url(message.text or "")
    if not url:
        await message.answer("Iltimos, YouTube/Instagram video link yuboring.")
        return

    wait_msg = await message.answer("Link tekshirilyapti va video tayyorlanyapti...")
    temp_dir: Path | None = None
    try:
        temp_dir, video_path = await asyncio.to_thread(download_video, url)
        size_mb = video_path.stat().st_size / (1024 * 1024)

        # Telegram bot API cheklovlari uchun xavfsiz ogohlantirish.
        if size_mb > 49:
            await wait_msg.edit_text(
                f"Video juda katta ({size_mb:.1f} MB). "
                "Iltimos, qisqaroq yoki pastroq sifatdagi link yuboring."
            )
            return

        await wait_msg.edit_text("Yuboryapman...")
        await message.answer_video(FSInputFile(video_path))
        await wait_msg.delete()
    except Exception as e:
        await wait_msg.edit_text(
            "Video olishda xatolik bo'ldi.\n"
            "Link private bo'lishi mumkin yoki platforma vaqtincha cheklagan.\n\n"
            f"Texnik xabar: <code>{str(e)[:300]}</code>"
        )
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "service": "brewgo-bot"}


@app.post("/webhook/" + WEBHOOK_SECRET)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    update = await request.json()
    await dp.feed_raw_update(bot, update)
    return JSONResponse({"ok": True})


@app.on_event("startup")
async def on_startup() -> None:
    global polling_task
    if RUN_MODE == "polling":
        await bot.delete_webhook(drop_pending_updates=True)
        polling_task = asyncio.create_task(dp.start_polling(bot))
    else:
        webhook_url = f"{PUBLIC_BASE_URL}/webhook/{WEBHOOK_SECRET}"
        await bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    global polling_task
    if polling_task:
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass
    await bot.session.close()

