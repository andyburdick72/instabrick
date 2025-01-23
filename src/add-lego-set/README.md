# Add LEGO Set Automator

## Description

Add LEGO Set Automator is a Python script designed to help LEGO enthusiasts automatically part out a new LEGO set into a specific Drawer and Container in their Instabrick inventory.

## Features

- Searches on the Instabrick Sets page for the set number passed in, and verifies its set name and that the part list is complete.
- Prompts the user for the Drawer in their Instabrick inventory that they want to use, and creates a new Container (using the set number and set name) in that chosen Drawer.
- Parts out the set into the chosen Drawer and new Container.

## Usage

- In a Terminal window, navigate to the `/instabrick/src/add-lego-set` directory; `cd /instabrick/src/add-lego-set`
- Run the script with the desired LEGO set ID from your command line: `python3 add-lego-set.py <set_number>`, replacing <set_number> with the set number of the LEGO set you want to generate a pick list for (e.g. `python3 add-lego-set.py 10783`), and press enter.
- Set number can include or exclude the hyphen (e.g. `10783-1` or `10783`); if no hyphen is included, `-1` will be assumed and added automatically.
- You will be prompted to choose a Drawer from your list of Drawers; this is the Drawer to which the new Container will be added.

All the parts for the set will be added to the new Container in the chosen Drawer.