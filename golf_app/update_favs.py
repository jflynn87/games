import os
from golf_app.models import Tournament
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from django.db.models import Min, Q, Count, Sum, Max
from requests import get
from selenium import webdriver
import urllib
from selenium.webdriver import Chrome, ChromeOptions
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec





class UpdateFavs(object):

    def __init__(self, tournament=None):
        if tournament == None:
            Tournament.objects.get(current=True)
        else:
            pass
            
        self.url = "https://www.pgatour.com/"


    def scrape(self):
        options = ChromeOptions()
        #options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--window-size=1920,1080")
        
        driver = Chrome(options=options)
        driver.get(self.url)

        run_dict = {}

        try:
            print ('scraping runkeeper')
            main_page = driver.current_window_handle
            login = driver.find_element_by_xpath('/html/body/div[10]/div[1]/div/div[1]/div[1]/div/div/div[5]/div/button[2]')
            
            login.click()
            print ('scrape logging in')
            for handle in driver.window_handles:
                print (handle)
                if handle != 'main page': 
                    login_page = handle

            driver.switch_to_window(login_page)
            time.sleep(5)
            
            try: 
                email_id = driver.find_element_by_xpath('//*[@id="com.fitnesskeeper.runkeeper.pro:id/login-a_email"]')
            except Exception:
                email_id = driver.find_element_by_name('a_email')                                        



            email_id.send_keys(os.environ.get('email_address'))


            password = email_id = driver.find_element_by_name('a_password')
            password.send_keys(os.environ.get('runkeeper_pwd'))
            time.sleep(5)

            try:
                sub_button = driver.find_element_by_id('com\.fitnesskeeper\.runkeeper\.pro\:id\/login-oneasics-login') 
            except Exception:
                sub_button = driver.find_element_by_xpath('//*[@id="com.fitnesskeeper.runkeeper.pro:id/login-oneasics-login"]')
            
            driver.execute_script("arguments[0].click()",sub_button)
            print ('scrape loggedg in')
            time.sleep(2)
            driver.switch_to.window(main_page)
            #driver.maximize_window()
        
            #try:
            #    wait = WebDriverWait(driver, 10)
            #    first = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="pageWrapper"]/div[2]/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/div[1]/div[1]/div[2]/ul')))
            #except Exception as e5:
            #    print (e5)
            time.sleep(30)
            try:
                first = driver.find_element_by_xpath('//*[@id="pageWrapper"]/div[2]/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/div[1]/div[1]/div[2]/ul')

            except Exception as e:
                print (e)
                try:
                    first = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div[1]/div/div[3]/div/div[2]/div[3]/div[1]/div[1]/div[2]')
                except Exception as e1:
                    print (e1)
                    first = driver.find_element_by_class_name('feedArrow.clickable')
                                                        
                                                    
            first.click()
            
            try:
                a_list = driver.find_element_by_id('ui-accordion-activityHistoryMenu-panel-0')
            except Exception:
                a_list = driver.find_element_by_xpath('//*[@id="activityHistoryMenu"]')
    
            lines = a_list.find_elements_by_tag_name('li')
            print ('before looping lines')

            for i, a in enumerate(lines):
                #time.sleep(5)
                if i >= 1:
                    a_list = driver.find_element_by_id('ui-accordion-activityHistoryMenu-panel-0')
                    a_list.find_elements_by_tag_name('li')[i].click()

                date = driver.find_element_by_class_name('micro-text.activitySubtitle')
                activity_list = driver.find_element_by_id('activityHistoryMenu')
                first_activity_div = activity_list.find_element_by_class_name('selected')
                first_activity = first_activity_div.find_element_by_tag_name('a')
                dist =  driver.find_element_by_id('totalDistance')
                duration = driver.find_element_by_id('totalDuration')
                cals = driver.find_element_by_id('totalCalories')

                if 'Running' in first_activity.text:
                    run_dict[date.text] = first_activity.text, dist.text.split('\n')[1], duration.text.split('\n')[1], cals.text.split('\n')[1]
                
        except Exception as e:
            print ('exception', e)

        finally:
            driver.quit()

        return run_dict


    def scrape_garmin(self):
        options = ChromeOptions()
        #options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--window-size=1920,1080")
        driver = Chrome(options=options)
        driver.get(self.url)

        run_dict = {}

        try:
            main_page = driver.current_window_handle
            
            login = driver.find_element_by_xpath('/html/body/div/div/div/header/nav/ul/li[4]/a/button')
            login.click()
            
            for handle in driver.window_handles:
                print (handle)
                if handle != 'main page': 
                    login_page = handle

            driver.switch_to_window(login_page)
            time.sleep(5)
            
            print ('before email')
            try:
                email_id = driver.find_element_by_xpath('//*[@id="com.fitnesskeeper.runkeeper.pro:id/login-a_email"]')
            except Exception as e:
                print ('email exception', e)                
                email_id = driver.find_element_by_id('input.username')
            
            print ('after email')
            email_id.send_keys(os.environ.get('email_address'))
            
            password = email_id = driver.find_element_by_id('#password')
            password.send_keys(os.environ.get('garmin_pwd'))
            time.sleep(5)
            sub_button = driver.find_element_by_id('login-btn-signin') 
            sub_button.click()
            #driver.execute_script("arguments[0].click()",sub_button)

            time.sleep(2)
            driver.switch_to.window(main_page)
            driver.maximize_window()
        
            first = driver.find_element_by_class_name('feedArrow')
                                                    
            first.click()
            a_list = driver.find_element_by_id('ui-accordion-activityHistoryMenu-panel-0')
            lines = a_list.find_elements_by_tag_name('li')
            

            for i, a in enumerate(lines):
                #time.sleep(5)
                if i >= 1:
                    a_list = driver.find_element_by_id('ui-accordion-activityHistoryMenu-panel-0')
                    a_list.find_elements_by_tag_name('li')[i].click()

                date = driver.find_element_by_class_name('micro-text.activitySubtitle')
                activity_list = driver.find_element_by_id('activityHistoryMenu')
                first_activity_div = activity_list.find_element_by_class_name('selected')
                first_activity = first_activity_div.find_element_by_tag_name('a')
                dist =  driver.find_element_by_id('totalDistance')
                duration = driver.find_element_by_id('totalDuration')
                cals = driver.find_element_by_id('totalCalories')

                if 'Running' in first_activity.text:
                    run_dict[date.text] = first_activity.text, dist.text.split('\n')[1], duration.text.split('\n')[1], cals.text.split('\n')[1]
                
        except Exception as e:
            print ('exception', e)

        finally:
            driver.quit()

        return run_dict





