#! /usr/bin/python3
# James Loye Colley
# 22MAY2018
# https://www.roboshout.com

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys
import random
import re

# search for a given website by a string of text using a different proxy each time
# page indexes are printed to the console (including final index of the site
# once the site is found, a random link on the site will be clicked

class ProxyCrawler:
    def __init__(self, URL, keyword, socket_list=[]):
        self.__scrape_socket()
        self.keyword = keyword
        self.url = URL

    # get a list of sockets from https://www.sslproxies.org
    def __scrape_socket(self):
        string_builder = ""
        browser1 = webdriver.Firefox()
        browser1.get("https://www.sslproxies.org/")
        time.sleep(2)
        td_tags = browser1.find_elements_by_tag_name('td')
        for tag in td_tags:
            string_builder += tag.text + " "
        browser1.quit()
        self.socket_list = re.findall("\d+.\d+.\d+.\d+\s+\d+", string_builder)

    # search with the given proxy. If an exception occurs, the loop continues and the next proxy is used
    def start_search(self):
        for socket in self.socket_list:
            temp_socket = socket.split()
            PROXY_HOST = temp_socket[0]
            PROXY_PORT = temp_socket[1]
            fp = webdriver.FirefoxProfile()
            fp.set_preference("network.proxy.type", 1)
            fp.set_preference("network.proxy.http", PROXY_HOST)
            fp.set_preference("network.proxy.http_port", int(PROXY_PORT))
            fp.set_preference("network.proxy.ssl", PROXY_HOST)
            fp.set_preference("network.proxy.ssl_port", int(PROXY_PORT))
            fp.set_preference("general.useragent.override", "whater_useragent")
            fp.update_preferences()
            browser2 = webdriver.Firefox(firefox_profile=fp)
            try:
                browser2.get('https://www.bing.com/')
                assert "Bing" in browser2.title
            except:
                print("retrying Bing with different socket")
                browser2.quit()
                continue
            print("\n--------------------------------------------")
            print("using socket: " + PROXY_HOST + ":" + PROXY_PORT)
            print("searching for keyword(s):   " + self.keyword)
            search_box = browser2.find_element_by_name("q")
            sub_button = browser2.find_element_by_name("go")
            time.sleep(random.randint(10, 20) + random.random())
            search_box.send_keys(self.keyword)
            time.sleep(random.randint(10, 20) + random.random())
            sub_button.send_keys(Keys.RETURN)
            time.sleep(random.randint(10, 20) + random.random())
            page_index = 0
            extractor = re.sub(r".*.//"," ", self.url)
            if "www." in extractor:
                domain = extractor[5:]
            else:
                domain = extractor
            while  domain not in browser2.current_url:
                page_index += 1
                page_links = browser2.find_elements_by_xpath("//a[@href]")
                for link in page_links:
                    if domain in link.get_attribute("href"):
                        time.sleep(1)
                        link.click()
                        print("Found " + domain + " at page index " + str(page_index))
                        break
                if not domain in browser2.current_url:
                    try:
                        print("current index:   " + str(page_index))
                        time.sleep(random.randint(5, 10) + random.random())
                        browser2.find_element_by_link_text(str(page_index + 1)).click()
                    except:
                        print("Exception occurred: trying next socket")
            time.sleep(random.randint(30, 60) + random.random())
            target_page_links = browser2.find_elements_by_xpath("//a[@href]")
            random_page_num = random.randint(0, len(target_page_links))
            time.sleep(random.randint(30, 60) + random.random())
            target_link = target_page_links[random_page_num]
            try:
                target_link.click()
            except:
                print("Invalid target link... retrying with next socket")
            time.sleep(random.randint(10, 15) + random.random())
            print("current page:   " + browser2.current_url)
            time.sleep(random.randint(30, 60) + random.random())
            browser2.quit()


if __name__ == "__main__":
    print("\nPlease enter the FULLY QUALIFIED URL that you want to crawl for...")
    url = input("example: https://www.mysite.com\n\n")
    if "http" not in url or "https" not in url:
        print("invalid URL... exiting")
        sys.exit()
    keywd = input("\nWhat keyword(s) would you like to search for?\n\n")
    if len(keywd) < 1:
        print("Please enter a keyword... exiting")
        sys.exit()
    bot = ProxyCrawler(url, keywd)
    while True:
        bot.start_search()