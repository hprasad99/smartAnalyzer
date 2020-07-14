import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.environ["PATH"] += os.pathsep + os.path.join(BASE_DIR,'/gecko')
os.environ["PATH"] += os.pathsep + os.path.join(BASE_DIR,'/chrome')
os.environ["PATH"] += os.pathsep + os.path.join(BASE_DIR,'/edge')

from django.test import TestCase,LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class AccountTestCase(LiveServerTestCase):
    def test_login(self):
        driver = webdriver.Firefox(executable_path=r'D:/Setup/geckodriver.exe')
        driver.get("http://127.0.0.1:8000/login/")
        try:
            username = driver.find_element_by_id("id_username")
            password = driver.find_element_by_id("id_password")
            submit = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID,"logger")))

            username.send_keys('himanshujprasad')
            password.send_keys('testing321')   
            submit.click()
        except e:
            print("TestedOK!")
        finally:
            driver.close()
    
    def test_signup(self):
        driver = webdriver.Firefox(executable_path=r'D:/Setup/geckodriver.exe')
        driver.get("http://127.0.0.1:8000/register/")

        try:
            username = driver.find_element_by_id("id_username")
            emailid = driver.find_element_by_id("id_email")
            passkey1 = driver.find_element_by_id("id_password1")
            passkey2 = driver.find_element_by_id("id_password2")

            signup = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID,"signup")))

            username.send_keys('Saurabh269')
            emailid.send_keys('saurabhsutar269@gmail.com')
            passkey1.send_keys('testing321')
            passkey2.send_keys('testing321')
            signup.click()
        except e:
            print("2nd Test Case: TestedOK!")
        finally:
            driver.close()