import os
import time
from typing import Optional

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from logger import AppLogger

class BrowserClient:
    """
    Selenium based Chrome browser driver.
    
    BrowserClient class is wrapping login process.
    """

    def __init__(self):
        load_dotenv()
        self.user_id = os.getenv("BIGKINDS_ID")
        self.user_pw = os.getenv("BIGKINDS_PW")
        self.logger = AppLogger("[BrowserClient]")

        if not self.user_id or not self.user_pw:
            msg = "BIGKINDS_ID or BIGKINDS_PW is not configurated in `.env`."
            self.logger.critical(msg)
            raise ValueError(msg)

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
        self.logger.debug("Browser driver initialized.")

    def login(self) -> None:
        """
        Login Bigkidns website with id & password with Selenium Browser.
        """
        
        self.logger.info("Login process started.")
        
        # 1. URL Access
        try:
            self.logger.debug("Accessing URL: https://www.bigkinds.or.kr/")
            self.driver.get("https://www.bigkinds.or.kr/")
            time.sleep(2)
            self.logger.info("URL access succeeded.")
        except Exception:
            self.logger.exception("URL access failed.")
            return
        
        # 2. Top Membership Button
        try:
            self.logger.debug("Locating 'topMembership' button.")
            top_membership_btn = self.driver.find_element(By.CLASS_NAME, "topMembership")
            top_membership_btn.click()
            time.sleep(1)
            self.logger.debug("Clicked 'topMembership' button.")
        except Exception:
            self.logger.exception("Failed to click 'topMembership' button.")
            return
        
        # 3. Login Modal Button
        try:
            self.logger.debug("Locating login modal trigger.")
            login_modal_btn = self.driver.find_element(By.CSS_SELECTOR, 'a[data-target="#login-modal"]')
            login_modal_btn.click()
            time.sleep(1)
            self.logger.debug("Opened login modal.")
        except Exception:
            self.logger.exception("Failed to open login modal.")
            return
          
        # 4. Input Credentials & Submit
        try:
            self.logger.debug("Inputting user credentials.")
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
                self.logger.error("Login modal still visible. Login failed (Incorrect ID/PW or Captcha).")
                return
            else:
                self.logger.info("Login modal closed. Login assumed successful.")
        except Exception:
            self.logger.exception("Error occurred during credential input or login click.")
            return

        self.logger.info("Login process completed successfully.")

    def close(self):
        self.driver.quit()
        self.logger.info("Browser driver closed.")