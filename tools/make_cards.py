"""Build the prize cards: each card's painting behind its prize level's frame, with the level and the character's name
stamped on. Not part of the game; run it on a Mac after adding or changing a card (docs/prize-cards.md).

    uv run --with pillow python tools/make_cards.py            # every card in assets/card_art/cards.json
    uv run --with pillow python tools/make_cards.py tiny_tut   # only the cards named

Each frame in assets/card_frames/ has a magenta centre. The magenta (and, on the mini candy frame, the black band
around it) becomes see-through, the painting is scaled to fill that opening, and the frame goes on top. Near-white
outside a frame becomes black, to match the black mat. The text uses the game's font. Each card is saved as a
1024x768 JPG: 4:3, the shape of the Pi's display.
"""
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "assets/card_art/cards.json"
FONT = ROOT / "assets/fonts/Creepster-Regular.ttf"
OUT_SIZE = (1024, 768)

# Plaque boxes are in each frame image's own pixels (2400x1792): (left, top, right, bottom)
LEVELS = {
    "mini_candy": {
        "frame": ROOT / "assets/card_frames/mini_candy.png",
        "title": "MINI CANDY",
        "title_box": (963, 120, 1434, 249),
        "name_box": (780, 1530, 1574, 1676),
        "fill": (236, 222, 190), "stroke": (30, 18, 10),
        "clear_black_band": True,
    },
    "mini_boss": {
        "frame": ROOT / "assets/card_frames/mini_boss.png",
        "title": "PLAYDOUGH",
        "title_box": (1017, 120, 1512, 227),
        "name_box": (753, 1566, 1638, 1691),
        "fill": (120, 255, 60), "stroke": (12, 30, 8),
        "clear_black_band": False,
    },
    "final_boss": {
        "frame": ROOT / "assets/card_frames/final_boss.png",
        "title": "FULL SIZE",
        "title_box": (1000, 82, 1400, 176),
        "name_box": (820, 1606, 1590, 1716),
        "fill": (245, 90, 35), "stroke": (25, 5, 2),
        "clear_black_band": False,
    },
}


def flood(seed, allowed):
    """Grow `seed` (a True/False mask) through neighbouring pixels where `allowed` is True."""
    h, w = allowed.shape
    out = seed.copy()
    queue = deque(zip(*np.nonzero(seed)))
    while queue:
        y, x = queue.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and allowed[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True
                queue.append((ny, nx))
    return out


def load_frame(level):
    """The level's frame with its opening see-through, and the opening's box (left, top, right, bottom)."""
    a = np.asarray(Image.open(level["frame"]).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # magenta, and the darker purple where the image model shaded it: red and blue both well above green
    hole = (r - g > 40) & (b - g > 40) & (abs(r - b) < 110)
    if level["clear_black_band"]:
        hole = flood(hole, hole | (a.max(-1) < 40))
    white = a.min(-1) > 200
    edge = np.zeros_like(white)
    edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
    a = a.copy()
    a[flood(white & edge, white)] = 0
    alpha = np.where(hole, 0, 255).astype("uint8")
    # soften the cut by a pixel, so its edge is not jagged
    alpha = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    frame = Image.fromarray(np.dstack([a.astype("uint8"), np.asarray(alpha)]), "RGBA")
    ys, xs = np.nonzero(hole)
    return frame, (xs.min(), ys.min(), xs.max(), ys.max())


def trim_bars(art):
    """Cut off flat bands the image model sometimes adds at the top or bottom, then centre-crop back to 4:3."""
    rows = np.nonzero(np.asarray(art).astype(int).std(axis=(1, 2)) > 12)[0]
    if len(rows):
        art = art.crop((0, rows[0], art.width, rows[-1] + 1))
    width = round(art.height * 4 / 3)
    if width < art.width:
        left = (art.width - width) // 2
        return art.crop((left, 0, left + width, art.height))
    height = round(art.width * 3 / 4)
    top = (art.height - height) // 2
    return art.crop((0, top, art.width, top + height))


def stamp(img, text, box, fill, stroke):
    """Write `text` centred in `box`, shrunk until it fits, with an outline and a soft shadow."""
    left, top, right, bottom = box
    draw = ImageDraw.Draw(img)
    size = int((bottom - top) * 0.78)
    while size > 10:
        font = ImageFont.truetype(str(FONT), size)
        x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font, stroke_width=max(2, size // 12))
        if x1 - x0 <= (right - left) * 0.9 and y1 - y0 <= (bottom - top) * 0.9:
            break
        size -= 2
    cx, cy = (left + right) / 2, (top + bottom) / 2
    outline = max(2, size // 12)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((cx + size * 0.05, cy + size * 0.07), text, font=font, anchor="mm",
                                fill=(0, 0, 0, 180), stroke_width=outline, stroke_fill=(0, 0, 0, 180))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(size * 0.06)))
    draw.text((cx, cy), text, font=font, anchor="mm", fill=fill, stroke_width=outline, stroke_fill=stroke)


def make_card(art_path, level_name, name, frames):
    level = LEVELS[level_name]
    if level_name not in frames:
        frames[level_name] = load_frame(level)
    frame, (left, top, right, bottom) = frames[level_name]
    card = Image.new("RGBA", frame.size, (0, 0, 0, 255))
    art = trim_bars(Image.open(art_path).convert("RGB"))
    # cover the opening, reaching a little under the frame
    scale = max((right - left) * 1.04 / art.width, (bottom - top) * 1.04 / art.height)
    art = art.resize((round(art.width * scale), round(art.height * scale)), Image.LANCZOS)
    card.paste(art, (round((left + right - art.width) / 2), round((top + bottom - art.height) / 2)))
    card.alpha_composite(frame)
    stamp(card, level["title"], level["title_box"], level["fill"], level["stroke"])
    stamp(card, name.upper(), level["name_box"], level["fill"], level["stroke"])
    return card.convert("RGB").resize(OUT_SIZE, Image.LANCZOS)


def main(only):
    frames = {}
    for card in json.loads(CARDS.read_text()):
        slug = Path(card["out"]).stem
        if only and slug not in only:
            continue
        out = ROOT / card["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        make_card(ROOT / card["art"], card["level"], card["name"], frames).save(out, quality=92)
        print("made", card["out"])


if __name__ == "__main__":
    main(sys.argv[1:])
