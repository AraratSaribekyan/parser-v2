from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import MoveTargetOutOfBoundsException

import os
import time
import threading

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
DRIVER_PATH = "/home/anubis/Desktop/parser v2/chromedriver"
N_PROCESSES = 10
HOVER_SCRIPT = "var evObj = document.createEvent('MouseEvents');" \
              "evObj.initMouseEvent('mouseover', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);" \
              "arguments[0].dispatchEvent(evObj);"

options = wd.ChromeOptions()
options.add_argument(f"user-agent={USER_AGENT}")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

def get_img_srcs_by_urls(urls):
    print(f"======================= {threading.get_ident()} START ==========================")
    driver = None
    try:
        for url in urls:
            try:
                driver = wd.Chrome(executable_path=DRIVER_PATH, options=options)
                driver.maximize_window()
                wait = WebDriverWait(driver, 5)
                driver.get(url=url)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

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
                        print(f"IMGS BEFORE = {len(imgs_before)} \nIMGS AFTER = {len(imgs_after)} \nIMAGES = {len(imgs)}")
                        print(ind_ex)
                        break
                    except MoveTargetOutOfBoundsException as ex:
                        print(f"IMGS BEFORE = {len(imgs_before)} \nIMGS AFTER = {len(imgs_after)} \nIMAGES = {len(imgs)}")
                        btn = driver.find_elements_by_xpath("//button[@class = 'iljErk r9BRio Md_Vex NN8L-8 heWLCX LyRfpJ Vn-7c- _5Yd-hZ MMd_43 XfNx0j iljErk r9BRio Md_Vex NN8L-8 heWLCX LyRfpJ Vn-7c- _5Yd-hZ em2cO_ dSpxXG k9D41m DpImHu H4R7ov']")
                        print(btn)
                    except Exception as ex:
                        print(ex)

                imgs_after = driver.find_elements_by_xpath(f"// li[@class='LiPgRT DlJ4rT S3xARh']//div//div//div//img")
                print(imgs_after[-1].get_attribute('src'))
                if len(imgs_after) >= 2:
                    print(imgs_after[-2].get_attribute('src'))

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
                            print(
                                f"IMGS BEFORE = {len(imgs_before)} \nIMGS AFTER = {len(imgs_after)} \nIMAGES = {len(imgs)}")
                            print(ind_ex)
                            break
                        except MoveTargetOutOfBoundsException as ex:
                            print(f"IMGS BEFORE = {len(imgs_before)} \nIMGS AFTER = {len(imgs_after)} \nIMAGES = {len(imgs)}")
                            btn = driver.find_elements_by_xpath("//button[@class = 'iljErk r9BRio Md_Vex NN8L-8 heWLCX LyRfpJ Vn-7c- _5Yd-hZ MMd_43 XfNx0j iljErk r9BRio Md_Vex NN8L-8 heWLCX LyRfpJ Vn-7c- _5Yd-hZ em2cO_ dSpxXG k9D41m DpImHu H4R7ov']")
                            print(btn)
                        except Exception as ex:
                            print(ex)
                    imgs_after = driver.find_elements_by_xpath(f"// li[@class='LiPgRT DlJ4rT S3xARh']//div//div//div//img")
                    print(imgs_after[-1].get_attribute('src'))
                    if len(imgs_after) >= 2:
                        print(imgs_after[-2].get_attribute('src'))
            except Exception as ex:
                raise ex

    except Exception as ex:
        print(ex)
    finally:
        if driver is not None:
            driver.quit()
        print(f"======================= {threading.get_ident()} END  ==========================")


def get_page_by_url(url):
    driver = None
    try:
        driver = wd.Chrome(executable_path=DRIVER_PATH, options=options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 5)
        driver.get(url=url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    except Exception as ex:
        print(ex)
    else:
        url_divs = driver.find_elements_by_xpath("//div[@class = '_5qdMrS w8MdNG cYylcv BaerYO _75qWlu iOzucJ JT3_zV _Qe9k6']//div[@class = '']")
        all_urls = [i.find_element_by_xpath(".//article//a").get_attribute("href") for i in url_divs]
        url_dict = {}
        for proc_num in range(N_PROCESSES):
            url_dict[f"urls{proc_num}"] = [all_urls[i] for i in range(len(all_urls)) if i%N_PROCESSES==proc_num]
        threads = []
        for urls in url_dict:
            time.sleep(2)
            thread = threading.Thread(target=get_img_srcs_by_urls, args=(url_dict[urls], ))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        # get_img_srcs_by_urls(all_urls)
    finally:
        if driver is not None:
            driver.quit()


def main():
    get_page_by_url("https://www.zalando.co.uk/womens-clothing-tops-tops-sale/?camp=uk_eoss_wave_2&sale=true&sleeves=sleeveless")

main()