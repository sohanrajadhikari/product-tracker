from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import re
from bs4 import BeautifulSoup

def clean_daraz_url(url: str) -> str:
    match = re.match(
        r"^(https://www\.daraz\.com\.np/products/.*?\.html)",
        url
    )

    if not match:
        raise ValueError("Invalid Daraz product URL")
    return match.group(1)


def track_new():
    url = input("Enter the url of the product you wnat to track: ")
    try:
        url = clean_daraz_url(url)
    except Exception as e:
        print(f"Error : {e}")
    else:
        with Stealth().use_sync(sync_playwright()) as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser

            page = context.new_page()

            try:
                page.goto(url, wait_until="networkidle")

                html = page.content()

                soup = BeautifulSoup(html, 'html.parser')
                
                title = soup.find("h1", class_="pdp-mod-product-badge-title").get_text(strip=True)
                
                string_price = soup.find("span", class_="pdp-price_type_normal").get_text(strip=True)
                match = re.search(r'(\d+)', string_price)
                price = int(match.group(1)) if match else None


                print(title, price)
                return
            except Exception as e:
                print(f"Error : {e}")
                return
