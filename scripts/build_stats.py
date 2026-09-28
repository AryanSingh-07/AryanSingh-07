"""Build an animated, self-contained GitHub profile statistics SVG."""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


USERNAME = "AryanSingh-07"
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "stats.svg"
GIF_OUTPUT = OUTPUT.with_suffix(".gif")


def github_json(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "aryan-profile-stats",
    }
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=20) as response:
        return json.load(response)


def make_gif(metrics, languages, updated: str) -> None:
    """Make a GIF so the statistics animate even when SVG motion is blocked."""
    width, height = 1200, 425
    base = Image.new("RGB", (width, height))
    pixels = base.load()
    for y in range(height):
        for x in range(width):
            t = (x / width + y / height) / 2
            pixels[x, y] = (
                int(20 + 43 * t),
                int(22 + 7 * t),
                int(45 + 44 * t),
            )

    font_path = next(
        (path for path in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ) if Path(path).exists()),
        None,
    )

    def font(size):
        return ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()

    title_font, value_font = font(29), font(37)
    body_font, small_font = font(17), font(13)
    top = languages.most_common(4)
    maximum = top[0][1] if top else 1
    frames = []
    steps = 19
    for frame_index in range(steps):
        progress = frame_index / (steps - 1)
        eased = 1 - (1 - progress) ** 3
        image = base.copy()
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=24, outline="#574675", width=2)
        draw.text((55, 27), "GitHub by the numbers", font=title_font, fill="#ffffff")
        draw.text((935, 37), f"Updated {updated}", font=small_font, fill="#c6c3dd")

        for index, (label, value) in enumerate(metrics):
            x = 55 + index * 280
            draw.rounded_rectangle((x, 83, x + 250, 195), radius=17, fill="#31294e", outline="#615474")
            draw.text((x + 20, 101), str(round(value * eased)), font=value_font, fill="#ffffff")
            draw.text((x + 20, 156), label, font=small_font, fill="#c9c4df")

        draw.text((55, 215), "Repositories by primary language", font=body_font, fill="#ffffff")
        for index, (language, count) in enumerate(top):
            y = 269 + index * 35
            draw.text((55, y - 6), language, font=body_font, fill="#e4e1f5")
            draw.rounded_rectangle((275, y, 995, y + 16), radius=8, fill="#494264")
            bar_width = round(720 * count / maximum * eased)
            if bar_width > 0:
                draw.rounded_rectangle((275, y, 275 + bar_width, y + 16), radius=min(8, bar_width // 2), fill="#6fe3ea")
            draw.text((1020, y - 6), str(count), font=body_font, fill="#ffffff")
        frames.append(image.quantize(colors=96))

    preview = frames[-1]
    preview.save(
        GIF_OUTPUT,
        save_all=True,
        append_images=frames,
        duration=[900] + [80] * (steps - 1) + [1700],
        loop=0,
        optimize=True,
    )


def main() -> None:
    repos = []
    page = 1
    while True:
        batch = github_json(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"
        )
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    languages = Counter(repo["language"] for repo in repos if repo["language"])
    metrics = [
        ("PUBLIC REPOS", len(repos)),
        ("STARS EARNED", sum(repo["stargazers_count"] for repo in repos)),
        ("FORKS", sum(repo["forks_count"] for repo in repos)),
        ("LANGUAGES", len(languages)),
    ]
    updated = datetime.now(timezone.utc).strftime("%d %b %Y UTC")

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="425" viewBox="0 0 1200 425" role="img" aria-labelledby="title desc">',
        '<title id="title">Aryan Singh GitHub statistics</title>',
        f'<desc id="desc">{len(repos)} public repositories, {metrics[1][1]} stars earned, {metrics[2][1]} forks, and {len(languages)} primary languages. Updated {updated}.</desc>',
        '<defs><linearGradient id="background" x2="1" y2="1"><stop stop-color="#14162d"/><stop offset=".55" stop-color="#242052"/><stop offset="1" stop-color="#3f1c59"/></linearGradient><linearGradient id="bar" x2="1"><stop stop-color="#5de6ec"/><stop offset="1" stop-color="#fa82b4"/></linearGradient></defs>',
        '<style>.card{fill:#ffffff;fill-opacity:.07;stroke:#ffffff;stroke-opacity:.15}.bar{transform-box:fill-box;transform-origin:left;animation:grow 1.1s ease-out both}.reveal{animation:appear .8s ease-out both}@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}@keyframes appear{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}@media(prefers-reduced-motion:reduce){.bar,.reveal{animation:none}}</style>',
        '<rect width="1200" height="425" rx="24" fill="url(#background)"/>',
        '<circle cx="1080" cy="15" r="180" fill="#fb79b4" opacity=".08"/>',
        '<text x="55" y="58" fill="#ffffff" font-family="Arial,sans-serif" font-size="29" font-weight="700">GitHub by the numbers</text>',
        f'<text x="1145" y="55" text-anchor="end" fill="#c6c3dd" font-family="Arial,sans-serif" font-size="14">Updated {updated}</text>',
    ]

    for index, (label, value) in enumerate(metrics):
        x = 55 + index * 280
        svg.extend(
            [
                f'<rect class="card" x="{x}" y="83" width="250" height="112" rx="17"/>',
                f'<text class="reveal" x="{x + 20}" y="139" fill="#ffffff" font-family="Arial,sans-serif" font-size="37" font-weight="700" style="animation-delay:{index * .12:.2f}s">{value}</text>',
                f'<text x="{x + 20}" y="171" fill="#c9c4df" font-family="Arial,sans-serif" font-size="13" letter-spacing="1.3">{label}</text>',
            ]
        )

    svg.append('<text x="55" y="240" fill="#ffffff" font-family="Arial,sans-serif" font-size="20" font-weight="700">Repositories by primary language</text>')
    top = languages.most_common(4)
    maximum = top[0][1] if top else 1
    for index, (language, count) in enumerate(top):
        y = 279 + index * 35
        width = round(720 * count / maximum)
        svg.extend(
            [
                f'<text x="55" y="{y + 5}" fill="#e4e1f5" font-family="Arial,sans-serif" font-size="16">{escape(language)}</text>',
                f'<rect x="275" y="{y - 10}" width="720" height="16" rx="8" fill="#ffffff" opacity=".10"/>',
                f'<rect class="bar" x="275" y="{y - 10}" width="{width}" height="16" rx="8" fill="url(#bar)" style="animation-delay:{index * .15:.2f}s"/>',
                f'<text x="1020" y="{y + 5}" fill="#ffffff" font-family="Arial,sans-serif" font-size="16" font-weight="700">{count}</text>',
            ]
        )
    svg.append('</svg>')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
    make_gif(metrics, languages, updated)
    print(f"Wrote {OUTPUT} and {GIF_OUTPUT} from {len(repos)} public repositories")


if __name__ == "__main__":
    main()
