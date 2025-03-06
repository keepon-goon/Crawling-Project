import json
from os import makedirs
from os.path import exists

RESULT_DIR = 'result'
exists(RESULT_DIR) or makedirs(RESULT_DIR)


def save_data(data):
    name = data.get('name')
    data_path = f'{RESULT_DIR}/{name}.json'
    json.dump(data, open(data_path,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
