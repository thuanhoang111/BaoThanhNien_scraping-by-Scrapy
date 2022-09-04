from encodings import utf_8
from unicodedata import category
from urllib.request import Request
import scrapy
import re
from urllib import parse
from scrapy.selector import Selector

def extract_id_from_url(url: str) -> str:
    result = re.search("post\d{1,}.html", url)
    post_id = re.findall("\d", result.group(0))
    return ''.join(post_id)
def extract_news(html: str, xpath: str) -> str:
    return Selector(text=html).xpath(xpath).get()

class Main(scrapy.Spider):
    name = 'newsDB'
    allowed_domains = ['thanhnien.vn']

    # target urls
    start_urls = [
        'https://thanhnien.vn/thoi-su/',
    ]
    def parse(self, response):
        articles = response.xpath("//article[@class = 'story']").getall()
        count = 0 
        for article in articles:
            url = extract_news(article,"//a[@class = 'story__thumb']/@href")
            title = extract_news(article,"//a[@class = 'story__thumb']//@title")
            thumbnail = extract_news(article,"//a[@class = 'story__thumb']/img/@data-src")

            if(title == None):
                url = extract_news(article,"//a[@class = 'story__title cms-link']//@href")
                title = extract_news(article,"//a[@class = 'story__title cms-link']//@title")
                thumbnail = None
            id = extract_id_from_url(url)
            count+=1
            yield  scrapy.Request(response.urljoin(url),self.getavt,method="GET",dont_filter=True,)
            # url1 = response.xpath("//a[@class = 'story__title cms-link']//@href").extract_first()
            # print(count)
            # yield {
            #     "id":id,
            #     "title":title,
            #     "url":url,
            #     "thumbnail":thumbnail
            # }
    def getavt(self,response):
        a  =  response.xpath("//h1[@class = 'details__headline cms-title']/text()").extract_first()
        title =  a.replace("/n","").strip()
        thumbnail = response.xpath("//td[@class = 'pic']/img/@src").extract_first()
        breadcrumb = response.xpath("//li[@class ='breadcrumb-item']/a/text()").getall()
        # print(breadcrumb)
        if(len(breadcrumb)<=1):
            category = breadcrumb[0]
            category_parent = breadcrumb[0]
        else :
            category = breadcrumb[1]
            category_parent = breadcrumb[0]
        # print(breadcrumb[1])
       

        yield {
            "id":extract_id_from_url(response.url),
            "title":title,
            "url":response.url,
            "thumbnail":thumbnail,
            "category_parent":category_parent,
            "category":category

        }