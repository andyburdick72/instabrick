import sys
from pathlib import Path
from selenium.webdriver.support import expected_conditions as EC

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import common functions from utils
from utils.common_functions import init_webdriver
from utils.common_functions import load_environment
from utils.common_functions import login_instabrick
from utils.common_functions import navigate_to_sets_page
from utils.common_functions import normalize_set_number
from utils.common_functions import search_for_set

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

        # Navigate to the Sets page
        navigate_to_sets_page(driver)

        # Search for the set on the Sets page and return the first row
        first_matching_row = search_for_set(driver, normalized_set_number)

        # WAB - continue here...
    
    finally:
        driver.quit()

# Entry point

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add-lego-set.py <set_number>")
        sys.exit(1)

    set_number = sys.argv[1]
    main(set_number)