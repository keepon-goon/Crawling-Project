'''
运用selenium库模拟浏览器登录操作，获取cookies并传给response请求，使得每次response请求里都
携带Cookies，从而使服务器认为已经处于登录状态
'''

from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time

BASE_URL = 'https://login2.scrape.center/'
LOGIN_URL = urljoin(BASE_URL, '/login')
INDEX_URL = urljoin(BASE_URL, '/page/1')
USERNAME = 'admin'
PASSWORD = 'admin'

browser = webdriver.Chrome()
browser.get(LOGIN_URL)  # 打开登录页面
browser.find_element(By.CSS_SELECTOR, 'input[name="username"]').send_keys(
    USERNAME)
# 在用户名框里输入用户名
browser.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(
    PASSWORD)
browser.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
time.sleep(10)

# 从浏览器对象中获取Cookie信息
cookies = browser.get_cookie()
print('Cookies', cookies)
browser.close()

# 把Cookie放入请求中
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])
response_index = session.get(INDEX_URL)
print('Response status', response_index.status_code)
print('Response URL', response_index.url)
