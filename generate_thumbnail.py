import os, io, random, requests
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

SCENIC_STYLES = [
    "stunning Indian woman in traditional saree, Taj Mahal, sunrise",
    "elegant Indian woman in lehenga choli, Jaipur, Hawa Mahal",
    "beautiful Indian woman in salwar kameez, Varanasi, Ganges river",
    "Indian woman at Kerala backwaters, houseboat, golden hour",
    "gorgeous Indian woman in modern fusion wear, Mumbai skyline sunset",
    "beautiful Indian woman, Udaipur, Lake Palace, warm golden light",
    "Indian woman in traditional attire, Himachal Pradesh, mountain view",
    "elegant Indian woman, Goa beach, palm trees, zen atmosphere",
]


def generate_scenic_image(category_english: str, category_hindi: str, output_path: str):
    scenic_img = None
    if POLLINATIONS_API_KEY:
        for attempt in range(3):
            style = random.choice(SCENIC_STYLES)
            prompt = f"Professional YouTube thumbnail background, {style}, 16:9 landscape, high contrast, vibrant, no text"
            try:
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1920&height=1080&nologo=true"
                resp = requests.get(url, timeout=60)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    scenic_img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                    scenic_img = scenic_img.resize((1920, 1080), Image.LANCZOS)
                    print(f"[thumbnail] AI scenic background generated")
                    break
            except Exception as e:
                print(f"[thumbnail] Attempt {attempt+1} failed ({str(e)[:60]}), retrying..." if attempt < 2 else f"[thumbnail] All AI attempts failed")

    if scenic_img is None:
        scenic_img = Image.new('RGB', (1920, 1080), (45, 35, 65))
        draw = ImageDraw.Draw(scenic_img)
        for y in range(1080):
            ratio = y / 1080
            if ratio < 0.5:
                r, g, b = 65, 50, 95
            else:
                r = int(65 + (45 - 65) * ((ratio - 0.5) * 2))
                g = int(50 + (35 - 50) * ((ratio - 0.5) * 2))
                b = int(95 + (65 - 95) * ((ratio - 0.5) * 2))
            draw.rectangle([(0, y), (1920, y + 1)], fill=(r, g, b))
        print(f"[thumbnail] Using gradient fallback background")

    overlay = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Semi-transparent dark overlay for readability
    draw.rectangle([(0, 0), (1920, 1080)], fill=(0, 0, 0, 100))

    en_fonts = [str(Path(__file__).parent / "fonts" / "DejaVuSans-Bold.ttf"),
                "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    lang_fonts = [str(Path(__file__).parent / "fonts" / "NotoSansDevanagari-Bold.ttf"),
                  "C:/Windows/Fonts/arialbd.ttf"]

    def load_font(paths, size):
        for p in paths:
            if Path(p).exists():
                try: return ImageFont.truetype(p, size)
                except: continue
        return ImageFont.load_default()

    f_big = load_font(en_fonts, 130)
    f_cat = load_font(lang_fonts, 90)
    f_sub = load_font(en_fonts, 55)
    f_brand = load_font(en_fonts, 45)

    # Yellow banner at top
    draw.rounded_rectangle([(0, 0), (1920, 130)], radius=0, fill=(255, 210, 0, 230))
    draw.text((960, 65), "120 HINDI PHRASES", fill=(45, 35, 65), font=f_big, anchor="mm")

    # Category badge
    cat_text = category_english.upper()
    bb = draw.textbbox((0, 0), cat_text, font=f_cat)
    cw = bb[2] - bb[0]
    cx = (1920 - cw) // 2
    draw.rounded_rectangle([(cx - 30, 250), (cx + cw + 30, 400)], radius=20, fill=(120, 40, 200, 230))
    draw.text((960, 325), cat_text, fill=(255, 255, 255), font=f_cat, anchor="mm")

    # 10 MINUTE LESSON badge
    draw.rounded_rectangle([(960 - 200, 480), (960 + 200, 570)], radius=15, fill=(0, 0, 0, 180))
    draw.text((960, 525), "10 MINUTE LESSON", fill=(255, 210, 0), font=f_sub, anchor="mm")

    # Branding
    bb = draw.textbbox((0, 0), "VELOCITY HINDI", font=f_brand)
    bw = bb[2] - bb[0]
    draw.text(((1920 - bw) // 2, 950), "VELOCITY HINDI", fill=(200, 200, 200), font=f_brand)

    scenic_img = Image.alpha_composite(scenic_img.convert('RGBA'), overlay).convert('RGB')

    thumb_bytes = io.BytesIO()
    quality = 85
    scenic_img.save(thumb_bytes, format="JPEG", quality=quality)
    while thumb_bytes.tell() > 2097152 and quality > 10:
        quality -= 10
        thumb_bytes = io.BytesIO()
        scenic_img.save(thumb_bytes, format="JPEG", quality=quality)
    thumb_bytes.seek(0)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(thumb_bytes.read())
    print(f"[thumbnail] Final thumbnail saved to {output_path}")
    return output_path
