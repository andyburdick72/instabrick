import os
import pandas as pd
import xml.etree.ElementTree as ET
import sys

# File paths for color mapping and user's inventory

color_mapping_file = '../../data/instabrick_colors.xlsx'
inventory_file = '../../data/user_data/inventory.xml'

# Function to read the color mapping

def read_color_mapping():
    df_colors = pd.read_excel(color_mapping_file)
    df_colors['color'] = df_colors['color'].astype(str)
    return df_colors

# Function to read the required parts and map color names

def read_required_parts(part_list_file):
    df_parts = pd.read_excel(part_list_file)
    df_colors = read_color_mapping()

    # Merge the part list with the color mapping on the 'Color' column
    required_parts = pd.merge(df_parts, df_colors, left_on='Color', right_on='name', how='left')
    required_parts = required_parts[['Design ID', 'color', 'name', 'Quantity', 'Part Name']].rename(columns={'name': 'Color Name'})

    print(required_parts)
    return required_parts

# Function to parse the inventory XML

def parse_inventory():
    tree = ET.parse(inventory_file)
    root = tree.getroot()

    inventory = []

    for item in root.findall('ITEM'):
        item_id = item.find('ITEMID').text
        color = item.find('COLOR').text
        quantity = int(item.find('QTY').text)
        location = item.find('REMARKS').text

        # Ignore certain drawers
        if any(ignore in location for ignore in ['(Built)', '(In Box)', '(Teardown)', '(Work in Progress)']):
            continue

        # Clean up the location
        if location.startswith('[IB]') and location.endswith('[IB]'):
            location = location[4:-4].strip()

        inventory.append({
            'item_id': item_id,
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
        color = str(part['color'])
        color_name = part['Color Name'] # Color name for output
        quantity_needed = part['Quantity']
        description = part['Part Name']

        for item in inventory:
            if item['item_id'] == design_id and item['color'] == color:
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
    df.to_excel(output_file, index=False)

# Main function

def main(set_number):

    # Define part list and output paths based on the set number

    subdirectory = f'data/{set_number}'
    part_list_file = os.path.join(subdirectory, f'{set_number}_part_list.xlsx')
    output_file = os.path.join(subdirectory, f'{set_number}_pick_list.xlsx')

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
