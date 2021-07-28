from rehabmeasures.items import  RehabmeasuresItem
from scrapy import Spider, Request
import re
import math

class RehabmeasuresSpider(Spider):
    name = 'rehabmeasures_spider'
    allowed_urls = ['https://www.sralab.org/rehabilitation-measures']
    start_urls = ['https://www.sralab.org/rehabilitation-measures/database?population=4636']

    def parse(self, response):
        last_page = response.xpath('//li[@class="pager__item pager__item--last"]/a/@href').extract_first()
        last_1 = re.search('page=(\d+)', last_page)
        num_pages = int(last_1.group(1))+1

        result_urls = [f'https://www.sralab.org/rehabilitation-measures/database?population=4636&contains=&page={i}' for i in range(num_pages)]

        for url in result_urls:
            yield Request(url=url, callback=self.parse_result_page)

    def parse_result_page(self, response):
        measure_urls = response.xpath('//div[@class="view-content"]//h3[@class="search-results-item__title"]/a/@href').extract()
        measure_urls = ['https://www.sralab.org' + url for url in measure_urls]

        for url in measure_urls:
            yield Request(url=url, callback=self.parse_measure_page)

    def parse_measure_page(self, response):
            measure_name = response.xpath('//h1[@class="page-header__title"]/text()').extract_first()

            # Purpose, Link to instrument, Ancronym, Area of assessment, Assessment type, Administration mode, Cost, Diagnosis, conditoins
            fields =  response.xpath('//div[@class="page-content"]/div[@class="package--info--twoup"]/div[@class="field"]')
            field_dict = {}

            for field in fields:
                data = field.xpath('.//text()').extract()
                key = data[1]
                value = data[2:]
                value = list(filter(lambda s: s!= '', map(str.strip, value)))
                print(key, value)
                field_dict[key] = value

            # Diagnosis/conditions
            try:
                diag_conditions = response.xpath('//div[@class="field field--conditions"]//li/text()').extract()
            except:
                diag_conditions = []

            # Population, no_items, tiem to administer
            population = response.xpath('.//div[@class="package package--populations"]//a/@title').extract()
            no_items = response.xpath('.//div[@class="package package--number-of-items"]/p/text()').extract()
            no_items = [i.replace('\n', "").strip() for i in no_items]
            try:
                time = response.xpath('//p[@class="time-to-administer__value"]/text()').extract_first()
                time = time + str(" minutes")
            except:
                time = str("NA")

            # Key description
            lis = response.xpath('//div[@class="package package--key-descriptions"]//li[@class="item"]')
            descriptions = []
            for li in lis:
                text = li.xpath('./text()').extract()
                text = '\n'.join(text)
                descriptions.append(text)


            # Body parts, icf domain, measurement domain dictionary
            threeup_dict = {}
            threeup_ps = response.xpath('//div[@class="package--info--threeup"]/div[@class="field"]')

            for three in threeup_ps:
                key = three.xpath('./h4[@class="field-label"]/text()').extract_first()
                value = three.xpath('./text()').extract()
                value = list(filter(lambda s: s!= '', map(str.strip, value)))
                print(key, value)
                threeup_dict[key] = value

            # Additional information extracted from papers (e.g., reliability, validity..) for Stroke only
            disease_ps = response.xpath('//div[@class="paragraph paragraph--populations"]')
            disease_dict = {}
            for disease in disease_ps:
                title = disease.xpath('.//h2/text()').extract_first()
                disease_dict[title] = disease

            try:
                stroke_ps = disease_dict['Stroke'].xpath('./div[@class="paragraph--populations--data"]')
                stroke_dict = {}
                for field in stroke_ps:
                    stroke_data = field.xpath('./div[@class="paragraph--populations--data"]')
                    key = field.xpath('./h4[@class="field-label"]/text()').extract_first()
                    value_1 = field.xpath('.//div/p/strong/text()').extract()
                    value_2 = field.xpath('.//ul/li//text()').extract()
                    value = value_1 + value_2
                    value = list(filter(lambda s: s!= '', map(str.strip, value)))
                    stroke_dict[key] = value
            except:
                stroke_dict={}
    

            item = RehabmeasuresItem()
            item['measure_name'] = measure_name
            item['field_dict'] = field_dict
            item['diag_conditions'] = diag_conditions
            item['population'] = population
            item['no_items'] = no_items
            item['time'] = time
            item['descriptions'] = descriptions
            item['threeup_dict'] = threeup_dict
            item['stroke_dict'] = stroke_dict

            yield item