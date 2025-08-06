import os 
import sys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Function to normalize the set number

def normalize_set_number(set_number):
    if '-' in set_number:
        print(f"Processing set number '{set_number}'.")
        return set_number
    else:
        normalized_set_number = f"{set_number}-1"
        print(f"Processing set number '{normalized_set_number}'.")
        return normalized_set_number
    
# Function to load Instabrick credentials from .env file

def load_instabrick_environment():
    
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

    return USERNAME, PASSWORD

# Function to initialize WebDriver (headless Chrome)

def init_webdriver():

    options = Options()
    options.add_argument("--headless")

    try:
        # Attempt to initialize the driver using an existing ChromeDriver installation
        driver = webdriver.Chrome(options=options)
        print("Using existing ChromeDriver installation.")

    except WebDriverException:
        # If ChromeDriver is not found or fails, install it using webdriver_manager
        print("ChromeDriver not found. Installing via webdriver_manager.")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    return driver

# Function to log into Instabrick

def login_instabrick(driver, USERNAME, PASSWORD):

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
        wait.until(EC.presence_of_element_located((By.ID, "top-menu")))

    except TimeoutException:
        # If the dashboard doesn't load, assume login failed
        print("Error: Instabrick login failed. Please check your username and password.")
        sys.exit(1)

# Function to navigate to the Sets page

def navigate_to_sets_page(driver):

    sets_url = "https://app.instabrick.org/sets"
    driver.get(sets_url)

    # Wait for the Sets table to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "sets_list_table_filter"))
    )

# Function to search for a set on the Sets page and return the first row

def search_for_set(driver, set_number):

    # Locate the Search field
    filter_input = driver.find_element(By.CSS_SELECTOR, '#sets_list_table_filter input[type="search"]')

    # Clear the Search field; enter the set number; and simulate hitting the Enter key
    filter_input.clear()
    filter_input.send_keys(set_number)
    filter_input.send_keys(Keys.RETURN)

    # Wait for the "Processing..." message to disappear
    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '#sets_list_table_processing'))
    )

    # Wait for at least one row to appear in the Sets table
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#sets_list_table tbody tr'))
    )

    # Locate all rows in the Sets table
    rows = driver.find_elements(By.CSS_SELECTOR, "#sets_list_table tbody tr")
    
    # Check the number of rows
    if len(rows) == 0 or (len(rows) == 1 and "No matching records found" in rows[0].text):
        print(f"No matching records found for set number: {set_number}")
        return None
    elif len(rows) > 1:
        print(f"Multiple results found after filtering ({len(rows)}). Proceeding with the first one.")

    # Return the first row
    return rows[0]

# Function to navigate to the Inventory page

def navigate_to_inventory_page(driver):
    
    inventory_url = "https://app.instabrick.org/inventory"
    driver.get(inventory_url)

    # Wait for the Inventory page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body.pace-done"))
    )

# Function to save page source to file (for debugging)

def save_page_source(driver):

    with open("page_source.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    print("Page source saved to page_source.html")