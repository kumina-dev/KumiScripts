import os
import requests
import subprocess
from tqdm import tqdm

def install_script(script_name, script_directory, script_url):
    script_path = os.path.join(script_directory, script_name)

    try:
        response = requests.get(script_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error occurred while downloading script '{script_name}': {e}")
        return

    with open(script_path, 'wb') as file:
        file.write(response.content)
    print(f"Script '{script_name}' installed successfully.")

def check_and_install_scripts(script_directory, website_url):
    scripts_url = f"{website_url}/scripts.json"
    try:
        response = requests.get(scripts_url)
        response.raise_for_status()
        script_data = response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error occurred while retrieving script information: {e}")
        return
    except ValueError as e:
        print(f"Error occurred while parsing script data: {e}")
        return

    scripts_to_install = script_data.get('scripts', [])
    if not scripts_to_install:
        print("No scripts found to install.")
        return

    print("Installing missing scripts:")
    for script in tqdm(scripts_to_install):
        script_name = script['name']
        script_url = script['url']
        script_path = os.path.join(script_directory, script_name)
        if not os.path.isfile(script_path):
            install_script(script_name, script_directory, script_url)

    print("Installation completed.")

def run_script(scripts_directory):
    script_files = os.listdir(scripts_directory)
    if not script_files:
        print("No scripts found in the directory.")
        return
    
    print("Available scripts:")
    for i, script_file in enumerate(script_files):
        print(f"{i + 1}. {script_file}")

    while True:
        try:
            script_choice = int(input("Enter the number of the script you want to run (or 0 to exit): "))
            if script_choice == 0:
                return
            script_index = script_choice - 1
            selected_script = script_files[script_index]
            script_path = os.path.join(scripts_directory, selected_script)
            subprocess.run(["python", script_path])
        except ValueError:
            print("Invalid input. Please enter a valid script number.")
        except IndexError:
            print("Invalid script number. Please try again.")

scripts_directory = './scripts'
website_url = 'https://kumina.wtf/scripts'

check_and_install_scripts(scripts_directory, website_url)
run_script(scripts_directory)
