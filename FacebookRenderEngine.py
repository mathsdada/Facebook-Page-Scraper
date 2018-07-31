import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import selenium.common.exceptions as exceptions
import time


class RenderEngine:
    def __init__(self, username, password):
        self.__login_to_facebook(username, password)

    def __login_to_facebook(self, username, password):
        # chrome_driver = r"C:\Users\sushg\Desktop\Data\Projects\Python\FacebookScraper\chromedriver"
        chrome_driver = r"<replace me with chromedriver_path as mentioned in above example>"
        os.environ["webdriver.chrome.driver"] = chrome_driver
        self.__driver = webdriver.Chrome(chrome_driver)

        self.__driver.get("http://www.facebook.com")
        username_box = self.__driver.find_element_by_id('email')
        password_box = self.__driver.find_element_by_id('pass')
        login_box = self.__driver.find_element_by_id('loginbutton')
        # enter username
        username_box.send_keys(username)
        # enter password
        password_box.send_keys(password)
        # click login button
        login_box.click()

    def close_engine(self):
        self.__driver.quit()

    def render_web_page(self, link):
        self.__driver.get(link)
        html_source = self.__driver.page_source
        return html_source

    def render_facebook_page(self, link):
        self.__driver.get(link)
        body = self.__driver.find_element_by_css_selector('body')
        body.send_keys(Keys.END)
        time.sleep(2)
        html_source = self.__driver.page_source
        return html_source

    def render_get_username_from_user_id(self, user_id):
        link = "https://www.facebook.com/{}".format(user_id)
        self.__driver.get(link)
        return self.__driver.current_url

    def render_user_profile(self, username):
        link = "https://www.facebook.com/{}".format(username)
        self.__driver.get(link)
        return self.__driver.page_source

    def render_posts_of_page(self, page_title):
        page_link = "https://m.facebook.com/pg/{}/posts/".format(page_title)
        self.__driver.get(page_link)

        prev_num_posts = 0
        repeat_count = 0
        while repeat_count < 5:
            list_of_posts_tags = self.__driver.find_elements_by_class_name("_3w7e")
            cur_num_posts = len(list_of_posts_tags)
            if cur_num_posts == prev_num_posts:
                repeat_count += 1
            else:
                prev_num_posts = cur_num_posts
                repeat_count = 0
            body = self.__driver.find_element_by_css_selector('body')
            body.send_keys(Keys.END)
            time.sleep(1)
        html_source = self.__driver.page_source
        return html_source

    def render_like_link_of_post(self, like_link):
        if len(like_link) == 0:
            return ""
        like_link = like_link.replace("m.facebook.com", "www.facebook.com")
        self.__driver.get(like_link)
        while True:
            try:
                self.__driver.find_element_by_class_name("pam.uiBoxLightblue.uiMorePagerPrimary")
                more_buttons = WebDriverWait(self.__driver, 20).until(
                    ec.element_to_be_clickable((By.CLASS_NAME, "pam.uiBoxLightblue.uiMorePagerPrimary")))
            except exceptions.NoSuchElementException:
                break
            except exceptions.TimeoutException:
                break
            else:
                script = "window.scrollTo(0," + str(more_buttons.location_once_scrolled_into_view) + ")"
                self.__driver.execute_script(script)
                more_buttons.click()
                time.sleep(3)
        html_source = self.__driver.page_source
        return html_source

    def render_share_link_of_post(self, share_link):
        if len(share_link) == 0:
            return ""
        share_link = share_link.replace("m.facebook.com", "www.facebook.com")
        prev_num_of_friends = 0
        repeat_count = 0
        self.__driver.get(share_link)
        while repeat_count < 5:
            friends = self.__driver.find_elements_by_css_selector("div[class='_6a _5u5j _6b']")
            current_num_of_friends = len(friends)
            if prev_num_of_friends == current_num_of_friends:
                repeat_count += 1
            else:
                prev_num_of_friends = current_num_of_friends
                repeat_count = 1
            body = self.__driver.find_element_by_css_selector('body')
            body.send_keys(Keys.END)
            time.sleep(2)
        html_source = self.__driver.page_source
        return html_source

    def render_user_data(self, user_id, option):
        if option == "network":
            link = "https://www.facebook.com/{}/friends".format(user_id)
        elif option == "liked_pages":
            link = "https://www.facebook.com/{}/likes".format(user_id)
        else:
            return ""
        prev_user_network_size = 0
        repeat_count = 0
        self.__driver.get(link)
        while repeat_count < 5:
            friends = self.__driver.find_elements_by_css_selector("div[class='fsl fwb fcb']")
            curr_user_network_size = len(friends)
            if prev_user_network_size == curr_user_network_size:
                repeat_count += 1
            else:
                prev_user_network_size = curr_user_network_size
                repeat_count = 1
            body = self.__driver.find_element_by_css_selector('body')
            body.send_keys(Keys.END)
            time.sleep(2)
        html_source = self.__driver.page_source
        return html_source

    def render_post_comments(self, page_id, post_id):
        link = "https://m.facebook.com/{}/posts/{}".format(page_id, post_id)
        self.__driver.get(link)
        comment_blocks = self.__driver.find_elements_by_css_selector("div[class='_2a_i']")
        time.sleep(3)
        for comment_block in comment_blocks:
            try:
                reply_block = comment_block.find_element_by_css_selector("div[class='_2b1h async_elem'")
            except exceptions.NoSuchElementException:
                continue
            else:
                reply_button = reply_block.find_element_by_tag_name('a')
                reply_button.click()
        body = self.__driver.find_element_by_css_selector('body')
        body.send_keys(Keys.END)
        time.sleep(2)
        html_source = self.__driver.page_source
        return html_source
