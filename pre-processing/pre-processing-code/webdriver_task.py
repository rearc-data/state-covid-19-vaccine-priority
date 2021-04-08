import os
import shutil
import uuid
import logging
import time

from selenium import webdriver

logger = logging.getLogger()

class WebDriver:
    def __init__(self):
        self._tmp_folder = '/tmp' #'/tmp/{}'.format(uuid.uuid4())

        if not os.path.exists(self._tmp_folder):
            os.makedirs(self._tmp_folder)

        if not os.path.exists(self._tmp_folder + '/user-data'):
            os.makedirs(self._tmp_folder + '/user-data')

        if not os.path.exists(self._tmp_folder + '/data-path'):
            os.makedirs(self._tmp_folder + '/data-path')

        if not os.path.exists(self._tmp_folder + '/cache-dir'):
            os.makedirs(self._tmp_folder + '/cache-dir')
            
        if not os.path.exists(self._tmp_folder + '/downloads'):
            os.makedirs(self._tmp_folder + '/downloads')

    def __get_default_chrome_options(self):
        chrome_options = webdriver.ChromeOptions()

        lambda_options = [
            '--no-sandbox',
            # '--start-maximized',
            # '--disable-infobars',
            # '--disable-extensions',
            '--autoplay-policy=user-gesture-required',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-client-side-phishing-detection',
            '--disable-component-update',
            '--disable-default-apps',
            '--disable-dev-shm-usage',
            '--disable-domain-reliability',
            '--disable-extensions',
            '--disable-features=AudioServiceOutOfProcess',
            '--disable-hang-monitor',
            '--disable-ipc-flooding-protection',
            '--disable-notifications',
            '--disable-offer-store-unmasked-wallet-cards',
            '--disable-popup-blocking',
            '--disable-print-preview',
            '--disable-prompt-on-repost',
            '--disable-renderer-backgrounding',
            '--disable-setuid-sandbox',
            '--disable-speech-api',
            '--disable-sync',
            '--disk-cache-size=33554432',
            '--hide-scrollbars',
            '--ignore-gpu-blacklist',
            '--ignore-certificate-errors',
            '--metrics-recording-only',
            '--mute-audio',
            '--no-default-browser-check',
            '--no-first-run',
            '--no-pings',
            '--no-zygote',
            '--password-store=basic',
            '--use-gl=swiftshader',
            '--use-mock-keychain',
            '--single-process',
            '--headless']

        # chrome_options.add_argument('--disable-gpu')
        for argument in lambda_options:
            chrome_options.add_argument(argument)          
        chrome_options.add_argument('--user-data-dir={}'.format(self._tmp_folder + '/user-data'))
        chrome_options.add_argument('--data-path={}'.format(self._tmp_folder + '/data-path'))
        chrome_options.add_argument('--homedir={}'.format(self._tmp_folder))
        chrome_options.add_argument('--disk-cache-dir={}'.format(self._tmp_folder + '/cache-dir'))
        chrome_options.add_argument('download.default_directory={}'.format(self._tmp_folder + '/downloads'))
        
        chrome_options.binary_location = "/opt/bin/chromium" 
        
        # chrome_options.add_argument('--no-sandbox') # Bypass OS security model
        # chrome_options.add_argument('--disable-dev-shm-usage') # overcome limited resource problems
        # chrome_options.add_argument("--start-maximized") #  open Browser in maximized mode
        # chrome_options.add_argument("--disable-infobars") #  disabling infobars
        # chrome_options.add_argument("--disable-extensions") #  disabling extensions
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--remote-debugging-port=9222')
        
        
        # chrome_options.add_argument('--disable-gpu') # applicable to windows os only
        # chrome_options.add_argument('--enable-logging')
        # chrome_options.add_argument('--log-level=0')
        # chrome_options.add_argument('--v=99')
        # chrome_options.add_argument('--single-process')
        # chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument(
        #     'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
        # chrome_options.add_argument('--window-size={}x{}'.format(1280, 1024))
        # chrome_options.add_argument('--user-data-dir={}'.format(chrome_tmp_dir + '/user-data'))
        # chrome_options.add_argument('--data-path={}'.format(chrome_tmp_dir+ '/data-path'))
        # chrome_options.add_argument('--homedir={}'.format(chrome_tmp_dir))
        # chrome_options.add_argument('--disk-cache-dir={}'.format(chrome_tmp_dir + '/cache-dir'))
        

        return chrome_options      

    # def enable_download_in_headless_chrome(self):
    #     """
    #     This function was pulled from
    #     https://github.com/shawnbutton/PythonHeadlessChrome/blob/master/driver_builder.py#L44

    #     There is currently a "feature" in chrome where
    #     headless does not allow file download: https://bugs.chromium.org/p/chromium/issues/detail?id=696481

    #     Specifically this comment ( https://bugs.chromium.org/p/chromium/issues/detail?id=696481#c157 )
    #     saved the day by highlighting that download wasn't working because it was opening up in another tab.

    #     This method is a hacky work-around until the official chromedriver support for this.
    #     Requires chrome version 62.0.3196.0 or above.
    #     """
    #     self._driver.execute_script(
    #         "var x = document.getElementsByTagName('a'); var i; for (i = 0; i < x.length; i++) { x[i].target = '_self'; }")
    #     # add missing support for chrome "send_command"  to selenium webdriver
    #     self._driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    #     params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': self.download_location}}
    #     command_result = self._driver.execute("send_command", params)
    #     print("response from browser:")
    #     for key in command_result:
    #         print("result:" + key + ":" + str(command_result[key]))
            
            
    def __get_correct_height(self, url, width=1280):
        chrome_options=self.__get_default_chrome_options()
        chrome_options.add_argument('--window-size={}x{}'.format(width, 1024))
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url)
        height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight )")
        driver.quit()
        return height    

    def get_pagesource(self, url, button_xpath_map, width=1280, height=None):
        page_source = None
        if height is None:
            height = self.__get_correct_height(url, width=width)

        chrome_options = self.__get_default_chrome_options()
        chrome_options.add_argument('--window-size={}x{}'.format(width, height))
        # chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--hide-scrollbars')
        
        driver = webdriver.Chrome(chrome_options=chrome_options)
        logger.info('Using Chromium version: {}'.format(driver.capabilities['browserVersion']))
        
        # enable_download_in_headless_chrome
        driver.execute_script(
            "var x = document.getElementsByTagName('a'); var i; for (i = 0; i < x.length; i++) { x[i].target = '_self'; }")
            
        # add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': self._tmp_folder + '/downloads'}}
        command_result = driver.execute("send_command", params)
        print("response from browser:")
        for key in command_result:
            print("result:" + key + ":" + str(command_result[key]))
        ###

        driver.get(url)
        
        # buttons = driver.find_elements_by_css_selector("button")
        # for button in buttons:
        #     # print(button.text.strip())
        #     if button.text.strip() == 'Export CSV':
        #         print(button.text.strip())
        #         button.click()
        
        for title, button_xpath in button_xpath_map.items():
            print(title)
            print(button_xpath)
            driver.find_element_by_xpath(button_xpath).click()
            filesrc = os.path.join(self._tmp_folder, 'downloads', 'raw_data.csv')
            filedest = os.path.join(self._tmp_folder, 'downloads', title + '.csv')
            while not os.path.exists(filesrc):
                time.sleep(1)
            os.rename(filesrc, filedest)
            # page_source = driver.page_source
        driver.quit()
        return page_source

    def close(self):
        # Remove specific tmp dir of this "run"
        shutil.rmtree(self._tmp_folder)


 