'''
通过selenium库，模拟用户在浏览器的各种行为，来爬取数据。
selenium可以打开HTML代码并进一步分析
'''

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urljoin
import logging

import a01_write

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

INDEX_URL = 'https://spa2.scrape.center/page/{page}'
TIME_OUT = 10
TOTAL_PAGE = 2

browser = webdriver.Chrome()
wait = WebDriverWait(browser, TIME_OUT)


def scrape_page(url, condition, locator):
    '''
    对任意URL进行爬取，状态监听，异常处理
    :param url:
    :param condition: 页面加载成功的判断条件
    :param locator: 定位器
    :return:
    '''
    logging.info('scraping %s', url)
    try:
        browser.get(url)
        wait.until(condition(locator))
    except TimeoutException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_index(page):
    '''加载列表页，这里不返回任何结果，执行完方法后列表页刚好处于加载完成状态'''
    url = INDEX_URL.format(page=page)
    scrape_page(url, EC.visibility_of_all_elements_located,
                (By.CSS_SELECTOR, '#index .item'))


def parse_index():
    '''解析列表页，返回详情页的url'''
    elements = browser.find_elements(By.CSS_SELECTOR, '#index .item .name')
    for element in elements:
        href = element.get_attribute('href')
        yield urljoin(INDEX_URL, href)


def scrape_detail(url):
    '''爬取详情页'''
    scrape_page(url, condition=EC.visibility_of_all_elements_located,
                locator=(By.TAG_NAME, 'h2'))



def parse_detail():
    '''解析详情页，以字典类型返回匹配的值'''
    url = browser.current_url
    name = browser.find_element(By.TAG_NAME,'h2').text
    categories = [element.text for element in
                  browser.find_elements(By.CSS_SELECTOR,'.categories button span')]
    cover = browser.find_element(By.CSS_SELECTOR,'.cover').get_attribute('src')
    score = browser.find_element(By.CLASS_NAME,'score').text
    drama = browser.find_element(By.CSS_SELECTOR,'.drama p').text

    return {
        'url':url,
        'name':name,
        'categories':categories,
        'cover':cover,
        'score':score,
        'drama':drama
    }


def main():
    try:
        for page in range(1, TOTAL_PAGE + 1):
            scrape_index(page)
            detail_urls = parse_index()
            # logging.info('detail urls %s', list(detail_urls))
            for detail_url in list(detail_urls):
                logging.info('get detail urls %s',detail_url)
                scrape_detail(detail_url)
                detail_data = parse_detail()
                # logging.info('detail data %s',detail_data)
                logging.info('saving data in json')
                a01_write.save_data(data=detail_data)
                logging.info('save data successfully')
    finally:
        browser.close()


if __name__ == '__main__':
    main()
