# !python3
import sys
import os

import re
import datetime

from PIL import Image
from icrawler.builtin import BingImageCrawler
from dotenv import load_dotenv
from google.cloud import storage
from logging import getLogger, StreamHandler, DEBUG


def main():
    '''main process
    '''
    # for time logging start
    datetime_start = datetime.datetime.now()
    datetime_start_formated = format(datetime_start, '%Y/%m/%d %H:%M:%S')
    logger.debug(f'START AT : {datetime_start_formated}')

    # main process
    try:
        # load .env
        load_dotenv()
        # make dir
        if not os.path.isdir(WORKING_DIRECTORY):
            os.makedirs(WORKING_DIRECTORY)
        # crawling from Bing
        BingCrawl(SEARCH_WORD, WORKING_DIRECTORY, SEARCH_QT)
        # resize and get list
        dir_save_resizedimg, list_resizedimg = resize_image(WORKING_DIRECTORY)
        # upload gcs
        upload_gcs(dir_save_resizedimg, list_resizedimg)
    except Executionerror:
        logger.debug('running failed in main process')
    
    # for time logging end
    datetime_end_formated = format(datetime.datetime.now(), '%Y/%m/%d %H:%M:%S')
    total_time = datetime.datetime.now() - datetime_start
    logger.debug(f'END AT   : {datetime_end_formated}')
    logger.debug(f'TOTAL    : {total_time}')

def BingCrawl(SEARCH_WORD:str, WORKING_DIRECTORY: str, SEARCH_QT: int):
    '''Bing画像検索で画像を取得する
    '''
    # SEARCH_QT = 3
    # # make dir
    # if not os.path.isdir(IMG_PATH):
    #     os.makedirs(IMG_PATH)
    # crawl and save to dir
    crawler = BingImageCrawler(storage = {"root_dir": WORKING_DIRECTORY})
    crawler.crawl(keyword = SEARCH_WORD, max_num = SEARCH_QT)


def resize_image(WORKING_DIRECTORY :str):
    '''取得した画像を指定サイズでリサイズ
    '''
    # jpg fileのみをリスト化
    filelist = os.listdir(WORKING_DIRECTORY)
    jpg_filelist = [file for file in filelist if re.search(r'.jpg$', file)]
    print(jpg_filelist)

    # makedir of resized img
    dir_save_resizedimg = f'{WORKING_DIRECTORY}_resized'
    if not os.path.exists(dir_save_resizedimg):
        os.mkdir(dir_save_resizedimg)
        print(f'make a new dir as "{dir_save_resizedimg}" ')
    
    # set list
    list_resizedimg = []
    # resize loop
    for jpg_file in jpg_filelist:
        f = f'{WORKING_DIRECTORY}/{jpg_file}'
        img = Image.open(f)
        resized = img.resize((256, 256))
        resized.save(f'{dir_save_resizedimg}/{jpg_file}')
        print(f'save resized image to {dir_save_resizedimg}/{jpg_file}')
        list_resizedimg.append(jpg_file)
    
    return dir_save_resizedimg, list_resizedimg


def upload_gcs(dir_save_resizedimg:str, list_resizedimg: list):
    '''Google cloud storageへのアップロードをおこなう
    '''
    # set path from .env
    GCP_TOKEN = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    BUCKET_NAME = os.environ["BUCKET_NAME"]
    # connect to bucket
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)

    # upload
    for resizedimg in list_resizedimg:
        getpath=f'{dir_save_resizedimg}/{resizedimg}'
        uppath = f'{sys.argv[1]}/{resizedimg}'
        blob = bucket.blob(uppath)
        blob.upload_from_filename(filename=getpath)
    # show file list in blob
    # for blob in client.list_blobs(BUCKET_NAME):
    #     print(blob.name)


if __name__ == '__main__':
    # set log
    logger = getLogger(__name__)
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    handler.filename = 'test.log'
    logger.addHandler(handler)
    logger.propagate = False

    # set from args and make work directory.
    if not sys.argv[1:]:
        logger.debug('There are no arguments')
    SEARCH_WORD = str(sys.argv[1])
    logger.debug(f'Search word: {SEARCH_WORD}')
    SEARCH_QT = int(sys.argv[2])
    logger.debug(f'Search quantites: {SEARCH_QT}')
    WORKING_DIRECTORY = f'./{SEARCH_WORD}'

    # run main
    main()

