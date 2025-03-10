'''
借助selenium库模拟浏览器登录，获取Cookies后传给response请求，借助request.session类使每次
request请求都携带Cookies。
解决登录后，点击语文，获取主页面的HTML代码，关闭浏览器，从主页面HTMl代码中获取各个试卷页面的URL，
利用获取的试卷页的URL爬取对应的HTML代码，借助CSS选择器匹配所需的数据并保存为JSON格式
'''
# 12345@aaa

from selenium import webdriver
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq
import requests
import logging
import time

BASE_URL = 'https://zujuan.xkw.com/'
LOGIN_URL = urljoin(BASE_URL, '/login')
USERNAME = '13390680908'
PASSWORD = '1234@ABCD'  # 1234@ABCD12345@aaa
browser = webdriver.Chrome()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(levelname)s:%(message)s')
def match_data(detail_html):
    '''接收试卷页的HTML代码，匹配需要的数据并以生成器的形式返回'''
    doc = pq(detail_html)
    texts = doc('span[style="font-family:楷体;"]').items()
    for text in texts:
        yield text.text()


def scrape_page(url,session):
    '''接收一个页面的URL，返回该页面的HTML代码'''
    logging.info('scraping %s', url)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            logging.info('get html successfully')
            return response.text
        logging.error('get invalid status_code %s when scrape %s',
                      response.status_code, url)
    except requests.RequestException:
        logging.error('error occurred when scrape %s', url, exc_info=True)


def parse_detail(html):
    '''接受主页面的HTMl代码，以生成器的形式返回试卷页的url'''
    doc = pq(html)
    items = doc('a.info-title').items()  # 调用items方法得到一个生成器
    if not items:
        logging.info('empty list when using parse_detail')
        return []
    for item in items:
        detail_part_url = item.attr('href')
        detail_url = urljoin(BASE_URL, detail_part_url)
        logging.info('get detail url %s', detail_url)
        yield detail_url

def browser_login():
    '''模拟浏览器，点击登录，选择账号密码方式，输入数据，登录'''
    browser.get(LOGIN_URL)
    # 选择账号密码登录对应的按钮元素并点击
    logging.info('clicking the account password login method')
    browser.find_element(By.CSS_SELECTOR,
                         'button.another[data-mode="account-login"]').click()
    logging.info('successfully click the account password login method')
    # 输入账号密码并点击登录
    logging.info('entering the account and password and click the login')
    browser.find_element(By.CSS_SELECTOR,
                         'input#username.input.user').send_keys(
        USERNAME)
    browser.find_element(By.CSS_SELECTOR, 'input#password.input').send_keys(
        PASSWORD)
    (browser.find_element(By.CSS_SELECTOR, 'button.submit#accountLoginBtn')
     .click())
    logging.info('successfully login')

def get_Cookies_and_put_in_request():
    '''获取cookies并放入请求中'''
    # 获取Cookies
    cookies = browser.get_cookies()
    print('Cookies', cookies)
    # 把Cookies放入请求中
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session

def main():
    browser_login()
    session = get_Cookies_and_put_in_request()
    #点击叉号去除广告
    browser.find_element(By.CSS_SELECTOR,'a[data-type="closePop"]').click()
    logging.info('successfully click cross')
    # 点击语文
    browser.find_element(By.CSS_SELECTOR, 'a.item[data-subjectid="10"]').click()
    logging.info('successfully click 语文')
    # 获取主页面HTML
    main_html = browser.page_source
    logging.info('successfully get main_html')
    browser.close()
    # 获取试卷页的HTML,利用获取的试卷页的URL爬取对应的HTML代码
    detail_urls = parse_detail(main_html)
    for detail_url in detail_urls:
        detail_html = scrape_page(detail_url,session=session)
        datas = match_data(detail_html)
        if not datas:
            logging.info('empty datas')
        logging.info('print data')
        for data in datas:
            print(data)

if __name__ == '__main__':
    main()