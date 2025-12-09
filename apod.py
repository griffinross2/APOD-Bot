import requests
from datetime import datetime, timedelta

def fetch_apod_url(url: str = ""):
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve {url}: {response.status_code}")
        return None
    
    def get_image(response):
        # Extract the image URL from the HTML content
        img_start = response.text.lower().find('<img src="')
        if img_start == -1:
            print(f"No image start found at {url}")
            return None, None
        img_end = response.text.find('"', img_start + 10)
        if img_end == -1:
            print(f"Malformed image tag src at {url}")
            return None, None
        img_src = response.text[img_start + 10:img_end]
        img_url = f"https://apod.nasa.gov/apod/{img_src}"
        return img_url, img_end
    
    def get_video(response):
        # Extract the video URL from the HTML content
        vid_start = response.text.lower().find('<iframe')
        if vid_start == -1:
            print(f"No iframe start found at {url}")
            return None, None
        vid_url_start = response.text.find('src="', vid_start + 7)
        if vid_url_start == -1:
            print(f"No iframe src found at {url}")
            return None, None
        vid_end = response.text.find('"', vid_url_start + 5)
        if vid_end == -1:
            print(f"Malformed iframe tag src at {url}")
            return None, None
        vid_src = response.text[vid_url_start + 5:vid_end]
        return vid_src, vid_end

    is_video = False
    content_url, url_end = get_image(response)
    if content_url is None:
        content_url, url_end = get_video(response)
        is_video = True
        if content_url is None:
            return None

    # Extract the image title from the HTML content (next bold tag after the image)
    title_start = response.text.lower().find('<b>', url_end)
    title_end = response.text.lower().find('</b>', title_start)
    title = response.text[title_start + 3:title_end].strip() if title_start != -1 and title_end != -1 else "Astronomy Picture of the Day"

    if url == "https://apod.nasa.gov/":
        date_str = datetime.now().strftime('%y%m%d') if datetime.now() else datetime.now().strftime('%y%m%d')
        url = f"https://apod.nasa.gov/apod/ap{date_str}.html"

    if not is_video:
        response = requests.get(content_url)
        if response.status_code != 200:
            print(f"Failed to retrieve image/video {content_url}: {response.status_code}")
            return None
        print(f"Fetched APOD {url}: {content_url}")

        return False, url, title, response.content
    else:
        return True, url, title, content_url

def fetch_apod_date(date: datetime = datetime.now()):
    date_str = date.strftime('%y%m%d') if date else datetime.now().strftime('%y%m%d')
    url = f"https://apod.nasa.gov/apod/ap{date_str}.html"
    return fetch_apod_url(url)