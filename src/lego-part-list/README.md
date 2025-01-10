# LEGO Part List Extractor

## Description

The LEGO Part List Extractor is a Python script designed to help LEGO enthusiasts generate a part list for any given LEGO set listed on the Instabrick website and save it to a CSV file. The CSV file can then be used by the LEGO Pick List Generator Python script in this project.

## Features

- Downloads a part list for any LEGO set on the Instabrick website.
- Handles pagination and dynamic content on the Instabrick Sets page.
- Exports extracted part list data to a comma-delimited CSV file.

## Usage

- In a Terminal window, navigate to the `/instabrick/src/lego-part-list` directory; `cd /instabrick/src/lego-part-list`
- Run the script with the desired LEGO set ID from your command line: `python3 lego-part-list.py <set_number>`, replacing <set_number> with the set number of the LEGO set you want to generate a pick list for (e.g. `python3 lego-part-list.py 10783`), and press enter.
- Set number can include or exclude the hyphen (e.g. `10783-1` or `10783`); if no hyphen is included, `-1` will be assumed and added automatically.

The resulting part list will be put in a new <set_number> subdirectory in your `/instabrick/data/user_data` directory, and will be named `set_number_pick_list.csv` (e.g. `10783-1_part_list.csv`).