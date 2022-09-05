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
            # thumbnail = extract_news(article,"//a[@class = 'story__thumb']/img/@data-src")

            if(title == None):
                url = extract_news(article,"//a[@class = 'story__title cms-link']//@href")
            #     title = extract_news(article,"//a[@class = 'story__title cms-link']//@title")
            #     thumbnail = None
            # id = extract_id_from_url(url)
            count+=1
            yield  scrapy.Request(response.urljoin(url),self.getContentOfNews,method="GET",dont_filter=True,)
    def getContentOfNews(self,response):
        listTagnameP = response.xpath("//div[@class = 'details__content']/div/p").getall()
        arrayContent = []
        for tabnameP in listTagnameP:
            rel = Selector(text=tabnameP)
            itemContent =''
            for content in rel.xpath("//p//text()").getall():
                itemContent = itemContent +" "+ content
            arrayContent.append(itemContent)
            # arrayContent.append(content.xpath(".//text()"))
        listImage = response.xpath("//td[@class = 'pic']/img/@data-src").getall()
        if(len(listImage)!=0):
            listImage[0] = response.xpath("//td[@class = 'pic']/img/@src").extract_first()
        yield {
            "id_content":extract_id_from_url(response.url),
            "url":response.url,
            "test":arrayContent,
            "list_image":listImage
        }
    def getInforOfNews(self,response):
        a  =  response.xpath("//h1[@class = 'details__headline cms-title']/text()").extract_first()
        title =  a.replace("/n","").strip()
        thumbnail = response.xpath("//td[@class = 'pic']/img/@src").extract_first()
        if(thumbnail == None):
            thumbnail = response.xpath("//img[@class = 'cms-photo']/@src").extract_first()

        breadcrumb = response.xpath("//li[@class ='breadcrumb-item']/a/text()").getall()
        if(len(breadcrumb)<=1):
            category = breadcrumb[0]
            category_parent = breadcrumb[0]
        else :
            category = breadcrumb[1]
            category_parent = breadcrumb[0]
        time = response.xpath("//div[@class = 'meta']/time/text()").get()   
        author_name = response.xpath("//div[@class = 'details__author__meta ']/a/@title").extract_first()
        if(author_name == None):
            author_name = response.xpath("//div[@class = 'details__author__meta not-rating']/a/@title").extract_first()
            
        # content = response.xpath("//div[@class = 'l-content']/text()").get()
        description = response.xpath("//meta[@name = 'description']/@content").extract_first() 
        yield {
            "id":extract_id_from_url(response.url),
            "title":title,
            "url":response.url,
            "thumbnail":thumbnail,
            "category_parent":category_parent,
            "category":category,
            "time" : time ,
            "author_name":author_name,
            # "content":content
            "description":description

        }