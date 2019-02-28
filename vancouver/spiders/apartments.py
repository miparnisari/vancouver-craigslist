# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy import Request


class ApartmentsSpider(scrapy.Spider):
    name = 'apartments'
    allowed_domains = ['https://vancouver.craigslist.org/search/apa']
    start_urls = ['https://vancouver.craigslist.org/search/apa?sort=priceasc&availabilityMode=0&bundleDuplicates=1&hasPic=1&max_bathrooms=1&max_bedrooms=1&min_bathrooms=1&min_bedrooms=1&postal=V6E1G3&search_distance=3/']

    def parse(self, response):
        apts = response.xpath('//p[@class="result-info"]')
        p = re.compile("(\d*)ft")
        for apt in apts:
            title = apt.xpath('a/text()').extract_first()
            price_per_month = apt.xpath('span[@class="result-meta"]/span[@class="result-price"]/text()').extract_first().replace('$', '');
            size = apt.xpath('span[@class="result-meta"]/span[@class="housing"]/text()').extract_first().strip()
            
            m = p.search(size)
            if m:
              normalized_size = m.group(1)
              relative_url = apt.xpath('a/@href').extract_first()
              absolute_url = response.urljoin(relative_url)

              cost_per_sq_ft = float(price_per_month) / float(normalized_size)
          
              yield{
                'URL':absolute_url, 
                'Size in sq ft':normalized_size,
                'Price per month':price_per_month, 
                'Cost per sq ft': cost_per_sq_ft}

        relative_next_url = response.xpath('//a[@class="button next"]/@href').extract_first("")
        absolute_next_url = response.urljoin(relative_next_url)
        if(relative_next_url != ""):
          yield Request(absolute_next_url, callback=self.parse, dont_filter=True)