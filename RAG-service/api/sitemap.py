import requests
from xml.etree import ElementTree

def get_main_urls():
    return [
        "https://mojastrona.com/dokumentacja1",
        "https://mojastrona.com/dokumentacja2",
        "https://mojastrona.com/dokumentacja3"
    ]


SITEMAP_URL = "https://ai.pydantic.dev/sitemap.xml"

def get_ai_docs_urls():
    """Fetch and parse documentation URLs from sitemap.xml"""
    try:
        response = requests.get(SITEMAP_URL)
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        return [loc.text for loc in root.findall('.//ns:loc', namespace)]
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []
