import requests
import logging
import pymongo


def scrape_api(url):
    logging.info('scraping %s...', url)
    try:
        reponse = requests.get(url)
        if reponse.status_code == 200:
            return reponse.json()
        logging.error('get invalid status code %s while scraping %s',
                      reponse.status_code, url)
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_index(page):
    url = INDEX_URL.format(limit=LIMIT, offset=LIMIT * (page - 1))
    return scrape_api(url)


def scrape_detail(id):
    url = DETAIL_URL.format(id=id)
    return scrape_api(url)


def save_data(data):
    collection.update_one({'name': data.get('name')}, {'$set':data},
                          upsert=True)


def main():
    for page in range(1, TOTAL_PAGE + 1):
        index_data = scrape_index(page)
        for item in index_data.get('results'):
            id = item.get('id')
            detail_data = scrape_detail(id)
            logging.info('detail data %s', detail_data)
            save_data(detail_data)
            logging.info('data saved successfully')


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s:%(message)s')
# %(name)s等是 Python 日志系统（logging 模块）特有的格式化占位符，普通字符串格式化（如 str.format()
# 或 f-string）并不支持它。它是专门用于在日志记录中插入日志记录器（Logger）的名称的。
INDEX_URL = 'https://spa1.scrape.center/api/movie/?limit={limit}&offset={offset}'
DETAIL_URL = 'https://spa1.scrape.center/api/movie/{id}'
LIMIT = 10
TOTAL_PAGE = 2

MONGo_CONNECTION_STRING = 'mongodb://localhost:27017'
MONGO_DB_NAME = 'movies'
MONGO_CLOOECTION_NAME = 'movies'
client = pymongo.MongoClient(MONGo_CONNECTION_STRING)
db = client['movies']
collection = db['movies']

if __name__ == '__main__':
    main()
