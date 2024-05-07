
# import time
import re
# import os
import json
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options as FirefoxOptions

# WEB_DRIVER_LOCATION = "./geckodriver"
# current_dir = os.getcwd()
#
# overstock1 = os.path.join(current_dir, "overstock.com/jewelry01.html")
# overstock2 = os.path.join(current_dir, "overstock.com/jewelry02.html")
#
# rtv1 = os.path.join(current_dir, "rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html")
# rtv2 = os.path.join(current_dir, "rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html")
#
# urls = [rtv1, rtv2, overstock1, overstock2]
# htmls = []
#
# firefox_options = FirefoxOptions()
# firefox_options.add_argument("user-agent=fri-ieps-TEST")
#
# driver = webdriver.Firefox(executable_path=WEB_DRIVER_LOCATION, options=firefox_options)
#
# for url in urls:
#     driver.get("file://" + url)
#     htmls.append(driver.page_source)
#
# driver.close()
#print(html)


def regex_into_json(regex, text, data, keys):
    regex = re.compile(regex)
    match = regex.findall(text)
    if match is not None and match != []:
        i = 0
        for k in keys:
            if type(match[0]) is tuple:
                data["page"][k] = match[0][i]
            else:
                data["page"][k] = match[0]
            i += 1


# overstock
def regex_into_json1(regex, text, keys, data):
    regex = re.compile(regex)
    match = regex.findall(text)
    if match is not None and match != []:
        i = 0
        for m in match:
            m = m[1:]
            j = 0
            data[f"page{i+1}"] = {}
            for k in keys:
                if type(m) is tuple:
                    data[f"page{i+1}"][k] = m[j].replace("\n", " ")
                else:
                    data[f"page{i+1}"][k] = m
                j += 1
            i += 1
        return data


def regex_rtvslo(htmls):
    for i in range(2):
        data = {"page": {}}
        html = htmls[i]
        regex_into_json('''class="author-timestamp">[.\s]*<strong>([\w\s]+)<\/strong>\| ([\w\d\.: ]+)\t''',
                        html, data, ["Author", "PublishedTime"])
        regex_into_json('''<h1>(.*)<\/''',
                        html, data, ["Title"])
        regex_into_json('''class="subtitle">(.*)<\/''',
                        html, data, ["SubTitle"])
        regex_into_json('''class="lead">(.*)<\/''',
                        html, data, ["Lead"])
        regex_into_json('''<p class="Body"><\/p><p class="Body">(.*)\n''',
                        html, data, ["Content"])
        #TODO content

        print(json.dumps(data, indent=4))

        # with open(f"rtv{i+1}.json", "w") as outfile:
        #     outfile.write(json.dumps(data, indent=4))


def regex_overstock(htmls):
    for i in range(2):
        html = htmls[i]
        data = {}
        data = regex_into_json1('''href="http://www.overstock.com/cgi-bin/d2.cgi\?PAGE=PROFRAME&amp;PROD_ID=(\d*)"><b>(.*)</b>[\s\S]*(\$.*)</s>[\s\S]*(\$.*)</b>[\s\S]*(\$.*) (\(.*\))</span>[\s\S]*"normal">([\s\S]*)<br><a href="http://www.overstock.com/cgi-bin/d2.cgi\?PAGE=PROFRAME&amp;PROD_ID=\\1"''', html, ["Title", "ListPrice", "Price", "Saving", "SavingPercent", "Content"], data)

        print(json.dumps(data, indent=4))

        # with open(f"overstock{i+1}.json", "w") as outfile:
        #     outfile.write(json.dumps(data, indent=4))
