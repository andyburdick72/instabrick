# LEGO Pick List Generator

## Description

The LEGO Pick List Generator is a Python script designed to help LEGO enthusiasts create a pick list for any given LEGO set using their Instabrick inventory. This tool simplifies the process of identifying which parts to get from which containers in your inventory.

## Features

- Generate a pick list for any LEGO set.
- Cross-reference with your Instabrick inventory.
- Easy to use and customize.

## Download Your Instabrick Inventory

To get started with the LEGO Pick List Generator, follow these steps:

- From the Inventory page of the Instabrick website (https://app.instabrick.org/inventory), click Export XML to download your inventory file
- Accept the default file name of inventory.xml, and place it in the instabrick/data/user_data/ folder

## Usage

For each set that you want a pick list generated for:

- Create a subdirectory under the instabrick/src/lego-pick-list/data/ directory, using the set number as the name (e.g. 10783)
- Grab the set of parts for the set from the Sets page of the Instabrick website (https://app.instabrick.org/sets > Set Info)
- Save it as an Excel spreadsheet, naming it set_number_part_list.xlsx (e.g. 10783_part_list.xlsx), and placing it in the instabrick/src/lego-pick-list/data/<set_number> subdirectory you created for the set

Open a terminal window, and navigate to the instabrick/src/lego-pick-list directory:

  cd instabrick/src/lego-pick-list

Run the script with the desired LEGO set ID from your command line:

  python3 lego-pick-list.py <set_number>

Replace <set_number> with the set number of the LEGO set you want to generate a pick list for, and press enter.

The resulting pick list will be put in the <set_number> subdirectory in the instabrick/src/lego-pick-list/data/<set_number> directory you created for the set