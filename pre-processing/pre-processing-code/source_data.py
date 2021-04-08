import os
import sys
import boto3
import time
from urllib.request import urlopen
import urllib.request
from urllib.error import URLError, HTTPError
from zipfile import ZipFile
from boto3.s3.transfer import TransferConfig
import requests
import urllib
import datetime 
import shutil
import uuid
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from shutil import copyfile

from selenium.webdriver.chrome.options import Options

from s3_md5_compare import md5_compare
from webdriver_task import WebDriver


def source_dataset():
    button_xpath = '//*[@id="report-wrapper"]/div/div[2]/div[2]/div[1]/div/div/div/div[1]/div/button[2]'
    page_url = 'https://www.kff.org/report-section/state-covid-19-data-and-policy-actions-policy-actions/'
    
    button_xpath_map = {
        'covid-19-state-vaccine-priority-populations': '//*[@id="report-wrapper"]/div/div[2]/div[2]/div[1]/div/div/div/div[1]/div/button[2]',
        'covid-19-state-populations-eligiblity-and-residency-requirements': '//*[@id="report-wrapper"]/div/div[2]/div[1]/div/div/div[2]/div/div/div/div/div[1]/div/button[2]',
        'covid-19-state-social-distancing-actions': '//*[@id="report-wrapper"]/div/div[2]/div[2]/div[5]/div/div/div/div/div/div/div[1]/div/button[2]',
        'covid-19-state-health-policy-actions': '//*[@id="report-wrapper"]/div/div[2]/div[2]/div[7]/div[3]/div/div/div/div/div/div/div[1]/div/button[2]',
        'covid-19-state-actions-on-telehealth': '//*[@id="report-wrapper"]/div/div[2]/div[2]/div[7]/div[5]/div[2]/div/div/div[1]/div/div/div/div[1]/div/button[2]',
        'covid-19-state-health-care-provider-capacity': '//*[@id="report-wrapper"]/div/div[2]/div[2]/div[7]/div[5]/div[4]/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div[2]/div[2]/div[1]/div/div/div/div/div/div/div/div[1]/div/button[2]',
    }
    
    data_dir = '/tmp/downloads'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
        
    s3_bucket = os.environ['S3_BUCKET']
    data_set_name = os.environ['DATA_SET_NAME']

    driver = WebDriver()
    page_source = driver.get_pagesource(page_url, button_xpath_map)
    # print(page_source)
    
    for root, dirs, files in os.walk(data_dir):
        print(root)
        print(files)
        print(dirs)
        print('--')

    # sys.exit(0)
    
    s3_uploads = []
    asset_list = []

    # filename = data_set_name + '.csv'
    # file_location = os.path.join(data_dir, filename)

    s3 = boto3.client('s3')
    
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            print(f)
            new_s3_key = data_set_name + '/dataset/' + f
            
            has_changes = True
            filedata = None
            file_location = os.path.join(root, f)
            with open(file_location, 'rb') as reader: #, encoding='utf-8'
                filedata = reader
                has_changes = md5_compare(s3, s3_bucket, new_s3_key, filedata) #BytesIO(filedata)
            if (has_changes):
                # s3_resource.Object(s3_bucket, new_s3_key).put(Body=filedata)
                s3.upload_file(file_location, s3_bucket, new_s3_key)
                print('Uploaded: ' + f)
            else:
                print('No changes in: ' + f)
            asset_source = {'Bucket': s3_bucket, 'Key': new_s3_key}
            s3_uploads.append({'has_changes': has_changes, 'asset_source': asset_source})

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