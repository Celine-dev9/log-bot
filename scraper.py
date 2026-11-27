"""
Website Scraper Module for Human Code Reader Bot
=================================================
Scrapes full multi-page websites using Playwright (visible Chrome browser).
  - Prominently displays the Chrome browser window on screen
  - Performs realistic human scrolling (down, left/right, and back up)
  - Discovers internal pages across the website to build a multi-page project
  - STRICTLY captures code only: HTML, CSS, and JavaScript
  - Completely rejects media assets (images, videos, audio, fonts)
  - Saves each project in an independent folder outside the bot directory
"""

import os
import re
import time
import random
import asyncio
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

import config


def slugify_url(url: str) -> str:
    """Generates a clean directory name from a URL."""
    parsed = urlparse(url)
    host = parsed.netloc.replace("www.", "")
    path = parsed.path.strip("/").replace("/", "_")
    name = f"{host}_{path}" if path else host
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name).strip("_")
    return name or "web_project"


def extract_internal_links(base_url: str, html: str, max_pages: int) -> List[Dict[str, str]]:
    """Extracts unique internal links from the same domain."""
    soup = BeautifulSoup(html, "html.parser")
    base_parsed = urlparse(base_url)
    base_domain = base_parsed.netloc.lower()

    discovered = []
    seen = {base_url.rstrip("/")}

    for a in soup.find_all("a", href=True):
        raw_href = a["href"].strip()
        if not raw_href or raw_href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        full_url = urljoin(base_url, raw_href)
        parsed = urlparse(full_url)

        if parsed.scheme in ("http", "https") and parsed.netloc.lower() == base_domain:
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
            if clean_url not in seen and len(clean_url) > len(parsed.scheme) + 3:
                seen.add(clean_url)

                # Generate clean filename (e.g., about.html, contact.html)
                clean_path = parsed.path.strip("/").replace("/", "_")
                filename = f"{clean_path}.html" if clean_path else f"page_{len(discovered) + 1}.html"
                filename = re.sub(r"[^a-zA-Z0-9.\-_]", "_", filename)
                if not filename.endswith(".html"):
                    filename += ".html"

                discovered.append({"name": filename, "url": full_url})
                if len(discovered) >= max_pages - 1:
                    break

    return discovered


async def _scrape_website_async(
    target_url: str,
    output_root: Optional[str] = None,
    max_pages: Optional[int] = None,
) -> Optional[str]:
    """Asynchronous core scraper using Playwright."""
    output_root = output_root or config.OUTPUT_ROOT
    max_pages = max_pages or getattr(config, "MAX_PAGES_PER_SITE", 6)

    project_slug = slugify_url(target_url)
    project_dir = Path(output_root) / project_slug
    assets_dir = project_dir / "assets"

    assets_dir.mkdir(parents=True, exist_ok=True)

    url_to_local_map = {}
    captured_pages = []

    print(f"\n" + "=" * 65)
    print(f"🌐 [SCRAPER] Launching Chrome Browser for: {target_url}")
    print(f"📁 Destination Folder: {project_dir}")
    print("=" * 65)

    async def handle_response(response):
        """Intercepts and saves ONLY CSS and JavaScript files. Zero image/asset downloads."""
        try:
            url = response.url
            content_type = response.headers.get("content-type", "").lower()
            resource_type = response.request.resource_type

            # Strictly CSS and JS only
            is_css = ("text/css" in content_type) or (resource_type == "stylesheet") or urlparse(url).path.endswith(".css")
            is_js = ("javascript" in content_type) or (resource_type == "script") or urlparse(url).path.endswith(".js")

            # Exclude images, fonts, media, svgs, etc.
            is_asset = any(t in content_type for t in ["image", "font", "audio", "video", "media"])

            if (is_css or is_js) and not is_asset:
                parsed_url = urlparse(url)
                base_name = os.path.basename(parsed_url.path).split("?")[0]

                if not base_name or "." not in base_name:
                    ext = "css" if is_css else "js"
                    base_name = f"script_{int(time.time() * 1000)}_{os.urandom(2).hex()}.{ext}"

                safe_name = re.sub(r"[^a-zA-Z0-9.\-_]", "_", base_name)
                local_path = assets_dir / safe_name

                if 200 <= response.status < 300:
                    body = await response.body()
                    with open(local_path, "wb") as f:
                        f.write(body)
                    url_to_local_map[url] = f"./assets/{safe_name}"
        except Exception:
            pass

    try:
        async with async_playwright() as p:
            # Launch visible Chrome window maximized
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--start-maximized",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                ],
            )

            context = await browser.new_context(
                viewport=None,  # Inherit maximized screen dimensions
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            )

            page = await context.new_page()

            # Apply stealth to mimic real human browsing
            stealth = Stealth()
            await stealth.apply_stealth_async(page)

            page.on("response", handle_response)

            pages_queue = [{"name": "index.html", "url": target_url}]

            page_idx = 0
            while page_idx < len(pages_queue):
                current = pages_queue[page_idx]
                page_idx += 1
                curr_url = current["url"]

                print(f"\n[Browser {page_idx}/{len(pages_queue)}] Navigating to: {curr_url}")

                try:
                    # Navigate and wait for content
                    await page.goto(curr_url, wait_until="domcontentloaded", timeout=45000)
                    try:
                        await page.wait_for_selector("body", state="visible", timeout=15000)
                    except Exception:
                        pass

                    # Prompt visual mouse movement without long delay (every 4 to 5s pace)
                    await asyncio.sleep(1.0)
                    await page.mouse.move(random.randint(300, 750), random.randint(250, 550))

                    print("  ↳ Scrolling and moving mouse (every 4 to 5s pace)...")
                    # 1. Smooth scroll down to bottom
                    await page.evaluate("""
                        async () => {
                            let total = 0;
                            let step = 280;
                            while (total < document.body.scrollHeight && (window.innerHeight + window.scrollY) < document.body.scrollHeight) {
                                window.scrollBy(0, step);
                                total += step;
                                await new Promise(r => setTimeout(r, 80));
                            }
                        }
                    """)

                    # Active mouse movement every 4 to 5 seconds
                    await page.mouse.move(random.randint(250, 850), random.randint(200, 600))
                    await asyncio.sleep(random.uniform(4.0, 5.0))

                    # 2. Horizontal scroll wiggle (left and right)
                    await page.evaluate("""
                        () => {
                            window.scrollBy(160, 0);
                            setTimeout(() => window.scrollBy(-160, 0), 150);
                        }
                    """)

                    await page.mouse.move(random.randint(250, 850), random.randint(200, 600))
                    await asyncio.sleep(random.uniform(4.0, 5.0))

                    # 3. Smooth scroll back up to the top
                    await page.evaluate("""
                        async () => {
                            while (window.scrollY > 0) {
                                window.scrollBy(0, -350);
                                await new Promise(r => setTimeout(r, 60));
                            }
                            window.scrollTo(0, 0);
                        }
                    """)

                    await asyncio.sleep(1.0)

                    raw_html = await page.content()
                    captured_pages.append({"name": current["name"], "url": curr_url, "html": raw_html})
                    print(f"  ↳ Captured: {current['name']}")

                    # If this is the main page, discover internal subpages
                    if page_idx == 1 and len(pages_queue) < max_pages:
                        subpages = extract_internal_links(target_url, raw_html, max_pages)
                        if subpages:
                            print(f"  ↳ Discovered {len(subpages)} internal subpages to mirror.")
                            pages_queue.extend(subpages)

                except Exception as page_err:
                    print(f"  ↳ [Notice] Skipped page due to error: {page_err}")

            await browser.close()

    except Exception as browser_err:
        print(f"[Scraper Error] Browser session encountered an issue: {browser_err}")

    if not captured_pages:
        print("[Scraper] No pages were successfully captured.")
        return None

    # Post-process captured HTML: rewrite CSS and JS paths, and internal navigation links
    print("\n[Scraper] Writing clean HTML, CSS, and JS files into project folder...")
    for p_data in captured_pages:
        soup = BeautifulSoup(p_data["html"], "html.parser")

        # Map external CSS & JS to local saved files
        for tag in soup.find_all(["link", "script"]):
            attr = "href" if tag.name == "link" else "src"
            remote = tag.get(attr)
            if remote:
                abs_url = urljoin(p_data["url"], remote)
                if abs_url in url_to_local_map:
                    tag[attr] = url_to_local_map[abs_url]

        # Map internal links so pages navigate locally
        for a in soup.find_all("a", href=True):
            try:
                abs_href = urljoin(p_data["url"], a["href"])
                match = next((p for p in captured_pages if p["url"].rstrip("/") == abs_href.rstrip("/")), None)
                if match:
                    a["href"] = f"./{match['name']}"
            except Exception:
                pass

        out_file = project_dir / p_data["name"]
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(str(soup))

    print(f"🎉 Scraping complete! Project saved at: {project_dir}")
    return str(project_dir)


def scrape_website(
    target_url: str,
    output_root: Optional[str] = None,
    max_pages: Optional[int] = None,
) -> Optional[str]:
    """
    Synchronous wrapper to scrape a website.
    Returns the path to the newly created project folder, or None on failure.
    """
    try:
        return asyncio.run(_scrape_website_async(target_url, output_root, max_pages))
    except Exception as e:
        print(f"[Scraper Error] {e}")
        return None


if __name__ == "__main__":
    test_url = "https://www.track-trace.com/aircargo"
    result = scrape_website(test_url)
    print(f"Resulting folder: {result}")
