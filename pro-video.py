import os
import asyncio
import requests
import edge_tts
from PIL import Image, ImageDraw, ImageFont

PEXELS_API_KEY = "eW6q8Fl2clKZ17eRft32vjnxuWJ9Y4RaHd5fhNlhpLBltCCxBNWZDDgf"
VOICE = "en-GB-SoniaNeural"
VIDEO_QUERY = "corporate office laptop"

TEXT_SCRIPT = """
5 CV mistakes that keep you from getting hired in the UK. 
Number 1: No measurable achievements. UK employers want numbers, not just duties.
Number 2: A generic personal statement. If it applies to anyone, it applies to no one.
Number 3: Spelling and grammar errors. One typo can ruin your chances.
Number 4: Making it longer than two pages. Keep it concise.
And Number 5: Not tailoring it to the job description. 
Fix these today, and subscribe for more career tips!
"""

async def generate_audio():
    print("🎙️ 1/4 Генерируем британскую озвучку...")
    communicate = edge_tts.Communicate(TEXT_SCRIPT, VOICE)
    await communicate.save("voice.mp3")

def download_video():
    print("🎥 2/4 Ищем стильное фоновое видео на Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={VIDEO_QUERY}&orientation=portrait&size=medium&per_page=1"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Ошибка Pexels API. Код: {response.status_code}")
        return False
    data = response.json()
    if not data.get("videos"):
        print("❌ Видео не найдено.")
        return False
    files = data["videos"][0]["video_files"]
    hd_file = next((f for f in files if f["quality"] == "hd"), files[0])
    with open("bg_video.mp4", "wb") as f:
        f.write(requests.get(hd_file["link"]).content)
    return True

def create_text_overlay():
    print("✍️ 3/4 Создаем графику с заголовками...")
    img = Image.new('RGBA', (1080, 1920), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font_main = ImageFont.truetype("DejaVuSans-Bold.ttf", 90)
    font_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
    
    draw.text((100, 750), "5 UK CV MISTAKES", fill=(255, 255, 255, 255), font=font_main)
    draw.text((100, 870), "THAT COST YOU THE JOB", fill=(255, 204, 0, 255), font=font_sub)
    draw.text((100, 1700), "@careercriminalss", fill=(255, 255, 255, 180), font=font_sub)
    img.save("overlay.png")

def render_final_video():
    print("🎬 4/4 Рендерим финальный Shorts в FFmpeg...")
    cmd = (
        'ffmpeg -y -stream_loop -1 -i bg_video.mp4 -i overlay.png -i voice.mp3 '
        '-filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=aa=0.5[dark_bg];'
        '[dark_bg][1:v]overlay=0:0[outv]" '
        '-map "[outv]" -map 2:a '
        '-c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k -shortest final_shorts.mp4'
    )
    os.system(cmd + " -v quiet -stats")
    print("\n✅ ГОТОВО! Видео сохранено как 'final_shorts.mp4'")

async def main():
    await generate_audio()
    if download_video():
        create_text_overlay()
        render_final_video()

if __name__ == "__main__":
    asyncio.run(main())
