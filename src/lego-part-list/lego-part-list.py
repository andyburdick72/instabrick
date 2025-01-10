import csv
import os 
import re
import sys
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Function to load Instabrick credentials from .env file

def load_environment():
    
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
        print("ChromeDriver not found. Installing via webdriver_manager...")
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

# Function to normalize the set number

def normalize_set_number(set_number):
    if '-' in set_number:
        print(f"Extracting part list for set number '{set_number}'.")
        return set_number
    else:
        normalized_set_number = f"{set_number}-1"
        print(f"Extracting part list for set number '{normalized_set_number}'.")
        return normalized_set_number
    
# Function to get the page source for the part list

def get_part_list_page(driver, set_number):

    sets_url = "https://app.instabrick.org/sets"
    driver.get(sets_url)

    # Wait for the Sets table to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "sets_list_table_filter"))
    )
    
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

    # Go to the first row of the Sets table and find the Set Info button
    first_row = rows[0]
    set_info_button = first_row.find_element(By.CSS_SELECTOR, "td .table_button_show_set")

    # Click the Set Info button and wait for the parts list to load
    set_info_button.click()
    time.sleep(2)

    # Get the initial row count
    rows = driver.find_elements(By.CSS_SELECTOR, '#sets_list_table tbody tr')
    
    # Locate the "Showing 1 to 25 of n entries" text
    info_element = driver.find_element(By.CSS_SELECTOR, '.dataTables_info')
    info_text = info_element.text
    
    # Extract the total number of entries using regex
    match = re.search(r'of (\d+) entries', info_text)
    if match:
        total_entries = int(match.group(1))  # Extract the number of entries
    else:
        total_entries = 0  # Default to 0 if parsing fails

    # Determine the expected number of rows to display (lesser of 100 or total_entries)
    expected_entries = min(100, total_entries)

    # If rows <= 25, skip dropdown selection and pagination logic
    if total_entries > 25:

        # Locate the Show Entries dropdown
        entries_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#set_parts_list_length select"))
        )

        # Wait until the Show Entries dropdown is clickable, and click it
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#set_parts_list_length select")))
        entries_dropdown.click()
        
        # Select "100" from the dropdown
        select = Select(entries_dropdown)
        select.select_by_visible_text("100")
        
        # Trigger the change event
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", entries_dropdown)

        # Wait for the "Showing 1 to 25 of n entries" text to update to show the correct range
        expected_info_text = f"Showing 1 to {expected_entries} of {total_entries} entries"
        WebDriverWait(driver, 20).until(
            lambda driver: expected_info_text in driver.find_element(By.CSS_SELECTOR, '.dataTables_info').text
        )

    # Pagination handling for the parts list page
    combined_page_source = ""

    while True:
        # Append the current page's source
        combined_page_source += driver.page_source

        # Check if the "Next" button is available and enabled
        try:
            next_button = driver.find_element(By.ID, "set_parts_list_next")
            if "disabled" in next_button.get_attribute("class"):
                break  # Exit the loop if the button is disabled

            # Record the current number of rows
            current_row_count = len(driver.find_elements(By.CSS_SELECTOR, '#set_parts_list tbody tr'))

            # Click the "Next" button
            next_button.click()

            # Wait for the table to update (using .dataTables_info to confirm a change)
            WebDriverWait(driver, 10).until(
                lambda d: int(d.find_element(By.CSS_SELECTOR, '.dataTables_info').text.split("to")[1].split("of")[0].strip()) > current_row_count
            )

        except NoSuchElementException:
            # Exit the loop if the "Next" button is not found
            break

    return combined_page_source

# Function to scrape the parts list from the page source

def scrape_part_list(page_source):

    soup = BeautifulSoup(page_source, "html.parser")
    parts = []

    # Get the part list
    part_list_rows = soup.select("#set_parts_list tr")
    for row in part_list_rows:
        cells = row.find_all("td")
        if len(cells) < 5:  # Skip invalid rows
            continue
        part_id = cells[0].text.strip()
        part_name = cells[1].text.strip()
        design_id = cells[2].text.strip()
        color = cells[3].text.strip()
        type = cells[4].text.strip()
        quantity = cells[6].text.strip()
        parts.append({"Part ID": part_id, "Part Name": part_name, "Design ID": design_id, "Color": color, "Type": type, "Qty": quantity})

    return parts

# Function to save the part list to a CSV file

def write_part_list_to_csv(part_list, set_number):

    # Create subdirectory for part list if it doesn't exist
    output_dir = f"../../data/user_data/{set_number}"
    os.makedirs(output_dir, exist_ok=True)  # Create the subdirectory if it doesn't exist

    # Output CSV file path using the set number in the file name
    csv_file_name = f"{set_number}_part_list.csv"
    csv_file_path = os.path.join(output_dir, csv_file_name)

    # CSV headers
    headers = ["Part ID", "Part Name", "Design ID", "Color", "Type", "Quantity"]

    # Writing to CSV
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)

        # Write headers
        writer.writerow(headers)

        # Write data
        for part in part_list:
            writer.writerow([
                part["Part ID"],   # Part ID
                part["Part Name"], # Part Name
                part["Design ID"], # Design ID
                part["Color"],     # Color
                part["Type"],      # Type
                part["Qty"]        # Quantity
            ]
        )

    print(f"Parts list exported successfully to {csv_file_path}")

# Main function

def main(set_number):

    # Normalize the set number
    normalized_set_number = normalize_set_number(set_number)
        
    # Get Instabrick credentials and initialize the WebDriver
    username, password = load_environment()
    driver = init_webdriver()

    # Log into Instabrick and get the part list for the specified set
    try:
        # Log into Instabrick
        login_instabrick(driver, username, password)

        # Get the page source for the part list
        page_source = get_part_list_page(driver, normalized_set_number)

        # Get the part list from the page source
        part_list = scrape_part_list(page_source)

        # Save the part list to a CSV file
        write_part_list_to_csv(part_list, normalized_set_number)

    finally:
        driver.quit()

# Entry point

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lego-part-list.py <set_number>")
        sys.exit(1)

    set_number = sys.argv[1]
    main(set_number)