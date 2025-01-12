import json
import os
import pandas as pd
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.common_functions import normalize_set_number

# File paths for color mapping and user's inventory

color_mapping_file = '../../data/instabrick_colors.csv'
inventory_file = '../../data/user_data/inventory.xml'
    
# Function to read the color mapping

def read_color_mapping():
    df_colors = pd.read_csv(color_mapping_file)
    df_colors['color'] = df_colors['color'].astype(str)
    return df_colors

# Function to read the required parts and map color names

def read_required_parts(part_list_file):
    try:
        df_parts = pd.read_csv(part_list_file)
    except FileNotFoundError:
        print(f"Error: The required file '{part_list_file}' is missing. Please ensure the file exists and try again.")
        raise  # Re-raise the exception after logging the message to terminate the program
        
    df_colors = read_color_mapping()

    # Merge the part list with the color mapping on the 'Color' column
    required_parts = pd.merge(df_parts, df_colors, left_on='Color', right_on='name', how='left')
    required_parts = required_parts[['Design ID', 'Part ID', 'Color', 'name', 'Quantity', 'Part Name']].rename(columns={'name': 'Color Name'})

    return required_parts

# Function to parse the inventory XML

def parse_inventory():

    tree = ET.parse(inventory_file)
    root = tree.getroot()

    inventory = []

    # Load strings to ignore from (optional) configuration file
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        config = {}

    ignore_strings = config.get('ignore_strings', [])

    # Build the inventory data structure
    for item in root.findall('ITEM'):
        design_id = item.find('ITEMID').text
        color = item.find('COLOR').text
        quantity = int(item.find('QTY').text)
        location = item.find('REMARKS').text

        # Ignore locations matching the strings to ignore
        if any(ignore in location for ignore in ignore_strings):
            continue

        # Remove the [IB] text from the location for readability
        if location.startswith('[IB]') and location.endswith('[IB]'):
            location = location[4:-4].strip()

        inventory.append({
            'design_id': design_id,
            'color': color,
            'quantity': quantity,
            'location': location
        })

    return inventory

# Function to create the pick list

def create_pick_list(required_parts, inventory):
    pick_list = []

    for _, part in required_parts.iterrows():
        part_found = False

        design_id = str(part['Design ID'])
        part_id = str(part['Part ID'])
        color = str(part['Color'])
        color_name = part['Color Name'] # Color name for output
        quantity_needed = part['Quantity']
        description = part['Part Name']

        for item in inventory:
            if item['design_id'] == design_id:
                pick_list.append({
                    'Location': item['location'],
                    'Design ID': design_id,
                    'Description': description,
                    'Color': color_name,
                    'Quantity Needed': quantity_needed
                })

                # Mark that the part was found
                part_found = True

                break

        # If the part was not found, add a "Location Unknown" row
        if not part_found:
            pick_list.append({
                'Location': '(Location unknown)',
                'Design ID': design_id,
                'Description': description,
                'Color': color_name,
                'Quantity Needed': quantity_needed
            })

    # Sort the pick list by Location, then Design ID
    pick_list = sorted(pick_list, key=lambda x: (x['Location'], x['Design ID']))
    
    return pick_list

# Function to save the pick list to an Excel file

def save_pick_list(pick_list, output_file):
    df = pd.DataFrame(pick_list)
    df.to_csv(output_file, index=False)

# Main function

def main(set_number):

    # Normalize the set number
    normalized_set_number = normalize_set_number(set_number)
        
    # Define part list and output paths based on the set number
    subdirectory = f'../../data/user_data/{normalized_set_number}'
    part_list_file = os.path.join(subdirectory, f'{normalized_set_number}_part_list.csv')
    output_file = os.path.join(subdirectory, f'{normalized_set_number}_pick_list.csv')

    # Read required parts and parse the inventory
    required_parts = read_required_parts(part_list_file)
    inventory = parse_inventory()

    # Create the pick list
    pick_list = create_pick_list(required_parts, inventory)

    # Save the pick list to an Excel file
    save_pick_list(pick_list, output_file)

    print(f"Pick list saved to {output_file}")

# Entry point

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 lego-pick-list.py <set_number>")
        sys.exit(1)

    set_number = sys.argv[1]
    main(set_number)