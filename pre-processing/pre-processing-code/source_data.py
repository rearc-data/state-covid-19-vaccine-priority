import os
import sys
import boto3
import time
from urllib.request import urlopen
import urllib.request
from urllib.error import URLError, HTTPError
from zipfile import ZipFile
import requests
import urllib
import datetime 
import shutil
import uuid
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from shutil import copyfile

from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType


from s3_md5_compare import md5_compare


def get_default_chrome_options():
    # chrome_options = webdriver.ChromeOptions()

    chrome_tmp_dir = '/tmp'
    if not os.path.exists(chrome_tmp_dir):
        os.mkdir(chrome_tmp_dir)
    
    chrome_options = Options()
    print(chrome_options.capabilities['version'])
    #chrome_options.add_argument('--headless')
    #chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
    # chrome_options.add_argument('--window-size={}x{}'.format(1280, 1024))
    # chrome_options.add_argument('--user-data-dir={}'.format(chrome_tmp_dir + '/user-data'))
    # chrome_options.add_argument('--data-path={}'.format(chrome_tmp_dir+ '/data-path'))
    # chrome_options.add_argument('--homedir={}'.format(chrome_tmp_dir))
    # chrome_options.add_argument('--disk-cache-dir={}'.format(chrome_tmp_dir + '/cache-dir'))

    chrome_options.binary_location = "tmp/chromedriver"
    

    

    return chrome_options 


def click_for_download():
    button_xpath = '//*[@id="report-wrapper"]/div/div[2]/div[2]/div[1]/div/div/div/div[1]/div/button[2]'

    page_url = 'https://www.kff.org/report-section/state-covid-19-data-and-policy-actions-policy-actions/'
    
    driver_url = 'https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip'
    #r = requests.get(driver_url, allow_redirects=True)
    #open('/tmp/chromedriver', 'wb').write(r.content)
    #localDestination = "/home/user/local/path/to/file.pdf"
    #resultFilePath, responseHeaders = urllib.urlretrieve(driver_url, "/tmp/")
    
    
    #fullfilename = os.path.join('/tmp/', 'chromedriver')
    #urllib.request.urlretrieve(driver_url, fullfilename)

    
    data_dir = '/tmp/'
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            print(f)
        for d in dirs:
            print(d)
        print (root)
        
        
    newPath = os.path.join(os.getcwd(), "/tmp/chromedriver")
    
    print("here")
    print(os.getcwd())
    print(os.path.isfile(newPath))

    

    chromedriver_path = "/tmp/chromedriver"
    
    print(chromedriver_path)
    os.chmod(newPath, 0o775)
    copyfile(newPath, chromedriver_path)
    #os.rename("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
    #shutil.move(os.path.join(os.getcwd(), "tmp/chromedriver"), chromedriver_path)
    #os.replace("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
    
    os.chmod(chromedriver_path, 0o775)
    chrome_options = get_default_chrome_options()

    driver = webdriver.Chrome(executable_path = chromedriver_path, chrome_options=chrome_options) # executable_path=chromedriver_path, 
    print(driver.capabilities['version'])
    driver.get(page_url)
    driver.find_element_by_xpath(button_xpath).click()

    page_source = driver.page_source

    #print(page_source)

    driver.quit()

    return page_source

def source_dataset():
    click_for_download()
    

    s3_uploads = []
    asset_list = []
    data_dir  = '/tmp'
    data_set_name = os.environ['DATA_SET_NAME']
    filename = data_set_name + '.csv'
    file_location = '/tmp/' + filename

    s3_bucket = os.environ['S3_BUCKET']
    new_s3_key = data_set_name + '/dataset/' + filename
    s3 = boto3.client('s3')



    for root, dirs, files in os.walk(data_dir):
        for f in files:
            print(f)
            new_s3_key = data_set_name + '/dataset/' + f

            has_changes = md5_compare(s3, s3_bucket, new_s3_key,file_location)
            if(has_changes):
                s3.upload_file(file_location, s3_bucket, new_s3_key)
                print('Uploaded: ' + filename)
            else:
                print('No changes in: ' + filename)
            asset_source = {'Bucket': s3_bucket, 'Key': new_s3_key}
            s3_uploads.append({'has_changes': has_changes, 'asset_source': asset_source})


    count_updated_data = sum(upload['has_changes'] is True for upload in s3_uploads)
    if count_updated_data > 0:
        asset_list = list(map(lambda upload: upload['asset_source'], s3_uploads))
        if len(asset_list) == 0:
            raise Exception('Something went wrong when uploading files to s3')


    return asset_list



            


    
    count_updated_data = sum(upload['has_changes'] == True for upload in s3_uploads)
    if count_updated_data > 0:
        asset_list = list(map(lambda upload: upload['asset_source'], s3_uploads))
        if len(asset_list) == 0:
            raise Exception('Something went wrong when uploading files to s3')
    # asset_list is returned to be used in lamdba_handler function
    # if it is empty, lambda_handler will not republish
    return asset_list



if __name__ == '__main__':
    source_dataset()