from lxml import html
import json

OVERSTOCK_PREFIX = '//table/tbody/tr/td[5]/table/tbody/tr[2]/td//table/tbody/tr/td/table/tbody/tr/td[2]'


def extract_rtvslo(htmls):
    tree = html.fromstring(htmls)

    title = tree.xpath('//header[@class="article-header"]/h1/text()')
    sub_title = tree.xpath('//header[@class="article-header"]/div[@class="subtitle"]/text()')
    author = tree.xpath('//div[@class="author"]/div[@class="author-name"]/text()')
    published_time = [tree.xpath('//div[@class="publish-meta"]/text()')[0].strip().split('\n\t')[0]]
    lead = tree.xpath('//header[@class="article-header"]/p[@class="lead"]/text()')
    content_arr = tree.xpath('//div[@class="article-body"]/article/p/text()')

    content = ''
    for c in content_arr:
        content += c
        content += '\n'

    data = {"page": {}}
    data["page"]["Title"] = title[0]
    data["page"]["SubTitle"] = sub_title[0]
    data["page"]["Author"] = author[0]
    data["page"]["PublishedTime"] = published_time[0]
    data["page"]["Lead"] = lead[0]
    data["page"]["Content"] = content

    print(json.dumps(data, indent=4))


def extract_overstock(htmls):
    # Parsing the page
    tree = html.fromstring(htmls)

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


def extract_emka(htmls):
    tree = html.fromstring(htmls)

    titles_d = tree.xpath('//div/div[contains(@class, "GO-Results-Naziv ")]/span/text()')[1:]

    titles = []
    for t in titles_d:
        titles.append(t.strip())
    titles = tree.xpath('//a[contains(@class, "ie-book-title")]/text()')
    author = tree.xpath('//div[@class="book-item-information tw-relative"]/a[2]/text()')
    binding = tree.xpath('//div[@class="book-item-information tw-relative"]/div[3]/text()')
    price = tree.xpath('//div[@class="book-item-buy"]/div/div/span/text()')

    authors = []
    bindings = []
    for a in author:
        authors.append(a.strip())
    for b in binding:
        bindings.append(b.strip().split(' ')[1])

    data = {}
    for i in range(len(authors)):
        data[f"page{i + 1}"] = {}
        data[f"page{i + 1}"]["Title"] = titles[i]
        data[f"page{i + 1}"]["Author"] = authors[i]
        data[f"page{i + 1}"]["Binding"] = bindings[i]
        data[f"page{i + 1}"]["Price"] = price[i]

    print(json.dumps(data, indent=4))
