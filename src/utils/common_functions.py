# common_functions.py

# Function to normalize the set number

def normalize_set_number(set_number):
    if '-' in set_number:
        print(f"Extracting part list for set number '{set_number}'.")
        return set_number
    else:
        normalized_set_number = f"{set_number}-1"
        print(f"Extracting part list for set number '{normalized_set_number}'.")
        return normalized_set_number