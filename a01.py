import requests
import logging
import re
from urllib.parse import urljoin
import multiprocessing

import a01_write

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'https://ssr1.scrape.center/'
TOTAL_PAGE = 1


def scrape_page(url):
    '''接受一个页面的url,爬取此页面的HTML代码'''
    logging.info('scraping %s...', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        logging.error('get invalid status code %s while scraping %s',
                      response.status_code, url)
    except requests.RequestException:
        #requests.RequestException 是 Python requests 库中所有请求异常的基类，
        # 它用于捕获和处理在使用 requests 库进行 HTTP 请求时可能出现的各种异常情况。
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_index(page):
    '''接受一个页码，返回该页码对应的页面的HTML代码'''
    index_url = f'{BASE_URL}/page/{page}'
    return scrape_page(index_url)


def parse_index(html):
    '''接受页面的HTML代码，从中匹配详情页的url并且返回url'''
    pattern = re.compile('<a.*?href="(.*?)".*?class="name">')
    items = re.findall(pattern, html)
    if not items:
        return []
    for item in items:
        detail_url = urljoin(BASE_URL, item)
        logging.info('get detail url %s', detail_url)
        yield detail_url


def main(page):
    '''爬取所有详情页的url，并对详情页所需信息进行爬取,采用多进程'''
    # for page in range(1, TOTAL_PAGE + 1):
    #     index_html = scrape_index(page)
    #     detail_urls = parse_index(index_html)
    #     for detail_url in detail_urls:
    #         detail_html = scrape_detail(detail_url)
    #         data = parse_detail(detail_html)
    #         logging.info('get detail data %s', data)
    #         # logging.info('detail urls %s', list(detail_urls))
    #         # list(detail_urls) 是是一个将迭代器或生成器转换为列表的操作。
    #         # 在 Python 中，list() 函数可以接受任何可迭代的对象（如列表、元组、字符串、文件对象或生成器）
    #         # 并将其转换为一个新的列表。
    #         logging.info('saving data to json file')
    #         a01_write.save_data(data)
    #         logging.info('saved data successfully')

    #采用多进程
    index_html = scrape_index(page)
    detail_urls = parse_index(index_html)
    for detail_url in detail_urls:
        detail_html = scrape_detail(detail_url)
        data = parse_detail(detail_html)
        logging.info('get detail data %s', data)
        logging.info('saving data to json file')
        a01_write.save_data(data)
        logging.info('saved data successfully')


def scrape_detail(url):
    '''接受一个详情页的url，返回详情页的HTML代码'''
    return scrape_page(url)


def parse_detail(html):
    '''接收HTML代码，匹配所要的各项信息，最终返回一个字典'''

    cover_pattern = re.compile('<img.*?src="(.*?)".*?class="cover">', re.S)
    name_pattern = re.compile('<h2.*?>(.*?)</h2>')
    categories_pattern = re.compile('<button.*?category.*?'
                                    '<span>(.*?)</span>.*?</button>', re.S)
    published_at_pattern = re.compile('(\d{4}-\d{2}-\d{2})\s?上映')
    drama_pattren = re.compile('<div.*?drama.*?>.*?<p.*?>(.*?)</p>', re.S)
    score_pattern = re.compile('<p.*?score.*?>(.*?)</p>', re.S)

    cover = re.search(cover_pattern, html).group(1).strip() if \
        (re.search(categories_pattern, html)) else None
    name = re.search(name_pattern, html).group(1).strip() if \
        (re.search(name_pattern, html)) else None
    categories = re.findall(categories_pattern, html) if \
        (re.findall(categories_pattern, html)) else None
    published_at = re.search(published_at_pattern, html).group(1) if (
        re.search(published_at_pattern, html)) else None
    drama = re.search(drama_pattren, html).group(1).strip() if (
        re.search(drama_pattren, html)) else None
    score = float(re.search(score_pattern, html).group(1).strip()) if (
        re.search(score_pattern, html)) else None
    return {
        'cover': cover,
        'name': name,
        'categories': categories,
        'published_at': published_at,
        'drama': drama,
        'score': score
    }


if __name__ == '__main__':
    pool = multiprocessing.Pool()
    pages = range(1,TOTAL_PAGE+1)
    pool.map(main,pages)
    pool.close()
    pool.join()