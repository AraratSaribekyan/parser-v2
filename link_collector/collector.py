from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import MoveTargetOutOfBoundsException

import os
import time
import json
import logging
import subprocess
import multiprocessing
import shutil

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
DRIVER_PATH = "/datas/ararat/parse_zalando/chromedriver"

ATTRIBUTES_FILE = "/datas/ararat/parse_zalando/attributes_links.json"
LOGGING_FOLDER = "/datas/ararat/parse_zalando/logs"

VPN_FOLDER = "/datas/ararat/parse_zalando/vpn"

N_PROCESSES = 5
MAX_PAGES = 20
MAX_RETRIES = 5

VPN_NUMBER = 0

logging.basicConfig(filename=f"{LOGGING_FOLDER}/_base.log", filemode='w', format='%(levelname)s : %(message)s', encoding='utf-8', level=logging.INFO)

options = wd.ChromeOptions()
options.add_argument(f"user-agent={USER_AGENT}")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

class NoPageException(Exception):
    pass
class OtherException(Exception):
    pass
class VpnException(Exception):
    pass
class ConnectionException(Exception):
    pass


def file_writer(file_path, queue):
    file = open(file_path, "a")
    while True:
        data = queue.get()
        if data is None:
            break
        file.write(data)
    file.close()


def get_img_srcs_by_urls(urls, logger, queue, attribute):
    cur_proc = multiprocessing.current_process().name
    logger.info(f"======================= {cur_proc} START ==========================")
    driver = None
    try:
        driver = wd.Chrome(executable_path=DRIVER_PATH, options=options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 5)

        for url in urls:
            try:

                attemps = 1
                while True:
                    try:
                        if attemps > MAX_RETRIES:
                            raise NoPageException(f"Can't open page {url} in process {cur_proc}")
                        driver.get(url=url)
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    except TimeoutError:
                        logger.warning(f"Retry to load page {url} in process {cur_proc}")
                        attemps += 1
                        continue
                    except Exception as ex:
                        raise OtherException(f"Can't load pages {url} in process {cur_proc}. Error: {ex}")
                    else:
                        break

                color_button = driver.find_elements_by_xpath("//li[@class = 'pl0w2g _5qdMrS _2ZBgf']//button")
                if len(color_button) != 0:
                    color_button[0].click()
                
                color_as = driver.find_elements_by_xpath("//li[@class = 'pl0w2g _5qdMrS _2ZBgf']//div//a")
                color_hrefs = [i.get_attribute('href') for i in color_as]

                imgs_before = driver.find_elements_by_xpath(f"//li[@class='LiPgRT DlJ4rT S3xARh']//div//div//div//img")
                imgs = driver.find_elements_by_xpath(f"//li[@class = 'LiPgRT DlJ4rT Zhr-fS']//div//button//div//div//img")
                actions = ActionChains(driver)
                actions.w3c_actions.pointer_action._duration = 0
                if len(imgs)>=8:
                    i=6
                else:
                    i=-1
                while True:
                    try:
                        imgs_after = driver.find_elements_by_xpath(f"// li[@class='LiPgRT DlJ4rT S3xARh']//div//div//div//img")
                        if len(imgs_after) == len(imgs_before) and len(imgs_before) < len(imgs):
                            actions.move_to_element(imgs[i]).perform()
                            i-=1
                        else:
                            break
                    except IndexError as ind_ex:
                        logger.warning(f"Could not load all images when hovering in page {url} of process {cur_proc}")
                        break
                    except Exception as ex:
                        raise OtherException(f"Exception occured on page {url} in process {cur_proc}: {ex}")

                imgs_after = driver.find_elements_by_xpath(f"// li[@class='LiPgRT DlJ4rT S3xARh']//div//div//div//img")
                queue.put(imgs_after[-1].get_attribute('src'))
                if len(imgs_after) >= 2:
                    queue.put(imgs_after[-2].get_attribute('src'))
                
                if attribute != "pattern":
                    for href in color_hrefs:
                        driver.get(url=href)
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                        imgs_before = driver.find_elements_by_xpath(f"//li[@class='LiPgRT DlJ4rT S3xARh']//div//div//div//img")

                        imgs = driver.find_elements_by_xpath(f"//li[@class = 'LiPgRT DlJ4rT Zhr-fS']//div//button//div//div//img")
                        actions = ActionChains(driver)
                        actions.w3c_actions.pointer_action._duration = 0

                        if len(imgs) >= 8:
                            i = 6
                        else:
                            i = -1
                        while True:
                            try:
                                imgs_after = driver.find_elements_by_xpath(f"// li[@class='LiPgRT DlJ4rT S3xARh']//div//div//div//img")
                                if len(imgs_after) == len(imgs_before) and len(imgs_before) < len(imgs):
                                    actions.move_to_element(imgs[i]).perform()
                                    i-=1
                                else:
                                    break
                            except IndexError as ind_ex:
                                logger.warning(f"Could not load all images when hovering in page {href} of process {cur_proc}")
                                break
                            except Exception as ex:
                                raise OtherException(f"Exception occured on page {href} in process {cur_proc}: {ex}")

                            
                        imgs_after = driver.find_elements_by_xpath(f"// li[@class='LiPgRT DlJ4rT S3xARh']//div//div//div//img")
                        queue.put(imgs_after[-1].get_attribute('src'))
                        if len(imgs_after) >= 2:
                            queue.put(imgs_after[-2].get_attribute('src'))

            except TimeoutError as timeout:
                logger.error(f"TimeOut error occured in {cur_proc} with page {url}")
                continue
            except NoPageException as nopg:
                logger.warning(nopg) 
                continue
            except OtherException as other:
                logger.error(other)
                continue

    except Exception as ex:
        logger.error(f"Soomething went wrong with process {cur_proc}")

    finally:
        if driver is not None:
            driver.quit()
        logger.info(f"======================= {cur_proc} END  ==========================")


def get_pages_by_url(url, logger, file, attribute):
    driver = None
    try:
        page=1
        driver = wd.Chrome(executable_path=DRIVER_PATH, options=options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 5)
        driver.get(url=url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(1)
        while True:

            logger.info(f"\n\n==================== PAGE {page} START ==================\n")
            attemp = 1
            seconds = 1
            global_attemps = 1
            while True:
                print("HELLO")
                if global_attemps > 5*MAX_RETRIES:
                    raise ConnectionException(f"Something wrong went on page {page} of url {url}. Stopping the process")
                if attemp > MAX_RETRIES:
                    logger.warning("Some troubles with connection, try to turn on vpn")
                    try:
                        subprocess.run(["sudo", "killall", "openvpn"])
                        subprocess.Popen(["sudo", "openvpn", f"{VPN_FOLDER}/{VPN_NUMBER}.ovpn"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
                        time.sleep(5)
                    except:
                        raise VpnException(f"Couldn't run VPN on page {page} of url {url}. Stopping the process")
                    else:
                        VPN_NUMBER = (VPN_NUMBER+1)%5
                        logger.info(f"VPN has been turned on with {VPN_NUMBER}")
                        seconds = 1
                        attemp = 1
                        continue
                try:
                    url_divs = driver.find_elements_by_xpath("//div[@class = '_5qdMrS w8MdNG cYylcv BaerYO _75qWlu iOzucJ JT3_zV _Qe9k6']//div[@class = '']")
                    assert len(url_divs) != 0
                except Exception as ex:
                    driver.get(url=url)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    logger.warning(f"Attemp to reload page {page}")
                    time.sleep(seconds)
                    attemp += 1
                    seconds += 1
                    global_attemps += 1
                    continue
                else:
                    break

            all_urls = [i.find_element_by_xpath(".//article//a").get_attribute("href") for i in url_divs]
            print(len(all_urls))
            url_dict = {}
            for proc_num in range(N_PROCESSES):
                url_dict[f"urls{proc_num}"] = [all_urls[i] for i in range(len(all_urls)) if i%N_PROCESSES==proc_num]
            
            queue = multiprocessing.Queue()
            writer_process = multiprocessing.Process(target=file_writer, args=(f"links/{file}", queue, ))
            writer_process.start()

            processes = []
            for urls in url_dict:
                process = multiprocessing.Process(target=get_img_srcs_by_urls, args=(url_dict[urls], logger, queue, attribute))
                process.start()
                processes.append(process)
            for process in processes:
                process.join()
            queue.put(None)
            writer_process.join()

            del url_divs
            del all_urls
            del url_dict
            del processes

            logger.info(f"\n==================== PAGE {page} END ==================\n\n")

            next_button = driver.find_elements_by_xpath("//a[@title = 'next page']")
            if len(next_button)==0:
                break
            else:
                url = next_button[0].get_attribute('href')
                driver.get(url = url)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                page += 1
                if page > MAX_PAGES:
                    logger.info("Exceeded max page size. ")
                    break
                time.sleep(5)

    
    except Exception as ex:
        logger.error(ex) 

    finally:
        if driver is not None:
            driver.quit()


def main():
    with open("/datas/ararat/parse_zalando/attributes_links.json", "r") as fd:
        attributes_dict = json.load(fd)
    
    # print(attributes_dict)
    for category in attributes_dict:
        for attribute in attributes_dict[category]:
            for attribute_type in attributes_dict[category][attribute]:
                # print(attributes_dict[category][attribute][attribute_type])
                for url in attributes_dict[category][attribute][attribute_type]:

                    if attribute_type == "3/4":
                        file = f"{LOGGING_FOLDER}/{category}_{attribute}_3-4"
                    else:
                        file = f"{LOGGING_FOLDER}/{category}_{attribute}_{attribute_type}"
                    logger = logging.getLogger()
                    logger.setLevel(logging.INFO)
                    file_handler = logging.FileHandler(f"{file}.log", mode="a")
                    file_handler.setLevel(logging.INFO)
                    formatter = logging.Formatter('%(levelname)s : %(message)s')
                    file_handler.setFormatter(formatter)
                    logger.addHandler(file_handler)

                    logger.info(f"START {category} -- {attribute} -- {attribute_type} for {url}")
                    get_pages_by_url(url, logger, f"{file}.txt", attribute)
                    logger.info(f"FINISH {category} -- {attribute} -- {attribute_type} for {url}\n\n")

                    logger.removeHandler(file_handler)
                    file_handler.close()

main()