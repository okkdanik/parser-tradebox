import scrapy

class ParserSpider(scrapy.Spider):
    name = "parser"
    allowed_domains = ['tradebox.shop']
    start_urls = ['https://tradebox.shop/']

    def parse(self, response):
        """
        Парсит главную страницу сайта на категории.
        """
        for category_link in response.css('div.header__catalog-dropdown.clear ul li a::attr(href)').getall():
            yield response.follow(category_link, callback=self.parse_category)

    def parse_category(self, response):
        """
        Парсит категорию товаров на каждый товар и следующие страницы.
        """
        for product_link in response.css('div.clear a.card__img::attr(href)').getall():
            yield response.follow(product_link, callback=self.parse_product)

        next_pages = response.css('.pagination a::attr(href)').getall()
        for next_page in next_pages:
            if next_page:
                yield response.follow(next_page, callback=self.parse_category)

    def parse_product(self, response):
        """
        Парсит страницу товара и извлекает данные о нем.
        """

        price_text = response.css('.product__price::text').get().strip()

        if price_text == 'Нет в наличии':
            price = 'Нет в наличии'
        else:
            price = response.css('.product__price span::text').get().strip()

        yield {
            'group': response.css('div.breadcrumbs a::text')[1].get().strip(),
            'category': response.css('div.breadcrumbs a::text')[2].get().strip(),
            'title': response.css('.product__content h1::text').get(),
            'price': price,
            'link': response.request.url
        }

# scrapy crawl parser -o data.csv