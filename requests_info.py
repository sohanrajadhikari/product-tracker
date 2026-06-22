import requests
import time
import json
import hashlib
from datetime import datetime

def get_daraz_product_data(product_uri):
    url = "https://acs-m.daraz.com.np/h5/mtop.global.detail.web.getdetailinfo/1.0/"
    
    user_agent = "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.daraz.com.np/"
    }
    
    session = requests.Session()
    app_key = "24937400"
    
    # --- STEP 1: Dummy Request to initialize session tokens ---
    temp_payload = {
        "deviceType": "android",
        "path": f"https://www.daraz.com.np/products/{product_uri}.html",
        "uri": product_uri,
        "headerParams": json.dumps({"user-agent": user_agent}),
        "cookieParams": "{}", 
        "requestParams": "{}"
    }
    
    initial_params = {
        "appKey": app_key,
        "api": "mtop.global.detail.web.getDetailInfo",
        "v": "1.0",
        "type": "originaljson",
        "t": str(int(time.time() * 1000)),
        "data": json.dumps(temp_payload)
    }
    
    session.post(url, headers=headers, params=initial_params)
    
    h5_tk = session.cookies.get("_m_h5_tk", domain=".daraz.com.np")
    h5_tk_enc = session.cookies.get("_m_h5_tk_enc", domain=".daraz.com.np")
    
    if not h5_tk:
        print("[-] Error: Could not fetch fallback validation tokens from Daraz.")
        return None
        
    token = h5_tk.split("_")[0]
    
    # --- STEP 2: Package context into data schema strings ---
    cookie_params_dict = {
        "_m_h5_tk": h5_tk,
        "_m_h5_tk_enc": h5_tk_enc,
        "pdp_login": "false"
    }
    
    final_payload_data = {
        "deviceType": "android",
        "path": f"https://www.daraz.com.np/products/{product_uri}.html",
        "uri": product_uri,
        "headerParams": json.dumps({"user-agent": user_agent}),
        "cookieParams": json.dumps(cookie_params_dict),
        "requestParams": "{}"
    }
    data_str = json.dumps(final_payload_data)
    
    # --- STEP 3: Cryptographic Signature calculation ---
    timestamp = str(int(time.time() * 1000))
    sign_string = f"{token}&{timestamp}&{app_key}&{data_str}"
    sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    
    # --- STEP 4: Fetch authorized raw response payload ---
    final_params = {
        "appKey": app_key,
        "api": "mtop.global.detail.web.getDetailInfo",
        "v": "1.0",
        "type": "originaljson",
        "t": timestamp,
        "sign": sign,
        "data": data_str
    }
    
    response = session.post(url, headers=headers, params=final_params)
    res_json = response.json()
    
    # Check if the gateway request was successful
    ret_message = res_json.get('ret', [''])[0]
    if "SUCCESS" not in ret_message:
        print(f"[-] Gateway rejection or API Error: {ret_message}")
        return None

    # --- STEP 5: Extract fields into your target dictionary format ---
    try:
        module_str = res_json.get('data', {}).get('module', '{}')
        module_data = json.loads(module_str)
        
        default_sku = module_data.get('primaryKey', {}).get('defaultSkuId', '0')
        sku_info = module_data.get('skuInfos', {}).get(default_sku, {})
        
        extracted_data = {
            "title": module_data.get('product', {}).get('title', ''),
            "price": sku_info.get('price', {}).get('salePrice', {}).get('text', ''),
            "original_price": sku_info.get('price', {}).get('originalPrice', {}).get('text', ''),
            "discount_percent": sku_info.get('price', {}).get('discount', ''),
            "rating": module_data.get('product', {}).get('rating', {}).get('score', ''),
            "review_count": module_data.get('review', {}).get('ratings', {}).get('reviewCount', 0),
            "seller_name": module_data.get('tracking', {}).get('seller_name', ''),
            "availability": sku_info.get('quantity', {}).get('text', ''),
            "category": " > ".join(module_data.get('tracking', {}).get('pdt_category', [])),
            "brand": module_data.get('product', {}).get('brand', {}).get('name', ''),
            "url": module_data.get('product', {}).get('link', ''),
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return extracted_data
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[-] Data parsing exception: {e}")
        return None

# --- RUN / VERIFY THE PIPELINE ---
if __name__ == "__main__":
    product_slug = "brazil-fifa-world-cup-jersey-classic-yellow-football-fan-kit-a-grade-fabric-i1519540544-s12348686695"
    
    print(f"[+] Requesting data for product URI: {product_slug}...")
    product_dict = get_daraz_product_data(product_slug)
    
    if product_dict:
        print("\n[+] Extraction Complete! Target Dictionary:\n")
        print(json.dumps(product_dict, indent=4))