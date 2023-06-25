import os
import subprocess
import requests
from tqdm import tqdm

def run_script(script_path):
    try:
        subprocess.check_output(['python', script_path])
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_path}: {e.output.decode()}")

def install_script(script_url, script_path):
    response = requests.get(script_url)
    with open(script_path, 'wb') as file:
        file.write(response.content)

def check_and_install_scripts(script_directory, website_url):
    response = requests.get(website_url)
    required_scripts = response.json()

    missing_scripts = []
    for script in required_scripts:
        script_path = os.path.join(script_directory, script['filename'])
        if not os.path.isfile(script_path):
            missing_scripts.append(script)
    
    if missing_scripts:
        print("Installing missing scripts:")
        for script in tqdm(missing_scripts):
            install_script(script['url'], os.path.join(script_directory, script['filename']))
        print("Installation completed.")

def prompt_user(script_directory):
    script_files = [filename for filename in os.listdir(script_directory) if filename.endswith('.py')]
    if not script_files:
        print("No script files found in the directory.")
        return
    
    print("Available scripts:")
    for index, script_file in enumerate(script_files, start=1):
        print(f"{index}. {script_file}")
    
    script_choice = input("Enter the number corresponding to the script you want to run: ")

    try:
        script_index = int(script_choice) - 1
        if 0 <= script_index < len(script_files):
            script_path = os.path.join(script_directory, script_files[script_index])
            run_script(script_path)
        else:
            print("Invalid script choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")

scripts_directory = './scripts'

website_url = 'https://kumina.wtf/scripts'

check_and_install_scripts(scripts_directory, website_url)
prompt_user(scripts_directory)