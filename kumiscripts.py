import os
import sys
import requests
import subprocess
import json
from tqdm import tqdm
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QTextEdit

class ScriptInstallerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KumiScripts")
        self.resize(600, 400)

        # Script settings
        self.scripts_directory = './scripts'
        self.website_url = 'https://kumina.wtf/scripts'
        self.script_list = []

        # Create and set central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout(central_widget)
        script_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        cmd_layout = QVBoxLayout()

        # Script Input
        self.script_input = QLineEdit()
        script_layout.addWidget(QLabel("Website URL:"))
        script_layout.addWidget(self.script_input)

        # Install Button
        install_button = QPushButton("Install Scripts")
        install_button.clicked.connect(self.install_scripts)
        button_layout.addWidget(install_button)

        # Script List
        self.script_list_widget = QListWidget()
        self.script_list_widget.itemDoubleClicked.connect(self.remove_website)
        script_layout.addWidget(self.script_list_widget)

        # CMD Output
        self.cmd_output = QTextEdit()
        self.cmd_output.setReadOnly(True)
        cmd_layout.addWidget(QLabel("CMD Output:"))
        cmd_layout.addWidget(self.cmd_output)

        # Main Layout
        main_layout.addLayout(script_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(cmd_layout)

        # Load script settings
        self.load_settings()
    
    def load_settings(self):
        config_file = 'config.json'
        if os.path.isfile(config_file):
            with open(config_file, 'r') as file:
                settings = json.load(file)
                self.scripts_directory = settings.get('scripts_directory', './scripts')
                self.website_url = settings.get('website_url', 'https://kumina.wtf/scripts')

    def save_settings(self):
        config_file = 'config.json'
        settings = {
            'scripts_directory': self.scripts_directory,
            'website_url': self.website_url
        }
        with open(config_file, 'w') as file:
            json.dump(settings, file)

    def install_scripts(self):
        website_url = self.script_input.text().strip()
        if website_url:
            check_and_install_scripts(self.scripts_directory, website_url)
            self.update_script_list()
            self.script_input.clear()
            self.save_settings()
    
    def update_script_list(self):
        self.script_list_widget.clear()
        self.script_list = os.listdir(self.scripts_directory)
        for script in self.script_list:
            item = QListWidgetItem(script)
            self.script_list_widget.addItem(item)
    
    def remove_website(self, item):
        selected_script = item.text()
        script_path = os.path.join(self.scripts_directory, selected_script)
        os.remove(script_path)
        self.update_script_list()
        self.save_settings()
    
    def run_script(self):
        selected_script = self.script_list_widget.currentItem().text()
        script_path = os.path.join(self.scripts_directory, selected_script)
        process = subprocess.Popen(["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()
        self.cmd_output.setPlainText(output.decode())

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScriptInstallerGUI()
    window.show()
    sys.exit(app.exec_())
