'''
基于JWT登录的网页，先使用post请求模拟登录，获取JWT，在之后发送请求时均带上JWT
'''

import requests
from urllib.parse import urljoin

BASE_URL = 'https://login3.scrape.center/'
LOGIN_URL = urljoin(BASE_URL, '/api/login')
INDEX_URL = urljoin(BASE_URL, '/api/book')
USERNAME = 'admin'
PASSWORD = 'admin'

requests_login = requests.post(LOGIN_URL,json={
    'username':USERNAME,
    'password':PASSWORD
})
data = requests_login.json()
# Python 的requests库进行 HTTP 请求后，将响应内容解析为 JSON 格式的数据。
# 调用这个方法将其转换为 Python 的字典或列表对象，方便后续的数据处理。
print('Response JSON',data)
jwt = data.get('token')
print('JWT',jwt)

headers = {
    'Authorization':f'jwt{jwt}'
}
response_index = requests.get(INDEX_URL,params={
    'limit':18,
    'offset':0
},headers=headers)
print('Response status', response_index.status_code)
print('Response url',response_index.url)
print('Response data',response_index.json())
