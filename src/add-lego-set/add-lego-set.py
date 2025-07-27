import sys
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import common functions from utils
from utils.common_functions import init_webdriver
from utils.common_functions import load_instabrick_environment
from utils.common_functions import login_instabrick
from utils.common_functions import navigate_to_inventory_page
from utils.common_functions import navigate_to_sets_page
from utils.common_functions import normalize_set_number
from utils.common_functions import search_for_set


# Function to get the set name and number of parts from the row

def extract_set_details(set_row):
    try:
        set_name = set_row.find_element(By.XPATH, "./td[3]").text
        num_parts = int(set_row.find_element(By.XPATH, "./td[6]").text)
        print(f"Set Name: {set_name}, Number of Parts: {num_parts}")
        return set_name, num_parts
    
    except Exception as e:
        print(f"Failed to extract set details: {e}")
        return None, None

# Function to find the Part Out button for the first row on the Sets page and click it

def click_part_out_button(driver, set_row):
        
    try:
        part_out_button = set_row.find_element(By.CSS_SELECTOR, "td .table_button_partout_inventory")
        part_out_button.click()

        # Wait for the page to load (by waiting for Drawer dropdown to appear)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "inventory_drawerPartout"))
        )
    except Exception as e:
        print(f"Failed to click Part out button: {e}")

# Function to part out a Set into a selected Drawer and Container

def part_out_set(driver, drawer_name, container_name):

    try:

        # Find the Drawer dropdown and select the desired drawer
        drawer_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "inventory_drawerPartout"))
        )

        # Click the dropdown to open it
        drawer_dropdown.click()

        # Wait for the options to be populated
        WebDriverWait(driver, 10).until(
            lambda d: len(Select(d.find_element(By.ID, "inventory_drawerPartout")).options) > 1
        )

        Select(drawer_dropdown).select_by_visible_text(drawer_name)
        print(f"Selected drawer: {drawer_name}")

        # Find the Container dropdown and select the desired container
        container_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "inventory_containerPartout"))
        )

        # Click the dropdown to open it
        container_dropdown.click()

        # Wait for the options to be populated
        WebDriverWait(driver, 10).until(
            lambda d: len(Select(d.find_element(By.ID, "inventory_containerPartout")).options) > 1
        )

        Select(container_dropdown).select_by_visible_text(container_name)
        print(f"Selected container: {container_name}")

        # Step 3: Click the "Part Out" button
        part_out_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "inventoryModalActionPartout"))
        )
        part_out_button.click()
        print("Clicked 'Part Out' button.")

        # Step 4: Wait for the response or confirmation
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        print("Part out completed successfully.")

    except Exception as e:
        print(f"Failed to part out set into Drawer {drawer_name} and Container {container_name}: {e}")
    
# Function to click the Drawers button on the Inventory page

def click_drawers_button(driver):

    try:
        # Find the Drawers button and click it
        drawers_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="drawers"]/parent::label'))
        )
        drawers_button.click()

        # Wait for the page to load again (by waiting for Add Drawer to appear)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "add_drawer"))
        )
    except Exception as e:
        print(f"Failed to click Drawers button: {e}")

# Function to get the set of Drawers and ask the user to choose one

def choose_drawer(driver):

    try:
        # Find all elements with the class 'card-header' inside the inventory list
        drawer_elements = driver.find_elements(By.CSS_SELECTOR, '#inventory_list .card-header')

        # Extract the text (drawer names) from the elements
        drawer_names = [drawer.text.strip() for drawer in drawer_elements]

        # Present the list to the user
        if drawer_names:
            print("Available Drawers:")
            for idx, name in enumerate(drawer_names, start=1):
                print(f"{idx}: {name}")

            # Ask user to choose a drawer
            user_choice = int(input("Choose a drawer by number: "))
            drawer_name = drawer_names[user_choice - 1]
            print(f"You chose: {drawer_name}")
        else:
            print("No drawers found!")

        return drawer_name
    
    except Exception as e:
        print(f"Failed to choose a Drawer: {e}")
        return None

# Function to manage the content of a drawer

def manage_drawer_content(driver, drawer):

    try:
        # Use the drawer ID to locate the "Manage Content" button
        card_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//div[@class="card-header" and normalize-space()="{drawer}"]'))
        )
        # Traverse to the parent card and find the "Manage Content" button
        manage_content_button = card_header.find_element(By.XPATH, './/following-sibling::div[@class="card-footer"]/a[@class="card_button_containers"]')

        # Click the "Manage Content" button
        manage_content_button.click()

        # Wait for the Drawer content to be displayed (by waiting for Add Container to appear)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "add_container"))
        )

    except Exception as e:
        print(f"Failed to click the 'Manage Content' button for drawer {drawer}: {e}")

# Function to add a container to a drawer (set number + set name)

def add_container(driver, set_number, set_name):

    try:
        # Find the Create container button and click it
        create_container_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add_container"))
        )
        create_container_button.click()
        # Wait for the input field for the container name to appear
        container_name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input.add_container_name'))
        )

        # Set the container name
        container_name = f"{set_number} {set_name}"
        container_name_input.send_keys(container_name)
        print(f"Set container name to: {container_name}")

        # Find the Save button and click it
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.save_add_container'))
        )
        save_button.click()
        print("Successfully saved the new container.")
        return container_name

    except Exception as e:
        print(f"Failed to add container {container_name}: {e}")
        return None

# Main function

def main(set_number):

    # Normalize the set number
    normalized_set_number = normalize_set_number(set_number)
        
    # Get Instabrick credentials and initialize the WebDriver
    username, password = load_instabrick_environment()
    driver = init_webdriver()

    # Log into Instabrick and add the set to inventory
    try:
        # Log into Instabrick
        login_instabrick(driver, username, password)

        # Navigate to the Sets page
        navigate_to_sets_page(driver)

        # Search for the set on the Sets page and return the first row
        first_matching_row = search_for_set(driver, normalized_set_number)    
    
        # Grab the set name and number of parts from the first row
        set_name, num_parts = extract_set_details(first_matching_row)
        if num_parts <= 1:
            print(f"Set {normalized_set_number} does not have the correct number of parts. Exiting...")
            return
        
        # Navigate to the Inventory page
        navigate_to_inventory_page(driver)

        # Wait for the Drawers button to be available and click it
        click_drawers_button(driver)

        # Ask the user to choose a drawer
        drawer_name = choose_drawer(driver)

        # Manage the content of the chosen drawer
        manage_drawer_content(driver, drawer_name)

        # Add a container to the drawer for the set
        container_name = add_container(driver, normalized_set_number, set_name)

        # Navigate back to the Sets page
        navigate_to_sets_page(driver)

        # Search for the set on the Sets page again and return the first row
        first_matching_row = search_for_set(driver, normalized_set_number)    
        
        # Find the Part Out button for the first row on the Sets page and click it
        click_part_out_button(driver, first_matching_row)

        # Part out the set into the chosen drawer / container
        part_out_set(driver, drawer_name, container_name)

    finally:
        driver.quit()

# Entry point

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add-lego-set.py <set_number>")
        sys.exit(1)

    set_number = sys.argv[1]
    main(set_number)