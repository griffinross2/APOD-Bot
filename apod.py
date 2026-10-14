import re
import traceback

import requests
from datetime import datetime, timedelta

def reformat_explanation(explanation):
    # Adapted from https://gist.github.com/hqnna/e3c2e5e42eafe55d84e2ecc042b7f984 using Claude

    substitutions = [
        (r'<br\s*/?>', ''),
        (r'</p>', ''),
        (r'</div>', ''),
        (r'</li>', ''),
        (r'<li>', '- '),
        (r'<ul[^>]*>', ''),
        (r'</ul>', ''),
        (r'<ol[^>]*>', ''),
        (r'</ol>', ''),
        (r'<h([1-6])[^>]*>(.*?)</h\1>', r'\n**\2**'),
        (r'<strong>(.*?)</strong>', r'**\1**'),
        (r'<b>(.*?)</b>', r'**\1**'),
        (r'<em>(.*?)</em>', r'*\1*'),
        (r'<i>(.*?)</i>', r'*\1*'),
        (r'<u>(.*?)</u>', r'__\1__'),
        (r'<code>(.*?)</code>', r'`\1`'),
        (r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)'),
    ]

    explanation_formatted = explanation
    for pattern, replacement in substitutions:
        explanation_formatted = re.sub(pattern, replacement, explanation_formatted, flags=re.I)

    # <pre> blocks can span multiple lines
    explanation_formatted = re.sub(r'<pre>(.*?)</pre>', r'```\1```', explanation_formatted, flags=re.I | re.S)

    # Strip any remaining tags
    explanation_formatted = re.sub(r'<[^>]+>', '', explanation_formatted)

    # Decode HTML entities (&amp; last so it doesn't create new entities)
    for entity, char in [('&nbsp;', ' '), ('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&quot;', '"'), ('&#39;', "'")]:
        explanation_formatted = explanation_formatted.replace(entity, char)

    return explanation_formatted.strip()

def apod_api_req(api_key, date=None):
    url = "https://science.nasa.gov/wp-json/wp/v2/apod-basic/"
    
    # Add date
    if date is not None:
        date_str = date.strftime('%y%m%d')
        url += date_str

    # API key
        if type(api_key) is not str or len(api_key) == 0:
            raise ValueError("Invalid API key")
        else:
            url += f"?api_key={api_key}"

    # Make request
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching APOD: {e}")

        return None

    respjson = response.json()

    # If the request is a list, pick the first element (latest)
    if type(respjson) is list and len(respjson) > 0:
        respjson = respjson[0]
    elif type(respjson) is list:
        raise ValueError("APOD API returned an empty list")

    title = '[Missing title]'
    link = '[Missing link]'
    explanation = '[Missing explanation]'
    hdurl = None

    if 'title' in respjson.keys():
        title = respjson['title']

    if 'permalink' in respjson.keys():
        link = respjson['permalink']
    elif 'url' in respjson.keys():
        link = respjson['url']

    if 'explanation' in respjson.keys():
        explanation = reformat_explanation(respjson['explanation'])
        if len(explanation) > 2000:
            explanation = explanation[:1997] + "..."

    if 'hdurl' in respjson.keys():
        hdurl = respjson['hdurl']

    return {
        'title': title,
        'explanation': explanation,
        'link': link,
        'hdurl': hdurl
    }
