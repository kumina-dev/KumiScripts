# KumiScripts

KumiScripts is a script management tool that allows you to install and run scripts from a remote server. It provides a convenient way to organize and execute various scripts for your projects.

## Installation

1. Clone the repository:
   git clone https://github.com/your-username/kumi-scripts.git

2. Navigate to the project directory:
   cd kumi-scripts

## Usage

1. Modify the `scripts_directory` and `website_url` variables in the `kumiscripts.py` file to specify the directory where the scripts will be installed and the URL of the remote server hosting the scripts.

2. Run the script to install the required scripts:
   python kumiscripts.py

The script will retrieve the script information from the remote server and install any missing scripts in the specified directory.

3. After the installation, the script will prompt you to select a script to run. Enter the number of the script you want to execute, and the selected script will be launched.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.
