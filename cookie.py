import random
import time
import pickle
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (TimeoutException, WebDriverException, 
                                    NoAlertPresentException, UnexpectedAlertPresentException)


class WebSession:
    
    def __init__(self, link, title=None, headless=False):
        '''INSERT CLASS DOC STRING
        ####Probaly Need to make a Order Page object, given how many of the methods below
        Are Strictly for use while on Order Page'''
        self.link = link
        self.title = title 
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument('--log-level=1')
        options.add_argument("--mute-audio")
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get(self.link)
        #~ assert self.title in self.driver.title

    def get_html(self):
        '''returns tag parsed html of current page.'''
        raw_html = self.driver.page_source
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup

    def keyboard(self, *args, pauses=None, pause_length=0.5):
        '''takes a series of keyboard arguments, and performs them.
        can take list of args to pause after(list should contain index of arg)
        e.g. *args=Keys.DOWN, Keys.UP  to pause for Keys.UP, pauses=[1].'''
        if not pauses:
            pauses = []
        self.actions = ActionChains(self.driver)
        for i, arg in enumerate(args):
            self.actions.send_keys(arg)
            if i in pauses:
                time.sleep(pause_length)
        self.actions.perform()

    def check_element(self, element, element_type=By.XPATH, timeout=60, 
                    visibility='visible', clickable=True, critical=True):
        '''checks if an element has met certain conditions yet, continues
        to check until timeout parameter(seconds) has passed or and unexpected
        alert is present on the page(e.g. error alert). Function returns True
        if conditions met, else False.'''
        try:
            if visibility == 'visible':
                element_visibility = EC.visibility_of_element_located((element_type, element))
            elif visibility == 'invisible':
                element_visibility = EC.invisibility_of_element_located((element_type, element))
                
            WebDriverWait(self.driver, timeout).until(element_visibility)
            
            if clickable:
                element_clickable = EC.element_to_be_clickable((element_type, element))
                WebDriverWait(self.driver, timeout).until(element_clickable)
            return True

        except (WebDriverException, TimeoutException, UnexpectedAlertPresentException) as e:
            if critical:
                logger.exception(e)
            return False

    def click_xelement(self, element, clicks=1, timeout=60, critical=True):
        '''checks if element meets specified conditions(see self.check_element()).
        Then when conditions are approriate clicks the element the specified number 
        of times(clicks).'''
        func_timeout = time.time() + timeout
        while True:
            try:
                self.check_element(element, timeout=timeout, critical=critical)
                for _ in range(clicks):
                    x = self.driver.find_element_by_xpath(element).click()
                return True

            except (WebDriverException, TimeoutException, UnexpectedAlertPresentException) as e:
                if time.time() > func_timeout:
                    if critical:
                        logger.exception(e)
                    return False
                else:
                    continue

    def switch_frame(self, iframe):
        '''switch page to input iframe.'''
        self.check_element(iframe, clickable=False)
        iframe = self.driver.find_element_by_xpath(iframe)
        self.driver.switch_to.frame(iframe)

    def alert_handling(self, iframe):
        '''attempts to switch to displayed alert, pull alert
        message and then accept the alert and switch back to default 
        context/iframe (iframe=None to just switch to default context).
        Returns alert_text if alert found, else returns None.'''
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if not alert_text:
                alert_text = alert.getText()
            alert.accept()
            self.driver.switch_to_default_content()
            if iframe:
                self.switch_frame(iframe)
            return alert_text

        except NoAlertPresentException:
            return None
    
    def close_browser(self):
        '''logs out of site, and closes browser'''
        self.driver.quit() 

if __name__ == '__main__':
    pizzahut = WebSession('https://www.pizzahut.com/index.php#/home')
    pizzahut.click_xelement('//*[@id="ph-sign-in"]/span')
    pizzahut.click_xelement('//*[@id="email_signIn"]')
    pizzahut.keyboard('insert email')
    pizzahut.click_xelement('//*[@id="password_signIn"]')
    pizzahut.keyboard('inser password')
    pizzahut.click_xelement('//*[@id="ph-login"]')
    time.sleep(5)
    pizzahut.click_xelement('//*[@id="lg-nav-menu"]/span')
    time.sleep(1)
    pizzahut.click_xelement('//*[@id="lg-nav-desserts"]')
    pizzahut.click_xelement('//*[@id="tile-ultimate-hersheys-chocolate-chip-cookie-"]/div/div[2]/div[3]/div[2]/div[1]/div/a[1]/span')
    pizzahut.click_xelement('//*[@id="ph-localization-id"]/div[1]/div[2]/div/label/span[1]')
    pizzahut.click_xelement('//*[@id="ph-localization-id"]/div[3]/div[2]/div/div/div[1]/div/div[2]/button')
    pizzahut.click_xelement('//*[@id="ph-localization-id"]/div[3]/div[3]/div[2]/div/div[1]/div/div/div/div[3]/a/span')
    pizzahut.click_xelement('//*[@id="lg-nav-menu"]/span')
    pizzahut.click_xelement('//*[@id="ato-ultimate-hersheys-chocolate-chip-cookie-"]')
    pizzahut.click_xelement('//*[@id="cart-quantity-icon"]')
    pizzahut.click_xelement('//*[@id="checkout-top-os"]')
    pizzahut.click_xelement('/html/body/div[2]/div/div/div/div/div[1]/div[2]/div/form/div[5]/div[2]/button')
    pizzahut.click_xelement('/html/body/div[2]/div/div/div/div/div[1]/div[2]/div/div[2]/div[5]/span/label/input')
    pizzahut.click_xelement('/html/body/div[2]/div/div/div/div/div[1]/div[2]/div/div[3]/div/button')
