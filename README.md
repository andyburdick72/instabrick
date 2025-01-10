# Instabrick LEGO Project

## Description

Welcome to my Instabrick LEGO project! In this project, I use Python to automate some features not (yet) available on the Instabrick website.

## Scripts

- Download a part list for any LEGO set from the Instabrick website
- Generate a pick list for any LEGO set, based on the parts in your Instabrick inventory
- (Future) Tear down built LEGO sets into your main Instabrick inventory (provided they are stored in a separate drawer / container)

## Installation

To get started with the Instabrick LEGO project, follow these steps:

   ### Clone the repository:

   - Ensure you have Git or GitHub Desktop installed
   - Navigate to my Git repository in your web browser: https://github.com/andyburdick72/instabrick
   - Click the green Code button, and clone the repository

   ### Install Python:

   - Install Python 3 on your desktop (for macOS, I recommend using Homebrew)
   - Verify the Python installation by running `python3 --version` from a Terminal window

   ### Install dependencies:

   - Navigate to the `/instabrick` folder in a Terminal window
   - Install dependencies: `python3 -m pip install -r requirements.txt`
   - (If you receive an "externally managed environment" error, add the flag `--break-system-packages` to the above command or set up a virtual environment)

   ### Download Your Instabrick Inventory:

   - From the Inventory page of the Instabrick website (https://app.instabrick.org/inventory), click Export XML to download your inventory file
   - Accept the default file name of `inventory.xml`, and place it in the `/instabrick/data/user_data/` folder

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE.txt file for details.

## Contact

For any questions or feedback, feel free to reach out to me at andyburdick72@gmail.com.

## Acknowledgments

Special thanks to the LEGO community and Instabrick, in particular Stefano Berti (admin@instabrick.org), for their inspiration and support!