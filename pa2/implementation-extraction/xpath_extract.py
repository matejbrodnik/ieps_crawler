from lxml import html
import json

OVERSTOCK_PREFIX = '//table/tbody/tr/td'

def extract_rtvslo():
    pass

def extract_overstock(htmlstr):
    # Parsing the page
    tree = html.fromstring(htmlstr)

    # Get element using XPath
    titles = tree.xpath(f'{OVERSTOCK_PREFIX}/a/b/text()')
    list_prices = tree.xpath(f'{OVERSTOCK_PREFIX}/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s/text()')
    prices = tree.xpath(f'{OVERSTOCK_PREFIX}/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b/text()')
    savings_common = tree.xpath(f'{OVERSTOCK_PREFIX}/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text()')

    savings, savings_pct = [], []
    for s in savings_common:
        s_split = s.split(' ')
        savings.append(s_split[0])
        savings_pct.append(s_split[1])

    content = tree.xpath(f'{OVERSTOCK_PREFIX}/table/tbody/tr/td[2]/span[@class="normal"]/text()')

    data = {}
    for i in range(len(content)):
        data[f"page{i + 1}"] = {}
        data[f"page{i + 1}"]["Title"] = titles[i]
        data[f"page{i + 1}"]["ListPrice"] = list_prices[i]
        data[f"page{i + 1}"]["Price"] = prices[i]
        data[f"page{i + 1}"]["Saving"] = savings[i]
        data[f"page{i + 1}"]["SavingPercent"] = savings_pct[i]
        data[f"page{i + 1}"]["Content"] = content[i]

    print(json.dumps(data, indent=4))

    return data