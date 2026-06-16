from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import re

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
            browser = playwright.chromium.launch(headless=False)
            context = browser

            page = context.new_page()

            try:
                page.goto(url)
                print(page.title())
                return
            except:
                print("Your url was not valid.")
                return
