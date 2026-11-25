import asyncio
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup

# 1. CONFIGURATION: Define targeted routes and local workspace
BASE_URL = ''
PAGES_TO_MIRROR = [
    {'name': 'index.html', 'url': 'https://www.track-trace.com/aircargo'},


]

# Path setup relative to the script location
SITE_DIR = Path(__file__).parent / 'mirrors' / 'cargo-track-2'
ASSETS_DIR = SITE_DIR / 'assets'

# Safely construct output folder architecture
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

url_to_local_map = {}
captured_html_pages = []

async def handle_response(response):
    """Background network interceptor to harvest assets (images, css, js, fonts)."""
    url = response.url
    headers = response.headers
    content_type = headers.get('content-type', '').lower()
    resource_type = response.request.resource_type

    if any(t in content_type for t in ['image', 'css', 'font', 'javascript']) or \
       resource_type in ['script', 'stylesheet']:
        try:
            # Generate a sanitized filename
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path).split('?')[0]
            
            if not filename or '.' not in filename:
                ext = 'js' if 'javascript' in content_type else \
                      'css' if 'css' in content_type else \
                      'png' if 'image' in content_type else 'woff2'
                filename = f"asset_{int(time.time() * 1000)}_{os.urandom(2).hex()}.{ext}"

            filename = re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)
            local_file_path = ASSETS_DIR / filename

            # Download asset if successful
            if 200 <= response.status < 300:
                body = await response.body()
                with open(local_file_path, 'wb') as f:
                    f.write(body)
                url_to_local_map[url] = f"./assets/{filename}"
        except Exception:
            pass

async def run_mirror():
    print("🚀 Launching Playwright (Python) mirror engine...")
    
    async with async_playwright() as p:
        # Launching Chromium with common anti-detection flags
        browser = await p.chromium.launch(headless=False, args=[
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--window-size=1920,1080'
        ])
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Apply stealth to bypass bot detection
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        # Hook the response event
        page.on('response', handle_response)

        for page_target in PAGES_TO_MIRROR:
            target_url = page_target['url'].strip()
            print(f"\n🌐 [Processing]: {target_url}")
            
            try:
                # 1. Navigation. 'load' is often safer for sites with continuous data streams
                await page.goto(target_url, wait_until='load', timeout=120000)
                
                # 2. Wait for main content
                await page.wait_for_selector('body', state='visible', timeout=30000)

                # 3. dynamic animation buffer
                await asyncio.sleep(5)

                # 4. Trigger Lazy Loading via smooth scroll
                print('↕️ Scrolling to trigger lazy-loaded content...')
                await page.evaluate("""
                    async () => {
                        await new Promise((resolve) => {
                            let totalHeight = 0;
                            let distance = 100;
                            let timer = setInterval(() => {
                                let scrollHeight = document.body.scrollHeight;
                                window.scrollBy(0, distance);
                                totalHeight += distance;
                                if (totalHeight >= scrollHeight) {
                                    clearInterval(timer);
                                    window.scrollTo(0, 0); 
                                    resolve();
                                }
                            }, 100);
                        });
                    }
                """)

                # 5. Freeze SVGs for static rendering
                await page.evaluate("""
                    () => {
                        document.querySelectorAll('svg').forEach(svg => {
                            svg.setAttribute('aria-hidden', 'false');
                            svg.style.display = 'inline-block';
                            const style = window.getComputedStyle(svg);
                            svg.style.color = style.color;
                            svg.style.fill = style.fill || 'currentColor';
                        });
                    }
                """)

                # Save HTML and Meta
                raw_html = await page.content()
                captured_html_pages.append({'name': page_target['name'], 'html': raw_html})
                print(f"📥 Captured: {page_target['name']}")

            except Exception as e:
                print(f"❌ Error on {target_url}: {e}")

        await browser.close()
        
    print('\n🛑 Rewriting internal links and asset paths...')

    # Post-processing captured HTML using BeautifulSoup
    for page_data in captured_html_pages:
        soup = BeautifulSoup(page_data['html'], 'html.parser')

        # Map assets (CSS, JS, Images)
        for tag in soup.find_all(['img', 'link', 'script']):
            attr = 'href' if tag.name == 'link' else 'src'
            remote_url = tag.get(attr)
            if remote_url:
                try:
                    abs_url = urljoin(BASE_URL, remote_url)
                    if abs_url in url_to_local_map:
                        tag[attr] = url_to_local_map[abs_url]
                except Exception:
                    pass

        # Map internal links for offline navigation
        for a in soup.find_all('a', href=True):
            try:
                abs_href = urljoin(BASE_URL, a['href'])
                match = next((p for p in PAGES_TO_MIRROR if p['url'].rstrip('/') == abs_href.rstrip('/')), None)
                if match:
                    a['href'] = f"./{match['name']}"
            except Exception:
                pass

        output_path = SITE_DIR / page_data['name']
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    print(f"\n🎉 Process Complete!")
    print(f"📁 Mirror Location: {SITE_DIR}")

if __name__ == "__main__":
    asyncio.run(run_mirror())