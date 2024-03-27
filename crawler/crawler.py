import requests
import urllib
import urllib.robotparser
import concurrent.futures
import threading
import psycopg2
import time
import hashlib
import socket
from datetime import datetime
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup

WEB_DRIVER_LOCATION = "./geckodriver"
TIMEOUT = 5
page_types = ('HTML', 'BINARY', 'DUPLICATE', 'FRONTIER')
data_types = ('pdf', 'doc', 'docx', 'ppt', 'pptx')


def calculate_hash(data):
    hash_object = hashlib.sha256()
    hash_object.update(data.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    return hash_hex


def canonicalize(url):
    try:
        url = urlparse(url)
        scheme = url.scheme.lower()
        if scheme == 'https':
            scheme = 'http'
        # host = url.netloc.lower() # .netloc poda tudi port
        host = url.hostname.lower()
        path = url.path
        params = url.params.lower()
        query = url.query.lower()
        if params != "":
            paramsList = params.split(';')
            paramsList.sort()
            params = ""
            for p in paramsList:
                params += ";" + p
        if query != "":
            queryList = query.split('&')
            queryList.sort()
            query = "?"
            first = True
            for q in queryList:
                if first:
                    query += q
                    first = False
                else:
                    query += "&" + q
        return f"{scheme}://{host}{path}{params}{query}"
    except:
        return "http://www.gov.si/"


frontier = ["http://www.gov.si/", "http://evem.gov.si/", "http://e-uprava.gov.si/", "http://e-prostor.gov.si/"]
link_history = []
current_hosts = set()
images = []
firefox_options = FirefoxOptions()
firefox_options.add_argument("user-agent=fri-ieps-TEST")
firefox_options.add_argument("--headless")


def check_robots_file(hostname):
    robots_txt_url = f"http://{hostname}/robots.txt"

    response = requests.head(robots_txt_url)
    if response.status_code == 200:
        return response.text
    else:
        return None


def get_sitemap_content(sitemap_url):
    if sitemap_url is None:
        return


def map_page_type(content_type, url, hash_code):
    # page_types = ('HTML', 'BINARY', 'DUPLICATE', 'FRONTIER')
    if exists_same_page(hash_code):
        return 'DUPLICATE'
    if url in frontier:
        return 'FRONTIER'
    if 'html' in content_type:
        return 'HTML'
    for data_type in data_types:
        if data_type in content_type:
            return 'BINARY'
    return None


def crawl_page(n, thread):
    for _ in range(n):
        driver = webdriver.Firefox(executable_path=WEB_DRIVER_LOCATION, options=firefox_options)
        host = ""
        hostname = ""
        url = ""
        with lock:
            if len(frontier) > 0:
                for i in range(len(frontier)):  # iščemo stran na IP-ju, ki še ni zaseden
                    url = frontier[i]
                    if url in link_history:
                        continue
                    try:
                        hostname = urlparse(url).hostname
                        host = socket.gethostbyname(hostname)
                        if host not in current_hosts:
                            current_hosts.add(host)
                            frontier.pop(i)
                            break
                        print("Server on " + url + " busy (" + host + ")")
                    except:
                        print("Wrong URL format")
                        continue
                link_history.append(url)

                robots_url = f"http://{hostname}/robots.txt"
                rp = urllib.robotparser.RobotFileParser()

                site_id = get_site_id(hostname)
                # check if the site exists in the DB
                robots_content = check_robots_file(hostname)
                robots_exist = robots_content is not None

                if robots_exist:
                    rp.set_url(robots_url)

                # if the site is not the DB get sitemaps
                if site_id is None and robots_exist:
                    sitemap_url = rp.site_maps()
                    # TODO implement sitemap content retrieval
                    # sitemap_content = get_sitemap_content(sitemap_url)
                    sitemap_content = None
                    site_id = insert_new_site(hostname, robots_content, sitemap_content)

                if robots_exist and rp.can_fetch("*", url) or not robots_exist:
                    print(f"Retrieving web page URL '{url}' ({host}) - thread {thread}")
                    driver.get(url)
                else:
                    print(f"Not allowed to retrieve web page URL '{url}' ({host}) - thread {thread}")
                    continue

            else:
                print(f'----------------empty frontier---------------- thread {thread}')
                continue

        time.sleep(TIMEOUT)
        current_hosts.remove(host)

        html = driver.page_source

        # get information obout the page
        response = requests.head(url)
        status_code = response.status_code
        hash_code = calculate_hash(html)
        content_type = map_page_type(response.headers.get('content-type'), url, hash_code)

        # save the new page into the DB
        if content_type != 'BINARY':
            insert_page(site_id, content_type, url, html, status_code, datetime.now())
        else:
            insert_page(site_id, content_type, url, None, status_code, datetime.now())

        driver.close()

        soup = BeautifulSoup(html)
        with lock:
            for link in soup.find_all('a'):
                link = link.get('href')
                if link is not None:
                    if link.startswith('/'):  # stran znotraj domene
                        link = canonicalize("http://" + hostname + link)
                        if link not in frontier:
                            frontier.append(link)
                    elif link.startswith('http'):  # stran izven domene
                        link = canonicalize(link)
                        if 'gov.si' in link and link not in frontier:
                            frontier.append(link)
            for img in soup.find_all('img'):
                img = img.get('src')
                if img is not None:
                    img = url + img
                    if img not in images:
                        images.append(img);
    if thread == 0:
        print("\nLink history: ")
        for l in link_history:
            print(l)
        print("\nFrontier: ")
        for l in frontier:
            print(l)
        print("\nImages: ")
        for img in images:
            print(img)


lock = threading.Lock()
database_port = 5431


def insert_new_site(domain, robots_content, sitemap_content):
    conn = psycopg2.connect(host="localhost", port=database_port, user="user", password="SecretPassword")
    conn.autocommit = True

    with lock:
        cur = conn.cursor()
        cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES(%s, %s, %s)",
                    (domain, robots_content, sitemap_content))
        row = cur.fetchone()
        result = row[0] if row is not None else None

        cur.close()
    conn.close()
    return result


def get_site_id(domain):
    conn = psycopg2.connect(host="localhost", port=database_port, user="user", password="SecretPassword")
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT id FROM crawldb.site WHERE domain = %s", domain)

    row = cur.fetchone()
    result = row[0] if row is not None else None

    cur.close()
    conn.close()
    return result


def insert_page(site_id, page_type_code, url, html_content, https_status_code, hash_code, accessed_time):
    conn = psycopg2.connect(host="localhost", port=database_port, user="user", password="SecretPassword")
    conn.autocommit = True

    # If a page is of type HTML, its content should be stored as a value within html_content attribute,
    # otherwise (if crawler detects a binary file - e.g. .doc), html_content is set to NULL
    # and a record in the page_data table is created
    ###
    # The duplicate page should not have set the html_content value and should be linked to a duplicate version of a page.
    if page_type_code not in page_types:
        return
    with lock:
        cur = conn.cursor()
        cur.execute("INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, https_status_code, hash_code, accessed_time) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            (site_id, page_type_code, url, html_content, https_status_code, hash_code, accessed_time))
        cur.close()
    conn.close()

def insert_image(page_id, filename, content_type, data, accessed_time):
    conn = psycopg2.connect(host="localhost", port=database_port, user="user", password="SecretPassword")
    conn.autocommit = True

    # there is no need to populate data field
    with lock:
        cur = conn.cursor()
        if data is not None:
            cur.execute(
                "INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) VALUES(%s, %s, %s, %s, %s)",
                (page_id, filename, content_type, data, accessed_time))
        else:
            cur.execute(
                "INSERT INTO crawldb.image (page_id, filename, content_type, accessed_time) VALUES(%s, %s, %s, %s)",
                (page_id, filename, content_type, accessed_time))
        cur.close()
    conn.close()


def insert_link(from_page, to_page):
    conn = psycopg2.connect(host="localhost", port=database_port, user="user", password="SecretPassword")
    conn.autocommit = True

    with lock:
        cur = conn.cursor()
        cur.execute("INSERT INTO crawldb.link (from_page, to_page)) VALUES(%s, %s)",
                    (from_page, to_page))
        cur.close()
    conn.close()


def insert_page_data(page_id, data_type_code, data):
    conn = psycopg2.connect(host="localhost", port=database_port, user="user", password="SecretPassword")
    conn.autocommit = True

    # List all other content (.pdf, .doc, .docx, .ppt and .pptx) in the page_data table - there is no need to populate data field
    with lock:
        cur = conn.cursor()
        if data is not None:
            cur.execute("INSERT INTO crawldb.page_data (page_id, data_type_code, data)) VALUES(%s, %s, %s)",
                        (page_id, data_type_code, data))
        else:
            cur.execute("INSERT INTO crawldb.page_data (page_id, data_type_code)) VALUES(%s, %s)",
                        (page_id, data_type_code))
        cur.close()
    conn.close()


def exists_same_page(hash_code):
    conn = psycopg2.connect(host="localhost", port=database_port, user="user", password="SecretPassword")
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT id FROM crawldb.page WHERE hash_code = %s", hash_code)

    row = cur.fetchone()
    result = True if row is not None else False

    cur.close()
    conn.close()
    return result


def para(num_workers, pages_per_thread):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        print(f"\n ... executing workers ...\n")
        for i in range(num_workers):
            executor.submit(crawl_page, pages_per_thread, i)


pages = 25
workers = 5
pages_per_worker = pages // workers

print(f"Crawling {pages_per_worker * workers} pages with {workers} workers")
para(workers, pages_per_worker)
# crawl_page(10,0)

