import re
import json


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
    data = {"page": {}}
    regex_into_json('''class="author-timestamp">[.\s]*<strong>([\w\s]+)<\/strong>\| ([\w\d\.: ]+)\t''',
                    htmls, data, ["Author", "PublishedTime"])
    regex_into_json('''<h1>(.*)<\/''',
                    htmls, data, ["Title"])
    regex_into_json('''class="subtitle">(.*)<\/''',
                    htmls, data, ["SubTitle"])
    regex_into_json('''class="lead">(.*)<\/''',
                    htmls, data, ["Lead"])
    regex_into_json('''<p class="Body"><\/p><p class="Body">(.*)\n''',
                    htmls, data, ["Content"])

    print(json.dumps(data, indent=4))

    # with open(f"rtv{i+1}.json", "w") as outfile:
    #     outfile.write(json.dumps(data, indent=4))


def regex_overstock(htmls):
    data = {}
    data = regex_into_json1('''href="http://www.overstock.com/cgi-bin/d2.cgi\?PAGE=PROFRAME&amp;PROD_ID=(\d*)"><b>(.*)</b>[\s\S]*(\$.*)</s>[\s\S]*(\$.*)</b>[\s\S]*(\$.*) (\(.*\))</span>[\s\S]*"normal">([\s\S]*)<br><a href="http://www.overstock.com/cgi-bin/d2.cgi\?PAGE=PROFRAME&amp;PROD_ID=\\1"''', htmls, ["Title", "ListPrice", "Price", "Saving", "SavingPercent", "Content"], data)

    print(json.dumps(data, indent=4))

    # with open(f"overstock{i+1}.json", "w") as outfile:
    #     outfile.write(json.dumps(data, indent=4))


def extract_emka(htmls):
    data = {}

    title_pattern = '''class="ie-book-title[^>]*>(.*?)<span'''
    author_pattern = r'<li class="ie-custom-grid tw-relative".*?<a[^>]*class="tw-text-darkblue tw-text-sm tw-underline"[^>]*>\s*(.*?)\s*</a>'
    binding_pattern = '''<div class="product_var tw-text-darkblue tw-text-sm tw-font-bold">Vezava:\s*(.*?)\s*</div>'''
    price_pattern = r'<li class="ie-custom-grid tw-relative".*?<div class="book-item-buy">\s*<div[^>]*>\s*<div[^>]*>\s*<span[^>]*>(.*?)</span>'
    r = re.compile(title_pattern)
    titles = r.findall(htmls)

    authors = re.findall(author_pattern, htmls, re.DOTALL)

    r = re.compile(binding_pattern)
    bindings = r.findall(htmls, re.DOTALL)

    prices = re.findall(price_pattern, htmls, re.DOTALL)

    for i in range(len(titles)):
        page = f'page{i+1}'
        data[page] = {}
        data[page]["Title"] = titles[i]
        data[page]["Author"] = authors[i]
        data[page]["Binding"] = bindings[i]
        data[page]["Price"] = prices[i]

    print(json.dumps(data, indent=4))
