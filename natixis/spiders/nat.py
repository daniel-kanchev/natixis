import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from natixis.items import Article


class NatSpider(scrapy.Spider):
    name = 'nat'
    start_urls = ['https://www.natixis.com/natixis/en/news-c_5045.html']

    def parse(self, response):
        links = response.xpath('//a[@class="txt-card-title"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="txt-date"]/span/text()').get().split()[-1]
        if date:
            date = datetime.strptime(date.strip(), '%m/%d/%y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="wysiwyg"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        category = ",".join(response.xpath('//span[@class="hashtag txt-keyword"]/text()').getall())

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('category', category)

        return item.load_item()
