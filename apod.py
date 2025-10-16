import requests
from datetime import datetime, timedelta

def fetch_apod_url(url: str = ""):
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve {url}: {response.status_code}")
        return None
    
    # Extract the image URL from the HTML content
    img_start = response.text.lower().find('<img src="')
    if img_start == -1:
        print(f"No image found at {url}")
        return None
    img_end = response.text.find('"', img_start + 10)
    if img_end == -1:
        print(f"Malformed image tag at {url}")
        return None
    img_src = response.text[img_start + 10:img_end]
    img_url = f"https://apod.nasa.gov/apod/{img_src}"

    # Extract the image title from the HTML content (next bold tag after the image)
    title_start = response.text.lower().find('<b>', img_end)
    title_end = response.text.lower().find('</b>', title_start)
    title = response.text[title_start + 3:title_end].strip() if title_start != -1 and title_end != -1 else "Astronomy Picture of the Day"

    print(f"Fetched APOD {url}: {img_url}")
    return title, img_url

def fetch_apod_date(date: datetime = datetime.now()):
    date_str = date.strftime('%y%m%d') if date else datetime.now().strftime('%y%m%d')
    url = f"https://apod.nasa.gov/apod/ap{date_str}.html"
    return fetch_apod_url(url)