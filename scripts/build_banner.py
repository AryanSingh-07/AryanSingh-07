"""Render a compact looping GIF header; no external image service required."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 900, 250
FONT = next(p for p in ("C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf") if Path(p).exists())
font = lambda size: ImageFont.truetype(FONT, size)
base = Image.new("RGB", (W, H), "#111427")
d = ImageDraw.Draw(base)
for y in range(H):
    t = y / H
    d.line((0, y, W, y), fill=(int(17+16*t), 20, int(39+23*t)))
d.rounded_rectangle((1, 1, W-2, H-2), 22, outline="#514778", width=2)
d.text((42, 28), "ARYANSINGH-07  /  BUILD LOG", font=font(14), fill="#86e5ec")
d.text((40, 65), "Aryan Singh", font=font(49), fill="#f4f1ff")
d.text((43, 133), "Full-stack development  /  AI  /  Data", font=font(19), fill="#c9c2e5")
d.rounded_rectangle((42, 181, 524, 220), 9, fill="#101321", outline="#3c3855")
d.text((57, 191), "> building ideas into software", font=font(16), fill="#8de1c3")
cursor_x = 57 + int(d.textlength("> building ideas into software", font=font(16))) + 9
# Fixed orbital paths with moving colored nodes make the motion easy to see.
cx, cy = 721, 126
for radius in (57, 81, 106):
    d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline="#413a64", width=1)
d.text((cx-39, cy-29), "</>", font=font(44), fill="#eeeaff")
frames = []
for index in range(32):
    frame = base.copy()
    draw = ImageDraw.Draw(frame)
    phase = index / 32 * math.tau
    for radius, offset, color in ((57, 0, "#77e5ee"), (81, 2.1, "#bc9cff"), (106, 4.2, "#ff86bb")):
        x = cx + math.cos(phase+offset)*radius
        y = cy + math.sin(phase+offset)*radius
        draw.ellipse((x-6, y-6, x+6, y+6), fill=color)
    if index % 16 < 8:
        draw.rectangle((cursor_x, 192, cursor_x+7, 208), fill="#8de1c3")
    frames.append(frame)
palette = frames[0].quantize(colors=64)
frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
frames[0].save(ROOT / "assets/banner.gif", save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True)
print("Built assets/banner.gif")
