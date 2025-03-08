import requests
import logging
from pyquery import PyQuery as pq
from urllib.parse import urljoin


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(levelname)s:%(message)s')

BASE_URL = 'https://zujuan.xkw.com/'
TOTAL_PAGE = 1

def scrape_page(url):
    '''接收一个页面的URL，返回该页面的HTML代码'''
    logging.info('scraping %s',url)
    try:
        headers = {
            'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
        }
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        logging.error('get invaild status_code %s when scrape %s',
                      response.status_code,url)
    except requests.RequestException:
        logging.error('error occurred when scrape %s',url,exc_info=True)


def parse_detail(html):
    '''接受一个页面的HTMl代码，以生成器的形式返回详情页的url'''
    doc = pq(html)
    items = doc('a .info_title').items()#调用items方法得到一个生成器
    if not items:
        return []
    for item in items:
        detail_part_url = item.attr('href')
        detail_url = urljoin(BASE_URL,detail_part_url)
        logging.info('get detail url %s',detail_url)
        yield detail_url

def main():
    html = scrape_page(BASE_URL)
    detail_urls = parse_detail(html)
    for detail_url in detail_urls:
        detail_html = scrape_page(detail_url)
        datas = match_data(detail_html)
        if not datas:
            logging.info('empty datas')
            return []
        logging.info('print data')
        for data in datas:
            print(data)


def match_data(detail_html):
    '''接收详情页的HTML代码，匹配需要的数据并以生成器的形式返回'''
    doc = pq(detail_html)
    texts = doc('span[style="font-family:楷体;"]').items()
    for text in texts:
        yield text

if __name__ == '__main__':
    main()