import os
import requests
import mysql.connector
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import json

# Set to avoid re-crawling
visited = set()

# Folder to store main content text files
content_folder = "page_contents"
os.makedirs(content_folder, exist_ok=True)

# MySQL connection setup
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Anasaslam",
    database="webcrawler"
)
cursor = conn.cursor()

# Utility to clean and format text
def clean_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

# Utility to generate a safe filename from URL
def safe_filename(url):
    path = urlparse(url).path
    filename = path.strip("/").replace("/", "_")
    return filename if filename else "index"

# Crawl function
def crawl(url, depth=1):
    if depth == 0 or url in visited:
        return
    visited.add(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Metadata
    title = soup.title.string.strip() if soup.title else 'No Title'
    description_tag = soup.find("meta", attrs={"name": "description"})
    keywords_tag = soup.find("meta", attrs={"name": "keywords"})
    description = description_tag["content"] if description_tag and "content" in description_tag.attrs else "N/A"
    keywords = keywords_tag["content"] if keywords_tag and "content" in keywords_tag.attrs else "N/A"

    # Headings
    headings = []
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        for heading in soup.find_all(tag):
            headings.append(f"{tag.upper()}: {heading.get_text(strip=True)}")

    # Main content
    main_content = clean_text(soup.get_text(separator="\n"))
    filename = safe_filename(url) + ".txt"
    filepath = os.path.join(content_folder, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(main_content)

    # Image URLs
    image_urls = [urljoin(url, img['src']) for img in soup.find_all("img", src=True)]

    # Hyperlinks
    links = [urljoin(url, a['href']) for a in soup.find_all("a", href=True)]

    # Insert page data into MySQL
    insert_page = """
        INSERT INTO pages (url, title, description, keywords, headings, main_content_filename)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_page, (url, title, description, keywords, json.dumps(headings), filename))
    page_id = cursor.lastrowid

    # Insert links
    insert_link = "INSERT INTO page_links (page_id, link) VALUES (%s, %s)"
    for link in links:
        cursor.execute(insert_link, (page_id, link))

    # Insert image URLs
    insert_image = "INSERT INTO page_images (page_id, image_url) VALUES (%s, %s)"
    for img_url in image_urls:
        cursor.execute(insert_image, (page_id, img_url))

    conn.commit()

    # Crawl internal links
    for link in links:
        if urlparse(link).netloc == urlparse(url).netloc:
            crawl(link, depth - 1)


start_url = "https://webscraper.io/test-sites/e-commerce/static"
crawl(start_url, depth=1)


cursor.close()
conn.close()

print(f"\n✅ Crawling complete. Data stored in MySQL, content saved in '{content_folder}/'")
