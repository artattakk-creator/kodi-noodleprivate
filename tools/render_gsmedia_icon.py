#!/usr/bin/env python3
"""Deterministic GS Media Repository icon for Kodi (256x256 PNG).

A dark cinema-clapperboard/play identity with a luminous cyan/blue halo.
The source is kept in Git; build writes actual PNG into addon.zip and into
the published repository icon URL. Pillow is an existing publish dependency.
"""
from pathlib import Path


def render(destination):
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    import math

    S = 3
    W = H = 256 * S
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)

    def P(n):
        return int(n * S)

    im = Image.new("RGBA", (W, H), (3, 12, 27, 255))
    px = im.load()
    for y in range(H):
        for x in range(W):
            radial = max(0, 1 - math.hypot((x / S - 125) / 180, (y / S - 117) / 155))
            bottom = max(0, (y / S - 140) / 125)
            px[x, y] = (
                int(3 + 3 * radial + 1 * bottom),
                int(12 + 22 * radial + 7 * bottom),
                int(27 + 36 * radial + 21 * bottom), 255,
            )

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.rounded_rectangle((P(9), P(9), P(246), P(246)), radius=P(37),
                        outline=(0, 190, 255, 195), width=P(5))
    g.ellipse((P(10), P(82), P(250), P(183)), outline=(0, 157, 255, 245), width=P(7))
    g.polygon([(P(111), P(104)), (P(111), P(165)), (P(169), P(134))],
              fill=(0, 235, 255, 240))
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(P(10))))

    d = ImageDraw.Draw(im)
    d.rounded_rectangle((P(7), P(7), P(248), P(248)), radius=P(40),
                        outline=(0, 207, 255, 255), width=P(2))
    d.arc((P(8), P(79), P(248), P(193)), 180, 358,
          fill=(0, 175, 255, 255), width=P(7))
    d.arc((P(16), P(90), P(242), P(191)), 8, 170,
          fill=(4, 65, 204, 255), width=P(6))

    # Clapperboard and illuminated cinema-play emblem.
    d.rounded_rectangle((P(57), P(76), P(199), P(154)), radius=P(9),
                        fill=(4, 19, 39, 255), outline=(58, 150, 199, 255), width=P(2))
    d.polygon([(P(52), P(65)), (P(188), P(34)), (P(198), P(53)), (P(61), P(88))],
              fill=(12, 39, 73, 255), outline=(41, 136, 189, 255), width=P(2))
    for k in range(5):
        ox = 61 + k * 26
        d.polygon([(P(ox), P(63 - k * 6)), (P(ox + 16), P(59 - k * 6)),
                   (P(ox + 24), P(74 - k * 6)), (P(ox + 7), P(78 - k * 6))],
                  fill=(218, 237, 254, 255))
    d.rounded_rectangle((P(57), P(76), P(199), P(92)), radius=P(3),
                        fill=(18, 34, 57, 255), outline=(45, 158, 217, 255), width=P(1))
    for k in range(5):
        ox = 65 + k * 26
        d.polygon([(P(ox), P(77)), (P(ox + 15), P(77)),
                   (P(ox + 24), P(91)), (P(ox + 9), P(91))],
                  fill=(220, 236, 251, 255))
    d.polygon([(P(112), P(99)), (P(112), P(143)), (P(153), P(121))],
              fill=(4, 225, 255, 255))
    d.line([(P(112), P(99)), (P(153), P(121)), (P(112), P(143))],
           fill=(187, 254, 255, 255), width=P(2))

    for preferred in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ):
        if Path(preferred).is_file():
            fontfile = preferred
            break
    else:
        raise RuntimeError("GS Media artwork needs a DejaVu or Liberation bold TTF")

    def center(text, y, size, color, stroke=0):
        f = ImageFont.truetype(fontfile, P(size))
        box = d.textbbox((0, 0), text, font=f, stroke_width=P(stroke))
        x = (W - (box[2] - box[0])) / 2 - box[0]
        d.text((int(x), P(y)), text, font=f, fill=color,
               stroke_width=P(stroke), stroke_fill=(4, 22, 49, 255))

    center("GS", 147, 46, (232, 249, 255, 255), 1)
    center("MEDIA", 193, 27, (12, 219, 253, 255), 0)
    center("REPOSITORY", 224, 12, (215, 237, 253, 255), 0)
    im = im.convert("RGB").resize((256, 256), Image.Resampling.LANCZOS)
    im.save(dest, "PNG", optimize=True)
    return dest


if __name__ == "__main__":
    render(Path(__file__).resolve().parents[1] / "src/repository.gsmedia/icon.png")
