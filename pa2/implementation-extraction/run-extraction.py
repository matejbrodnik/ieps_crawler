import argparse
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service

import regex
import xpath_extract
import roadrunner

WEB_DRIVER_LOCATION = "./geckodriver"
current_dir = os.getcwd()

INPUT_DIR = "../input-extraction"

overstock1 = os.path.join(current_dir, f"{INPUT_DIR}/overstock.com/jewelry01.html")
overstock2 = os.path.join(current_dir, f"{INPUT_DIR}/overstock.com/jewelry02.html")

rtv1 = os.path.join(current_dir, f"{INPUT_DIR}/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html")
rtv2 = os.path.join(current_dir, f"{INPUT_DIR}/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html")

emka1 = os.path.join(current_dir, f"{INPUT_DIR}/emka.si/Iskanje_ najdeni rezultati (11) za »alamut«.html")
emka2 = os.path.join(current_dir, f"{INPUT_DIR}/emka.si/Iskanje_ najdeni rezultati (18) za »harry potter in«.html")

urls = [rtv1, rtv2, overstock1, overstock2, emka1, emka2]
htmls = []

firefox_options = FirefoxOptions()
firefox_options.add_argument("user-agent=fri-ieps-TEST")

service = Service(executable_path=WEB_DRIVER_LOCATION)
driver = webdriver.Firefox(service=service, options=firefox_options)

# driver.get("file://" + overstock1)
# with open(f"overstock.html", "w") as outfile:
#     outfile.write(driver.page_source)

for url in urls:
    driver.get("file://" + url)
    htmls.append(driver.page_source)

driver.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('extr_type', type=str,
                        help='A required string argument specifying the website type to be extracted')

    args = parser.parse_args()
    extr_type = args.extr_type

    if extr_type == "A":
        # using regular expressions
        regex.regex_rtvslo(htmls[0])
        regex.regex_rtvslo(htmls[1])
        regex.regex_overstock(htmls[2])
        regex.regex_overstock(htmls[3])
        regex.extract_emka(htmls[4])
        regex.extract_emka(htmls[5])
    elif extr_type == "B":
        # using xpath
        xpath_extract.extract_rtvslo(htmls[0])
        xpath_extract.extract_rtvslo(htmls[1])
        xpath_extract.extract_overstock(htmls[2])
        xpath_extract.extract_overstock(htmls[3])
        xpath_extract.extract_emka(htmls[4])
        xpath_extract.extract_emka(htmls[5])
    elif extr_type == "C":
        # using roadRunner algorithm
        roadrunner.get_wrapper(htmls[0], htmls[1])
        roadrunner.get_wrapper(htmls[2], htmls[3])
        roadrunner.get_wrapper(htmls[4], htmls[5])
