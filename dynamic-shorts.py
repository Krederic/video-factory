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

# Таймкоды: (Текст на экране, Старт в секундах, Конец в секундах)
TIMINGS = [
    ("5 UK CV MISTAKES\nTHAT COST YOU THE JOB", 0, 4.5),
    ("MISTAKE 1:\nNO MEASURABLE ACHIEVEMENTS", 4.5, 10.5),
    ("MISTAKE 2:\nGENERIC STATEMENT", 10.5, 16.5),
    ("MISTAKE 3:\nSPELLING & GRAMMAR", 16.5, 23.0),
    ("MISTAKE 4:\nLONGER THAN 2 PAGES", 23.0, 28.5),
    ("MISTAKE 5:\nNOT TAILORED", 28.5, 33.0),
    ("FIX THESE TODAY!\nSUBSCRIBE FOR MORE", 33.0, 40.0)
]

async def generate_audio():
    print("🎙️ 1/4 Генерируем аудио...")
    communicate = edge_tts.Communicate(TEXT_SCRIPT, VOICE)
    await communicate.save("voice.mp3")

def download_video():
    print("🎥 2/4 Проверяем фоновое видео...")
    if os.path.exists("bg_video.mp4"):
        print("✅ Видео уже скачано, используем его.")
        return True
        
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={VIDEO_QUERY}&orientation=portrait&size=medium&per_page=1"
    response = requests.get(url, headers=headers)
    if response.status_code != 200: return False
    data = response.json()
    if not data.get("videos"): return False
    
    files = data["videos"][0]["video_files"]
    hd_file = next((f for f in files if f["quality"] == "hd"), files[0])
    with open("bg_video.mp4", "wb") as f:
        f.write(requests.get(hd_file["link"]).content)
    return True

def create_text_overlays():
    print("✍️ 3/4 Генерируем динамичные слайды...")
    for i, (text, start, end) in enumerate(TIMINGS):
        img = Image.new('RGBA', (1080, 1920), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        font_main = ImageFont.truetype("DejaVuSans-Bold.ttf", 75)
        font_watermark = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        
        # Наносим водяной знак канала внизу
        wm_text = "@careercriminalss"
        wm_bbox = draw.textbbox((0, 0), wm_text, font=font_watermark)
        wm_x = (1080 - (wm_bbox[2] - wm_bbox[0])) / 2
        draw.text((wm_x, 1600), wm_text, fill=(255, 255, 255, 180), font=font_watermark)
        
        # Центрируем основной текст
        y_pos = 800
        for line in text.split('\n'):
            bbox = draw.textbbox((0, 0), line, font=font_main)
            w = bbox[2] - bbox[0]
            x = (1080 - w) / 2
            
            # Делаем заголовки желтыми, а пояснения белыми
            color = (255, 204, 0, 255) if "MISTAKE" in line or "5 UK" in line or "FIX" in line else (255, 255, 255, 255)
            draw.text((x, y_pos), line, fill=color, font=font_main)
            y_pos += 100
        
        img.save(f"slide_{i}.png")

def render_final_video():
    print("🎬 4/4 Сборка финального динамичного Shorts (FFmpeg)...")
    
    # Строим сложную команду для FFmpeg
    inputs = "-stream_loop -1 -i bg_video.mp4 -i voice.mp3 "
    for i in range(len(TIMINGS)):
        inputs += f"-i slide_{i}.png "
        
    filter_complex = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=aa=0.4[bg];"
    
    last_out = "bg"
    for i, (text, start, end) in enumerate(TIMINGS):
        current_out = f"v{i}"
        filter_complex += f"[{last_out}][{i+2}:v]overlay=0:0:enable='between(t,{start},{end})'[{current_out}];"
        last_out = current_out
        
    cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_complex}" -map "[{last_out}]" -map 1:a -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k -shortest dynamic_shorts.mp4'
    
    os.system(cmd + " -v quiet -stats")
    print("\n✅ ШЕДЕВР ГОТОВ! Сохранено как 'dynamic_shorts.mp4'")

async def main():
    await generate_audio()
    if download_video():
        create_text_overlays()
        render_final_video()

if __name__ == "__main__":
    asyncio.run(main())
