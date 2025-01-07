from dotenv import load_dotenv
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Load environment variables from .env file

dotenv_path = os.path.join(os.path.dirname(__file__), "../../data/user_data/.env")

if not os.path.exists(dotenv_path):
    print(f"Error: The .env file was not found at {dotenv_path}.")
    print("Please create the .env file with your credentials in the specified directory.")
    sys.exit(1)  # Exit the script with an error code

load_dotenv(dotenv_path)

# Retrieve credentials from .env file

USERNAME = os.getenv("INSTABRICK_USERNAME")
PASSWORD = os.getenv("INSTABRICK_PASSWORD")

if not USERNAME or not PASSWORD:
    print("Error: Missing USERNAME or PASSWORD in the .env file.")
    sys.exit(1)

# Initialize WebDriver

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Instabrick login page

login_url = "https://app.instabrick.org/signin"

try:
    # Navigate to the login page
    driver.get(login_url)

    # Log into the website
    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.presence_of_element_located((By.ID, "loginemail")))
    password_input = driver.find_element(By.ID, "loginpassword")
    login_button = driver.find_element(By.ID, "sign_in")

    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    login_button.click()

    # Wait for a successful login indicator (the top menu element)

    try:
        wait.until(EC.presence_of_element_located((By.ID, "top-menu")))
        print("Instabrick login successful!")

    except TimeoutException:
        # If the dashboard doesn't load, assume login failed
        print("Error: Instabrick login failed. Please check your username and password.")
        sys.exit(1)

    # Continue with the rest of the script...


finally:
    driver.quit()