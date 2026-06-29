from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import re
from bs4 import BeautifulSoup
import time
from requests_info import get_daraz_product_data
from datetime import datetime
import json

def clean_daraz_url(url: str) -> str:
    match = re.match(
        r"^(https://www\.daraz\.com\.np/products/.*?\.html)",
        url
    )

    if not match:
        raise ValueError("Invalid Daraz product URL")
    return match.group(1)


def fetch_item(url, page):
    try:
        page.goto(url, wait_until="networkidle", timeout=50000)

        while page.locator("div.count").count() == 0:
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(500)


        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        title = soup.find("h1", class_="pdp-mod-product-badge-title").get_text(strip=True)
        
        string_price = soup.find("span", class_="pdp-price_type_normal").get_text()
        match = re.search(r'[\d,]+', string_price)
        price = int(match.group().replace(',', '')) if match else None

        rating = soup.find("span", class_="score-average").get_text()

        count = soup.find("div", class_="count").get_text()
        match = re.search(r"\d+", count)
        reviews_count = match.group() if match else None

        return {
            "title": title,
            "price": price,
            "original_price": "N/A", 
            "discount_percent": "N/A",
            "rating": rating,
            "review_count": reviews_count,
            "seller_name": "N/A",
            "availability": "In Stock",
            "category": "N/A",
            "brand": "N/A",
            "url": url,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Error : {e}")
        return None





def track_new():
    url = input("Enter the url of the product you wnat to track: ")
    try:
        url = clean_daraz_url(url)
        slug = url.split("/products/")[1].split(".html")[0]
    except Exception as e:
        print(f"[-] Error parsing URL: {e}")
  

    
    print("[+] Attempting API fetch...")
    product_dict = get_daraz_product_data(slug)


    if not product_dict:
        print("[-] API rejected or failed. Trying fallback Playwright method...")
        try:
            with Stealth().use_sync(sync_playwright()) as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                product_dict = fetch_item(url, page)
                browser.close()
        except Exception as e:
            print(f"[-] Playwright Critical Failure: {e}")
        
    if product_dict:
        print("\n[+] Successfully gathered product details!")
        print(json.dumps(product_dict, indent=4))
        return product_dict  # Ready for database inclusion!
    else:
        print("[-] Error: Could not fetch data via API or Browser Fallback. Check the link or network.")
        return None
                