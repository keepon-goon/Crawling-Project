import motor
import logging
import asyncio
import aiohttp
import json
from motor.motor_asyncio import AsyncIOMotorClient


async def scrape_api(url):
    async with semaphore:
        try:
            logging.info('scraping %s', url)
            async with session.get(url) as response:
                # 发起了一个 HTTP GET 请求，并在代码块结束时自动处理响应对象的资源释放。
                # 只需要关注如何处理响应文本，而不需要担心资源管理的细节。
                return await response.json()
                # 服务器返回的响应内容可能是 JSON 格式的字符串。response.json() 方法会把
                # 这个 JSON 字符串解析为 Python 的字典（dict）或者列表（list）对象，这样
                # 就能在 Python 代码里方便地处理这些数据了。
        except aiohttp.ClientError:  # ClientError 是一个基类异常
            logging.info('error occured when scraping %s', url, exc_info=True)


async def scrape_index(page):
    url = INDEX_URL.format(offset=PAGE_SIZE * (page - 1))
    return await scrape_api(url)


async def save_data(data):
    logging.info('saving data %s', data)
    if data:
        return await collection.update_one({
            'id': data.get('id')
        }, {
            '$set': data
        }, upsert=True)


async def scrape_detail(id):
    url = DETAIL_URL.format(id=id)
    data = await scrape_api(url)
    await save_data(data)


async def main():
    global session
    session = aiohttp.ClientSession()
    scrpae_index_tasks = [asyncio.ensure_future(scrape_index(page)) for page in
                          range(1, PAGE_NUMBER + 1)]
    # 还未执行，只是一堆task对象
    results = await asyncio.gather(*scrpae_index_tasks)
    # 见笔记
    logging.info('result %s', json.dumps(results, ensure_ascii=False, indent=2))
    ids = []
    for index_data in results:
        if not index_data: continue
        for item in index_data.get('results'):
            ids.append(item.get('id'))
    scrpae_detail_tasks = [asyncio.ensure_future(scrape_detail(id)) for id in
                           ids]
    await asyncio.wait(scrpae_detail_tasks)
    # 等待所有task执行完成才会继续下一步，见笔记
    await session.close()
    # aiohttp.ClientSession 的 close 方法是一个异步方法，它返回一个协程对象


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
INDEX_URL = 'https://spa5.scrape.center/api/book/?limit=18&offset={offset}'
DETAIL_URL = 'https://spa5.scrape.center/api/book/{id}/'
CONCURRENCY = 5
PAGE_NUMBER = 3
PAGE_SIZE = 18
MONGO_CONNECTION_STRING = 'mongodb://localhost:27017'
MONGO_DB_NAME = 'books'
MONGO_COLLECTION_NAME = 'books'

semaphore = asyncio.Semaphore(CONCURRENCY)
session = None

client = AsyncIOMotorClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
