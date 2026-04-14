#!/usr/bin/env python3
"""
Extract SlideShare document slides and save as PDF.
"""

import re
import os
import sys
import time
import requests
import img2pdf
from PIL import Image
from io import BytesIO

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_page(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_slide_image_urls(html: str) -> list[str]:
    """
    SlideShare embeds slide images in JSON inside a <script> tag.
    They appear as slideImage / slide_image_url patterns.
    """
    urls = []

    # Pattern 1: JSON-like "slideImage":"https://..."
    pattern1 = re.findall(r'"slideImage"\s*:\s*"([^"]+)"', html)
    urls.extend(pattern1)

    # Pattern 2: data-full="https://..." inside slide elements
    pattern2 = re.findall(r'data-full="(https://[^"]+\.(?:jpg|jpeg|png)[^"]*)"', html, re.IGNORECASE)
    urls.extend(pattern2)

    # Pattern 3: srcset or src patterns for slide images on CDN
    pattern3 = re.findall(
        r'"(https://(?:image|cdn|media)\.slidesharecdn\.com/[^"]+\.(?:jpg|jpeg|png)(?:\?[^"]*)?)"',
        html,
        re.IGNORECASE,
    )
    urls.extend(pattern3)

    # Pattern 4: look for slide JSON block
    json_block = re.search(r'var\s+slideshow\s*=\s*(\{.*?\});', html, re.DOTALL)
    if json_block:
        block_urls = re.findall(
            r'(https://[^\s"\']+\.(?:jpg|jpeg|png)(?:\?[^\s"\']*)?)',
            json_block.group(1),
        )
        urls.extend(block_urls)

    # Pattern 5: any CDN image URL in the page
    if not urls:
        fallback = re.findall(
            r'(https://(?:image|cdn|media)\.slidesharecdn\.com/[^\s"\'<>]+\.(?:jpg|jpeg|png)(?:\?[^\s"\'<>]*)?)',
            html,
            re.IGNORECASE,
        )
        urls.extend(fallback)

    # Deduplicate preserving order
    seen = set()
    unique = []
    for u in urls:
        # Normalise: replace thumbnail suffixes with full-size
        u = re.sub(r'-320\.jpg', '.jpg', u)
        u = re.sub(r'-170\.jpg', '.jpg', u)
        u = re.sub(r'_thumbnail\.jpg', '.jpg', u)
        if u not in seen:
            seen.add(u)
            unique.append(u)

    return unique


def download_image(url: str, session: requests.Session) -> bytes | None:
    try:
        resp = session.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200 and resp.headers.get("Content-Type", "").startswith("image"):
            return resp.content
    except Exception as e:
        print(f"  Warning: could not download {url}: {e}")
    return None


def images_to_pdf(image_bytes_list: list[bytes], output_path: str):
    pdf_bytes = img2pdf.convert(image_bytes_list)
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)


def main(slideshare_url: str, output_pdf: str):
    print(f"Fetching page: {slideshare_url}")
    html = fetch_page(slideshare_url)

    print("Extracting slide image URLs...")
    slide_urls = extract_slide_image_urls(html)

    if not slide_urls:
        print("ERROR: No slide images found. The page structure may have changed.")
        sys.exit(1)

    print(f"Found {len(slide_urls)} slide(s).")

    session = requests.Session()
    image_bytes_list = []

    for i, url in enumerate(slide_urls, 1):
        print(f"  Downloading slide {i}/{len(slide_urls)}: {url[:80]}...")
        data = download_image(url, session)
        if data:
            # Ensure it's a valid JPEG/PNG (img2pdf needs clean images)
            try:
                img = Image.open(BytesIO(data)).convert("RGB")
                buf = BytesIO()
                img.save(buf, format="JPEG", quality=95)
                image_bytes_list.append(buf.getvalue())
            except Exception as e:
                print(f"    Skipping (bad image): {e}")
        else:
            print(f"    Skipping (download failed).")
        time.sleep(0.3)

    if not image_bytes_list:
        print("ERROR: No images were downloaded successfully.")
        sys.exit(1)

    print(f"\nBuilding PDF from {len(image_bytes_list)} slides...")
    images_to_pdf(image_bytes_list, output_pdf)
    print(f"Saved: {output_pdf}")


if __name__ == "__main__":
    url = "https://es.slideshare.net/slideshow/manual-taller-206-frances/53542947"
    out = "/home/user/Mervellous/manual_taller_206_frances.pdf"
    main(url, out)
