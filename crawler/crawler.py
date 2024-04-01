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
from urllib.parse import urlparse, quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
from datetime import datetime
from io import StringIO

WEB_DRIVER_LOCATION = "./geckodriver"
page_types = ('HTML', 'BINARY', 'DUPLICATE', 'FRONTIER')
data_types = ('pdf', 'doc', 'docx', 'ppt', 'pptx')
DB_USER = 'user'
DB_PWD = 'SecretPassword'
socket.setdefaulttimeout(10)


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
        return quote(f"{scheme}://{host}{path}{params}{query}", safe=':/?;&=@')
    except:
        return "http://gov.si/"

current_hosts = set() # zasedeni IP-ji
locked_hosts = set() # zasedeni IP-ji posebej za robots
current_pages = set() # trenutno brane strani (da več niti ne dostopa do iste)
empty_iterations = 0
disable_frontier = False
firefox_options = FirefoxOptions()
firefox_options.add_argument("user-agent=fri-wier-Arachnida")
firefox_options.add_argument("--headless")


def find_and_save_images(soup, page_id, page_type):
    for img in soup.find_all('img'):
        img_link = img.get('src')
        if img_link is not None and page_type != 'DUPLICATE':
            img_type = img_link.split('.')[-1]
            if len(img_link) > 255 or len(img_type) > 50:
                continue
            insert_image(page_id, img_link, img_type, None, datetime.now())

def find_and_save_links(soup, site_id, page_id, hostname):
    elements_with_onclick = soup.find_all(lambda tag: tag.has_attr('onclick'))
    for element in elements_with_onclick:
        onclick = element['onclick']
        if 'location.href' in onclick or 'document.location' in onclick:
            url_start_index = onclick.find("'") + 1
            url_end_index = onclick.find("'", url_start_index)
            if url_start_index != -1 and url_end_index != -1:
                url = onclick[url_start_index:url_end_index]
                print("ONCLICK_URL:", url)
                parse_link(link, site_id, page_id, hostname, False)
    for area in soup.find_all('area'):
        link = area.get('href')
        if link is not None:
            print("AREA URL ", link)
        parse_link(link, site_id, page_id, hostname, False)
    for link in soup.find_all('link'):
        link = link.get('href')
        parse_link(link, site_id, page_id, hostname, True)
    for link in soup.find_all('a'):
        link = link.get('href')
        parse_link(link, site_id, page_id, hostname, False)

def parse_link(link, site_id, page_id, hostname, only_http):
    if link is not None:
        if not only_http and link.startswith('/'):  # stran znotraj domene
            if 'gov.si' in hostname:
                link = canonicalize('http://' + hostname + link)
                page_new_id = check_and_insert_page(site_id, link, "FRONTIER")
                try:
                    insert_link(page_id, page_new_id)  # insert link into the database
                except:
                    pass
        elif link.startswith('http'):  # stran izven domene
            link = canonicalize(link)
            hostname = urlparse(link).hostname
            if 'gov.si' in hostname:
                page_new_id = check_and_insert_page(site_id, link, "FRONTIER")
                try:
                    insert_link(page_id, page_new_id)  # insert link into the database
                except:
                    pass
                
def crawl_page(n, thread, drivers, max_pages):
    global disable_frontier
    
    for iteration in range(n):
        #print(f"Begin thread {thread}, iteration {iteration}/{n}")
        driver = drivers[thread]
        host = ""
        hostname = ""
        url = ""
        TIMEOUT = 5
        if iteration == 0:
            robot = None
        # prejšnja iteracija je naletela na novo stran, parsamo robots in sitemap
        if robot is not None:
            hostname = urlparse(robot).hostname
            host = socket.gethostbyname(hostname)
            # čakamo da se IP za robote sprosti, če IP takoj po izhodu iz zanke zasede druga nit, ignoriramo timeout :(
            if host not in locked_hosts:
                print("\nERROR ERROR\nERROR ERROR\nERROR ERROR\nERROR ERROR\nERROR ERROR\nERROR ERROR\n")
            try:
                with urllib.request.urlopen(robot) as response:
                    robot_data = response.read().decode('utf-8')
                    if "User-agent" not in robot_data[:300]: # če robots redirecta na neko drugo stran
                        print(f"Thread {thread}, iter {iteration}/{n} | {robot} is not valid")
                    else: 
                        print(f"Thread {thread}, iter {iteration}/{n} | Parsed {robot} on {host}")
                        rp = urllib.robotparser.RobotFileParser()
                        rp.parse(StringIO(robot_data))
                        sitemaps = rp.site_maps()
                        TIMEOUT = rp.crawl_delay("*")
                        if TIMEOUT is None:
                            TIMEOUT = 5
                        if sitemaps is not None:
                            driver.get(sitemaps[0])
                            update_site(hostname, robot_data, driver.page_source)
                        else:
                            update_site(hostname, robot_data, None)
            except:
                print(f"Thread {thread}, iter {iteration}/{n} | {robot} cannot be reached")
            robot = None
            time.sleep(TIMEOUT)
            with lock:
                if host in locked_hosts:
                    locked_hosts.remove(host)
        else:
            try:
                with lock:
                    frontier = get_frontier()
                    num_pages = get_pages_num()
                    if len(frontier) == 0 and len(current_pages) == 0:
                        return
                    #if len(frontier) + num_pages > max_pages:
                        #disable_frontier = True
                        #print("frontier disabled")
                    can_parse = len(frontier) > len(current_pages)
                if can_parse:
                    with lock:
                        for i in range(len(frontier)):  # iščemo stran na IP-ju, ki še ni zaseden
                            url = frontier[i]
                            if url in current_pages:
                                continue
                            try:
                                hostname = urlparse(url).hostname
                                host = socket.gethostbyname(hostname)
                                if host not in current_hosts and host not in locked_hosts:
                                    TIMEOUT, allowed = check_robots(hostname, url)
                                    #print(allowed)
                                    if allowed is None:
                                        robot = f"http://{hostname}/robots.txt"
                                        print("Scheduling robot parsing on ", hostname)
                                        locked_hosts.add(host)
                                    elif not allowed:
                                        print(f"Thread {thread}, iter {iteration}/{n} | PAGE {url} IS NOT ALLOWED")
                                        update_page_type(url, 403, "HTML")
                                        continue
                                    current_hosts.add(host)
                                    current_pages.add(url)
                                    break
                                #print(f"Server on {url} busy ({host})")
                            except:
                                print(f"Thread {thread}, iter {iteration}/{n} | WRONG URL FORMAT: {url} {host}")
                                update_page_type(url, 404, "HTML")
                                continue
                        else:
                            can_parse = False
                            #empty_iterations += 1
                            iteration -= 1
                            print("CURRENTLY IN FRONTIER: ")
                    try:
                        if can_parse:
                            print(f"Thread {thread}, iter {iteration}/{n} | Retrieving web page URL '{url}' ({host})")
                            driver.get(url)
                    except:
                        print(f"Thread {thread}, iter {iteration}/{n} | Couldn't reach page {url}")
                        update_page_type(url, 404, "HTML")
                        can_parse = False
                else:
                    print(f'Thread {thread}, iter {iteration}/{n} | ------------empty frontier------------')
                    TIMEOUT = 5

                time.sleep(TIMEOUT)
                if not can_parse:
                    print(f"Thread {thread}, iter {iteration}/{n} | No urls to parse, trying again")
                    #driver.close()
                    continue
                with lock:
                    if host in current_hosts:
                        current_hosts.remove(host)
                html = driver.page_source
                #driver.close()
                hash_code = calculate_hash(html)

                content_type = 'HTML' # map_page_type(response.headers.get('content-type'), url, hash_code)
                site_id, page_id, is_duplicate = insert_all(hostname, "NULL", "NULL", url, html, hash_code, thread)

                with lock:
                    if url in current_pages:
                        current_pages.remove(url)
                if is_duplicate:
                    insert_link(page_id, get_duplicate_page_id(page_id, hash_code))
                else:
                    soup = BeautifulSoup(html)
                    if not disable_frontier:
                        find_and_save_links(soup, site_id, page_id, hostname)
                    else:
                        print("frontier disabled")
                    find_and_save_images(soup, page_id, content_type)
            except Exception as error:
                print(f"ERROR INSIDE LOOP: {thread} {error}")

lock = threading.Lock()
database_port = 5431

def insert_all(domain, robots_content, sitemap_content, url, html, hash_code, thread):
    with lock:
        conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
        conn.autocommit = True
    
        cur = conn.cursor()
        cur.execute("SELECT id FROM crawldb.site WHERE domain = %s", (domain,))
        row = cur.fetchone()
        if row is None:
            cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES(%s, %s, %s) RETURNING id",
                        (domain, robots_content, sitemap_content))
            row = cur.fetchone()
        site_id = row[0]
        cur.execute("SELECT id FROM crawldb.page WHERE url = %s", (url,))
        page_id = cur.fetchone()[0]
        content_type = "HTML"
        file_type = url.split('.')[-1].upper()
        
        if exists_same_page(hash_code):
            content_type = 'DUPLICATE'
            #cur.execute("UPDATE * FROM crawldb.link WHERE from_page = %s AND to_page = %s", (from_page, to_page))
        if any(file_type == s for s in ["PDF", "DOC", "DOCX", "PPT", "PPTX"]):
            content_type = 'BINARY'
            html = None
            insert_page_data(page_id, file_type, None)

        cur.execute("UPDATE crawldb.page SET site_id=%s, page_type_code=%s, html_content=%s, http_status_code=%s, hash_code=%s, "
        "accessed_time=%s WHERE id = %s",
        (site_id, content_type, html, 200, hash_code, datetime.now(), page_id))
        #(page_type, html, status_code, hash_code, accessed_time, page_id))

        #cur.execute(
        #"INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, hash_code, "
        #"accessed_time) VALUES(%s, %s, %s, %s, %s, %s, %s)",
        #(site_id, page_type_code, url, html, 0, "NULL", datetime.now()))
        cur.close()
        conn.close()
    return site_id, page_id, content_type == "DUPLICATE"
    
def insert_site(domain, robots_content, sitemap_content):
    with lock:
        conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES(%s, %s, %s)",
                    (domain, robots_content, sitemap_content))

        cur.close()
        conn.close()

def update_site(domain, robots_content, sitemap_content):
    with lock:
        conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("UPDATE crawldb.site SET robots_content=%s, sitemap_content=%s WHERE domain=%s",
                    (robots_content, sitemap_content, domain))

        cur.close()
        conn.close()
    
def update_page_type(url, status, content_type):
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("UPDATE crawldb.page SET page_type_code=%s, http_status_code=%s WHERE url=%s",
                (content_type, status, url))

    cur.close()
    conn.close()
    
def check_robots(domain, url):
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT robots_content FROM crawldb.site WHERE domain=%s",
                (domain,))
    row = cur.fetchone()
    
    cur.close()
    conn.close()
    if row is None:
        return 5, None
    if row[0] is None:
        return 5, True
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(StringIO(row[0]))
    delay = rp.crawl_delay("*")
    if delay is None:
        delay = 5
    return delay, rp.can_fetch("*", url)
    
def check_and_insert_page(site_id, url, page_type):
    with lock:
        conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
        conn.autocommit = True
    
        cur = conn.cursor()
        cur.execute("SELECT id FROM crawldb.page WHERE url = %s", (url,))
        #print("inside")
        row = cur.fetchone()
        if row is None and len(url) < 3000:
            cur.execute(
            "INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, hash_code, "
            "accessed_time) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (site_id, page_type, url, "", 0, "", datetime.now()))
            row = cur.fetchone()
        
        cur.close()
        conn.close()
    return row[0]

def get_duplicate_page_id(page_id, hash_code):
    with lock:
        conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
        conn.autocommit = True
        
        cur = conn.cursor()
        cur.execute("SELECT id FROM crawldb.page WHERE hash_code=%s AND id != %s", (hash_code, page_id))
        row = cur.fetchone()

        # page with this link does not exist yet, insert it into the DB
        result = row[0] if row is not None else None
        cur.close()
        conn.close()
    return result

def exists_same_page(hash_code):
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT id FROM crawldb.page WHERE hash_code = %s", (hash_code,))
    row = cur.fetchone()
    result = True if row is not None else False
    cur.close()
    conn.close()
    return result

def delete_page(url):
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("DELETE FROM crawldb.page WHERE url = %s",
                (url,))

    # page with this link does not exist yet, insert it into the DB
    cur.close()
    conn.close()

def insert_image(page_id, filename, content_type, data, accessed_time):
    with lock:
        conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
        conn.autocommit = True

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
    with lock:
        conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
        conn.autocommit = True

        cur = conn.cursor()
        cur.execute("SELECT * FROM crawldb.link WHERE from_page = %s AND to_page = %s", (from_page, to_page))
        row = cur.fetchone()
        if row is None:
            cur.execute("INSERT INTO crawldb.link (from_page, to_page) VALUES(%s, %s)", (from_page, to_page))
        cur.close()
        conn.close()

def insert_page_data(page_id, data_type_code, data):
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True
    # List all other content (.pdf, .doc, .docx, .ppt and .pptx) in the page_data table - there is no need to populate data field
    cur = conn.cursor()
    if data is not None:
        cur.execute("INSERT INTO crawldb.page_data (page_id, data_type_code, data) VALUES(%s, %s, %s)",
                    (page_id, data_type_code, data))
    else:
        cur.execute("INSERT INTO crawldb.page_data (page_id, data_type_code) VALUES(%s, %s)",
                    (page_id, data_type_code))
    cur.close()
    conn.close()

def get_frontier():
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT url FROM crawldb.page WHERE page_type_code = 'FRONTIER' ORDER BY id")

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return [row[0] for row in rows]

def get_pages():
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.page WHERE NOT page_type_code = 'FRONTIER' ORDER BY id")

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows

def get_pages_num():
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT id FROM crawldb.page WHERE NOT page_type_code = 'FRONTIER' ORDER BY id")

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return len(rows)

def get_sites():
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.site ORDER BY id")

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows

def get_images():
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.image ORDER BY id")

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows

def get_page_data():
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.page_data ORDER BY id")

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows

def get_links():
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT * FROM crawldb.link ORDER BY from_page")

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows

def reset_db():
    conn = psycopg2.connect(host="localhost", port=database_port, user=DB_USER, password=DB_PWD)
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("DROP SCHEMA IF EXISTS crawldb CASCADE")
    with open('init-scripts/crawldb.sql', 'r') as file:
        sql = file.read()
    cur.execute(sql)

    cur.close()
    conn.close()

    
def parallel(num_workers, pages_per_thread, drivers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        print(f"\nExecuting {num_workers} workers for {pages_per_thread} cycles\n")
        for thread_num in range(num_workers):
            executor.submit(crawl_page, pages_per_thread, thread_num, drivers, num_workers * pages_per_thread)

pages = 2000
workers = 5
pages_per_worker = pages // workers

drivers = []
print("Creating drivers...")
for _ in range(workers):
    driver = webdriver.Firefox(executable_path=WEB_DRIVER_LOCATION, options=firefox_options)
    driver.implicitly_wait(15)
    driver.set_page_load_timeout(15)
    drivers.append(driver)

print(datetime.now())

print(f"Crawling {pages_per_worker * workers} pages with {workers} workers")

reset_db()
insert_site("dummy-site-for-seeding-frontier.gov.si", "NULL", "NULL")
check_and_insert_page(1, "http://gov.si/", "FRONTIER")
check_and_insert_page(1, "http://www.e-prostor.gov.si/", "FRONTIER")
check_and_insert_page(1, "http://evem.gov.si/", "FRONTIER")
check_and_insert_page(1, "http://e-uprava.gov.si/", "FRONTIER")
#check_and_insert_page(1, "http://www.e-prostor.gov.si/dostopi/javni-dostop/storitve/?filter=.pf-državna-meja", "FRONTIER")

parallel(workers, pages_per_worker, drivers)
#crawl_page(10,0)

print(datetime.now())

print(f"FRONTIER LENGTH {len(get_frontier())}")
#for i in get_frontier():
    #print(i)
print(f"\nPAGES LENGTH {len(get_pages())}")
for i in get_pages():
    print(i[3])
print(f"\nSITES LENGTH {len(get_sites())}")
print("\nSITES ")
for i in get_sites():
    print(i[1])
print(f"\nPAGE DATA LENGTH {len(get_page_data())}")
print("\nPAGE DATA")
for i in get_page_data():
    print(i)
print(f"\nIMAGES LENGTH {len(get_images())}")
#for i in get_images():
    #print(i)
print(f"\nLINKS LENGTH {len(get_links())}")
#for i in get_links():
    #print(i)