# Instructions

Implement a web crawler that will crawl only *.gov.si web sites. You can choose a programming language of your choice. The initial seed URLs should be:
- gov.si,
- evem.gov.si,
- e-uprava.gov.si and
- e-prostor.gov.si.

The crawler needs to be implemented with multiple workers that retrieve different web pages in parallel. The number of workers should be a parameter when starting the crawler. The frontier strategy needs to follow the breadth-first strategy. In the report explain how is your strategy implemented.

Check and respect the robots.txt file for each domain if it exists. Correctly respect the commands User-agent, Allow, Disallow, Crawl-delay and Sitemap. Make sure to respect robots.txt as sites that define special crawling rules often contain spider traps. Also make sure that you follow ethics and do not send request to the same server more often than one request in 5 seconds (not only domain but also IP!).

In a database store canonicalized URLs only!

During crawling you need to detect duplicate web pages. The easiest solution is to check whether a web page with the same page content was already parsed (hint: you can extend the database with a hash, otherwise you need compare exact HTML code). If your crawler gets a URL from a frontier that has already been parsed, this is not treated as a duplicate. In such cases there is no need to re-crawl the page, just add a record into to the table link accordingly.

BONUS POINTS (10 points): Deduplication using exact match is not efficient as some minor content can be different but two web pages can still be the same. Implement one of the Locality-sensitive hashing methods to find collisions and then apply Jaccard distance (e.g. using unigrams) to detect a possible duplicate. Also, select parameters for this method. Document your implementation and include an example of duplicate detection in the report. Note, you need to implement the method yourself to get bonus points.
When your crawler fetches and renders a web page, do some simple parsing to detect images and next links.

When parsing links, include links from href attributes and onclick Javascript events (e.g. location.href or document.location). Be careful to correctly extend the relative URLs before adding them to the frontier.
Detect images on a web page only based on img tag, where the src attribute points to an image URL.
Donwload HTML content only. List all other content (.pdf, .doc, .docx, .ppt and .pptx) in the page_data table - there is no need to populate data field (i.e. binary content). In case you put a link into a frontier and identify content as a binary source, you can just set its page_type to BINARY. The same holds for the image data.

In your crawler implementation you can use libraries that implement headless browsers but not libraries that already implement web crawler functionality. Therefore, some useful libraries that you can use are:
- HTML Cleaner
- HTML Parser
- JSoup
- Jaunt API
- HTTP Client
- Selenium
- phantomJS
- HTMLUnit
- etc.

On the other hand, you MUST NOT use libraries like the following:
- Scrapy
- Apache Nutch
- crawler4j
- gecco
- Norconex HTTP Collector
- webmagic
- Webmuncher
- etc.

To make sure that you correctly gather all the needed content placed into the DOM by Javascript, you should use headless browsers. Googlebot implements this as a two-step process or expects to retrieve dynamically built web page from an HTTP server. A nice session on crawling modern web sites built using JS frameworks, link parsing and image indexing was a part of Google IO 2018 and it is suggested for you to check it:

## Database
Table site contains web site specific data. Each site can contain multiple web pages - table page. Populate all the fields accordingly when parsing. If a page is of type HTML, its content should be stored as a value within html_content attribute, otherwise (if crawler detects a binary file - e.g. .doc), html_content is set to NULL and a record in the page_data table is created. Available page type codes are HTML, BINARY, DUPLICATE and FRONTIER. The duplicate page should not have set the html_content value and should be linked to a duplicate version of a page.

You can optionally use table page also as a current frontier queue storage.

## Report

The report should follow the standard structure. It must not exceed 2 pages.

In the report include the following:

All the specifics and decisions you make based on the instructions above and describe the implementation of your crawler.
Document also parameters that are needed for your crawler, specifics, problems that you had during the development and solutions.
For the sites that are given in the instructions’ seed list and also for the whole crawldb together (for both separately) report general statistics of crawldb (number of sites, number of web pages, number of duplicates, number of binary documents by type, number of images, average number of images per web page, …).
Visualize links and include images into the report. If the network is too big, take only a portion of it or high-level representation (e.g. interconnectedness of specific domains). Use visualization libraries such as D3js, visjs, sigmajs or gephi.

## Submission

Only one of the group members should make a submission of the assignment in moodle. The submission should contain only a link to the repository that contains the following which you will use for all the submissions during the course:

- a file pa1/db
- a file pa1/report.pdf - PDF report.
- a file pa1/README.md - Short description of the project and instructions to install, set up and run the crawler.
- a folder pa1/crawler - Implementation of the crawler.