"""
AOSSIE Evangelist Acceptance Certificate Generator
Inspired by: https://github.com/Coders-HQ/CodersHQ

Generates a certificate PNG by overlaying text onto a template image.
Template: .github/certificate-template.png  (A4 landscape, ~2480x1754 px recommended)

Usage:
    python generate_certificate.py \
        --name "Ankit Kumar" \
        --university "IIT Patna" \
        --region "India" \
        --date "March 2, 2026" \
        --output certificate.png
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageFont


TEMPLATE_PATH = Path(__file__).parent.parent / "certificate-template.png"

# ── Colours ───────────────────────────────────────────────────────────────────
GOLD   = (197, 155,  55)
DARK   = ( 30,  30,  45)
WHITE  = (255, 255, 255)
GREY   = (150, 150, 160)

# ── Layout constants (fractions of image size) ─────────────────────────────────
# All positions are relative so the cert looks right at any resolution.
NAME_Y_FRAC       = 0.52   # vertical centre of name line
UNIV_Y_FRAC       = 0.62
DATE_Y_FRAC       = 0.74
CERT_ID_Y_FRAC    = 0.88


def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try common system fonts, fall back to default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSerif-Bold.ttf",
        "DejaVuSerif-Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def load_font_regular(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSerif.ttf",
        "DejaVuSerif.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def centred_x(draw: ImageDraw.ImageDraw, text: str, font, img_width: int) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    return (img_width - text_width) // 2


def generate_certificate(
    name: str,
    university: str,
    region: str,
    date: str,
    output: str = "certificate.png",
) -> str:
    # ── Load or create canvas ──────────────────────────────────────────────────
    if TEMPLATE_PATH.exists():
        img = Image.open(TEMPLATE_PATH).convert("RGBA")
        W, H = img.size
    else:
        # No template supplied — generate a clean certificate from scratch
        W, H = 2480, 1754   # A4 landscape @ 300 dpi
        img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        # ── Background gradient-ish fill ───────────────────────────────────────
        for y in range(H):
            t = y / H
            r = int(12 + (28  - 12)  * t)
            g = int(18 + (35  - 18)  * t)
            b = int(40 + (65  - 40)  * t)
            draw.line([(0, y), (W, y)], fill=(r, g, b))

        # ── Outer & inner border ───────────────────────────────────────────────
        pad, inner = 40, 55
        draw.rectangle([pad, pad, W - pad, H - pad],
                       outline=GOLD, width=6)
        draw.rectangle([inner, inner, W - inner, H - inner],
                       outline=GOLD, width=2)

        # ── Header: AOSSIE logo text ───────────────────────────────────────────
        title_font  = load_font(int(H * 0.072))
        header_font = load_font_regular(int(H * 0.038))
        body_font   = load_font_regular(int(H * 0.033))
        small_font  = load_font_regular(int(H * 0.022))

        org_text = "AOSSIE"
        draw.text(
            (centred_x(draw, org_text, title_font, W), int(H * 0.09)),
            org_text, font=title_font, fill=GOLD,
        )

        sub_text = "Australian Open Source Software Innovation and Education"
        draw.text(
            (centred_x(draw, sub_text, small_font, W), int(H * 0.19)),
            sub_text, font=small_font, fill=GREY,
        )

        # ── Divider line ───────────────────────────────────────────────────────
        div_y = int(H * 0.27)
        draw.line([(int(W * 0.2), div_y), (int(W * 0.8), div_y)],
                  fill=GOLD, width=3)

        # ── Body text ─────────────────────────────────────────────────────────
        cert_text = "Certificate of Acceptance"
        draw.text(
            (centred_x(draw, cert_text, header_font, W), int(H * 0.30)),
            cert_text, font=header_font, fill=WHITE,
        )

        presented_text = "This certifies that"
        draw.text(
            (centred_x(draw, presented_text, body_font, W), int(H * 0.41)),
            presented_text, font=body_font, fill=GREY,
        )

        # ── Applicant name (large, gold) ───────────────────────────────────────
        name_font = load_font(int(H * 0.08))
        draw.text(
            (centred_x(draw, name, name_font, W), int(H * NAME_Y_FRAC)),
            name, font=name_font, fill=GOLD,
        )

        # ── Name underline ────────────────────────────────────────────────────
        ul_y = int(H * (NAME_Y_FRAC + 0.095))
        name_bbox = draw.textbbox((0, 0), name, font=name_font)
        name_w = name_bbox[2] - name_bbox[0]
        ul_x = (W - name_w) // 2
        draw.line([(ul_x, ul_y), (ul_x + name_w, ul_y)], fill=GOLD, width=2)

        # ── Role text ─────────────────────────────────────────────────────────
        role_text = "has been officially accepted as an AOSSIE Evangelist"
        draw.text(
            (centred_x(draw, role_text, body_font, W), int(H * 0.63)),
            role_text, font=body_font, fill=WHITE,
        )

        # ── University & region ────────────────────────────────────────────────
        univ_text = f"representing  {university}  ·  {region}"
        draw.text(
            (centred_x(draw, univ_text, body_font, W), int(H * UNIV_Y_FRAC)),
            univ_text, font=body_font, fill=GREY,
        )

        # ── Divider ────────────────────────────────────────────────────────────
        draw.line([(int(W * 0.35), int(H * 0.77)), (int(W * 0.65), int(H * 0.77))],
                  fill=GOLD, width=1)

        # ── Date ──────────────────────────────────────────────────────────────
        draw.text(
            (centred_x(draw, date, small_font, W), int(H * DATE_Y_FRAC)),
            date, font=small_font, fill=GREY,
        )

        # ── Certificate ID ────────────────────────────────────────────────────
        import hashlib
        cert_id = "CERT-" + hashlib.sha1(f"{name}{date}".encode()).hexdigest()[:8].upper()
        cert_id_text = f"Certificate ID: {cert_id}"
        draw.text(
            (centred_x(draw, cert_id_text, small_font, W), int(H * CERT_ID_Y_FRAC)),
            cert_id_text, font=small_font, fill=GREY,
        )

        # ── Website footer ────────────────────────────────────────────────────
        footer = "aossie.org"
        draw.text(
            (centred_x(draw, footer, small_font, W), int(H * 0.92)),
            footer, font=small_font, fill=GOLD,
        )

    # ── Save as PNG ────────────────────────────────────────────────────────────
    final = img.convert("RGB")
    final.save(output, "PNG", dpi=(300, 300))
    print(f"Certificate saved → {output}")
    return output


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AOSSIE Evangelist Certificate")
    parser.add_argument("--name",       required=True,  help="Recipient full name")
    parser.add_argument("--university", required=True,  help="University name")
    parser.add_argument("--region",     required=True,  help="Country / Region")
    parser.add_argument("--date",       default=datetime.today().strftime("%B %d, %Y"),
                        help="Date string (default: today)")
    parser.add_argument("--output",     default="certificate.png", help="Output file path")
    args = parser.parse_args()

    generate_certificate(
        name=args.name,
        university=args.university,
        region=args.region,
        date=args.date,
        output=args.output,
    )
