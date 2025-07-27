import csv
import os 
import re
import sys
from bs4 import BeautifulSoup
from pathlib import Path
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import common functions from utils
from utils.common_functions import init_webdriver
from utils.common_functions import load_instabrick_environment
from utils.common_functions import login_instabrick
from utils.common_functions import navigate_to_sets_page
from utils.common_functions import normalize_set_number
from utils.common_functions import search_for_set

# Function to get the page source for the part list

def get_part_list_page(driver, first_matching_row):

    # Go to the first row of the Sets table and find the Set Info button
    set_info_button = first_matching_row.find_element(By.CSS_SELECTOR, "td .table_button_show_set")

    # Click the Set Info button
    set_info_button.click()

    # Locate the "Showing 1 to 25 of n entries" text
    info_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.dataTables_info'))
    )
    info_text = info_element.text
    
    # Extract the total number of entries using regex
    match = re.search(r'of (\d+) entries', info_text)
    if match:
        total_entries = int(match.group(1))  # Extract the number of entries
    else:
        total_entries = 0  # Default to 0 if parsing fails

    # Determine the expected number of rows to display (lesser of 100 or total_entries)
    expected_entries = min(100, total_entries)
    print(f"Total entries: {total_entries}, expected entries: {expected_entries}")

    # If rows <= 25, skip dropdown selection and pagination logic
    if total_entries > 25:

        # Locate the Show Entries dropdown
        entries_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#set_parts_list_length select"))
        )

        # Wait until the Show Entries dropdown is clickable, and click it
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#set_parts_list_length select"))
        )
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

            # Get the current range of displayed entries from .dataTables_info
            current_info_text = driver.find_element(By.CSS_SELECTOR, ".dataTables_info").text

            # Click the "Next" button
            next_button.click()

            # Wait for the table to update to the next range of entries
            WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.CSS_SELECTOR, ".dataTables_info").text != current_info_text
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
    username, password = load_instabrick_environment()
    driver = init_webdriver()

    # Log into Instabrick and get the part list for the specified set
    try:
        # Log into Instabrick
        login_instabrick(driver, username, password)

        # Navigate to the Sets page
        navigate_to_sets_page(driver)

        # Search for the set on the Sets page and return the first row
        first_matching_row = search_for_set(driver, normalized_set_number)
    
        # Get the page source for the part list
        page_source = get_part_list_page(driver, first_matching_row)

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