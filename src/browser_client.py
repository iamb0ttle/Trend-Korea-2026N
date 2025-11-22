import os
import time
from typing import Optional

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


class BrowserClient:
    """
    Selenium based Chrome browser driver.
    
    BrowserClient class is wrapping login process.
    """

    def __init__(self):
        load_dotenv()
        self.user_id = os.getenv("BIGKINDS_ID")
        self.user_pw = os.getenv("BIGKINDS_PW")

        if not self.user_id or not self.user_pw:
            raise ValueError("BIGKINDS_ID or BIGKINDS_PW is not configurated in `.env`.")

        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        self.driver.set_window_size(2560, 1440)

    def login(self, screening: bool = False) -> None:
        """
        Login Bigkidns website with id & password with Selenium Browser.

        Args:
          screening (bool): If or not about screenshot capture while trying login process

        Returns:
          None

        """
        
        print("[BrowserClient] Login trying...")
        
        try:
          print("[BrowserClient] Url access trying ...")
          self.driver.get("https://www.bigkinds.or.kr/")
          time.sleep(2)
          print("[BrowserClient] Url access successed.")
        except Exception as e:
          print("[BrowserClient] Url access failed.", e)
          return
        
        try:
          print("[BrowserClient] Trying find element and click.")
          top_membership_btn = self.driver.find_element(By.CLASS_NAME, "topMembership")
          top_membership_btn.click()
          time.sleep(1)
          print("[BrowserClient] Find element and click successfully.")
        except Exception as e:
          print("[BrowserClient] Find element and click failed.", e)
          return
        
        try:
          print("[BrowserClient] Trying find element and click.")
          login_modal_btn = self.driver.find_element(By.CSS_SELECTOR, 'a[data-target="#login-modal"]')
          login_modal_btn.click()
          time.sleep(1)
          print("[BrowserClient] Find element and click successfully.")
        except Exception as e:
          print("[BrowserClient] Find element and click failed.", e)
          return
          
        try:
          print("[BrowserClient] Trying find element and send ID & password.")
          id_input = self.driver.find_element(By.ID, "login-user-id")
          pw_input = self.driver.find_element(By.ID, "login-user-password")
        
          id_input.send_keys(self.user_id)
          time.sleep(1)
          pw_input.send_keys(self.user_pw)
          
          login_btn = self.driver.find_element(By.ID, "login-btn")
          login_btn.click()
          
          time.sleep(3)
          
          # check login modal closed  
          modals = self.driver.find_elements(
              By.CSS_SELECTOR, ".modal.modal-login.modal-click-close.in"
          )

          if modals:
              print("[BrowserClient] Login modal still visible → login failed.")
              return
          else:
              print("[BrowserClient] Login modal not found → login success.")
              print("[BrowserClient] Find element and send ID & password successfully.")
          
          print("[BrowserClient] Find element and send ID & password successfully.")
        except Exception as e:
          print("[BrowserClient] Find element and send ID & password failed.", e)
          return
        
        if screening == True:
          try:
            print("[BrowserClient] Try login status checking & saving screenshot")
            top_membership_btn = self.driver.find_element(By.CLASS_NAME, "topMembership")
            top_membership_btn.click()
            time.sleep(1)
            
            filename = f"success_login_{time.strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(f"../screenshoots/{filename}")
            print("[BrowserClient] Login status checking & saving screenshot processed successfully.")
          except Exception as e:
            print("[BrowserClient] Login status checking failed.", e)
            return
        
        print("[BrowserClient] Login completed successfully.")

    def close(self):
        self.driver.quit()
