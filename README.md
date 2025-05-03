
# Python Web Crawler with MySQL Integration

This project is a **Python-based web crawler** that scrapes webpages, extracts metadata, headings, hyperlinks, image URLs, and the main content from a given starting URL. It stores structured data in a **MySQL database** and saves main page content as text files.

---

## Features

- Recursively crawls internal links up to a specified depth.
- Extracts:
  - Page Title
  - Meta Description and Keywords
  - Headings (H1 to H6)
  - Image URLs
  - Hyperlinks
  - Main text content
- Saves content into text files under the `page_contents/` folder.
- Stores all extracted data into a MySQL database.
- Avoids re-crawling visited URLs.

---

## Install Dependencies
-pip install requests beautifulsoup4 mysql-connector-python

---

## MySQL Setup
CREATE DATABASE webcrawler;

USE webcrawler;

CREATE TABLE pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url TEXT,
    title VARCHAR(255),
    description TEXT,
    keywords TEXT,
    headings JSON,
    main_content_filename VARCHAR(255),
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE page_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_id INT,
    link TEXT,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

CREATE TABLE page_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_id INT,
    image_url TEXT,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

## Update Database Credentials
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YourPassword",
    database="webcrawler"
)



