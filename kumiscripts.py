import os
import sys
import requests
import subprocess
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QTextEdit, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class ScriptRunner(QThread):
    finished = pyqtSignal(str)

    def __init__(self, script_path):
        super().__init__()
        self.script_path = script_path
    
    def run(self):
        process = subprocess.Popen(
            ["python", self.script_path],
            capture_output=True,
            text=True
        )
        self.finished.emit(process.stdout)

class ScriptInstallerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KumiScripts")
        self.resize(600, 400)

        # Script settings
        self.config_file = 'config.json'
        self.scripts_directory = './scripts'
        self.website_list = []
        self.script_list = []

        # Create and set central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout(central_widget)
        website_layout = QHBoxLayout()
        script_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        cmd_layout = QVBoxLayout()

        # Website Input
        self.website_input = QLineEdit()
        website_layout.addWidget(QLabel("Website URL:"))
        website_layout.addWidget(self.website_input)

        # Add Website Button
        add_website_button = QPushButton("Add Website")
        add_website_button.clicked.connect(self.add_website)
        button_layout.addWidget(add_website_button)

        # Remove Website Button
        remove_website_button = QPushButton("Remove Website")
        remove_website_button.clicked.connect(self.remove_website)
        button_layout.addWidget(remove_website_button)

        # Website List
        self.website_list_widget = QListWidget()
        self.website_list_widget.itemDoubleClicked.connect(self.update_script_list)  # Connect the signal
        website_layout.addWidget(self.website_list_widget)

        # Script List
        self.script_list_widget = QListWidget()
        script_layout.addWidget(QLabel("Select Scripts to Install:"))
        script_layout.addWidget(self.script_list_widget)

        # Install Scripts Button
        install_button = QPushButton("Install Scripts")
        install_button.clicked.connect(self.install_scripts)
        button_layout.addWidget(install_button)

        # Run Script Button
        run_script_button = QPushButton("Run Script")
        run_script_button.clicked.connect(self.run_script)
        button_layout.addWidget(run_script_button)

        # CMD Output
        self.cmd_output = QTextEdit()
        self.cmd_output.setReadOnly(True)
        cmd_layout.addWidget(QLabel("CMD Output:"))
        cmd_layout.addWidget(self.cmd_output)

        # Main Layout
        main_layout.addLayout(website_layout)
        main_layout.addLayout(script_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(cmd_layout)

        # Load script settings
        self.load_settings()
    
    def load_settings(self):
        if os.path.isfile(self.config_file):
            with open(self.config_file, 'r') as file:
                settings = json.load(file)
                self.scripts_directory = settings.get('scripts_directory', './scripts')
                self.website_list = settings.get('websites', [])
        
        self.update_website_list()
        self.update_script_list()  # Add this line to update the script list initially

    def save_settings(self):
        config_file = 'config.json'
        settings = {
            'scripts_directory': self.scripts_directory,
            'websites': self.website_list
        }
        with open(config_file, 'w') as file:
            json.dump(settings, file)
    
    def add_website(self):
        website_url = self.website_input.text()
        if website_url:
            item = QListWidgetItem(website_url)
            self.website_list_widget.addItem(item)
            self.website_input.clear()

    def remove_website(self):
        selected_website_items = self.website_list_widget.selectedItems()
        for item in selected_website_items:
            self.website_list_widget.takeItem(self.website_list_widget.row(item))
        
        self.update_script_list()

    def update_website_list(self):
        self.website_list_widget.clear()
        for website in self.website_list:
            item = QListWidgetItem(website)
            self.website_list_widget.addItem(item)

    def install_scripts(self):
        selected_website_item = self.website_list_widget.currentItem()
        if selected_website_item is None:
            print("No website selected.")
            return

        selected_website = selected_website_item.text()  # Retrieve website URL from the item's text

        selected_scripts = []
        for index in range(self.script_list_widget.count()):
            item = self.script_list_widget.item(index)
            if item.checkState() == Qt.Checked:
                selected_scripts.append(item.text())
        if not selected_scripts:
            print("No scripts selected.")
            return
        
        scripts_url = f"{selected_website}/scripts.json"
        try:
            response = requests.get(scripts_url)
            response.raise_for_status()
            script_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while retrieving script information: {e}")
            return
        
        scripts_to_install = script_data.get('scripts', [])
        if not scripts_to_install:
            print("No scripts found to install.")
            return
        
        selected_scripts_to_install = [
            script for script in scripts_to_install if script['name'] in selected_scripts
        ]

        for script in selected_scripts_to_install:
            script_name = script['name']
            script_url = script['url']
            script_path = os.path.join(self.scripts_directory, script_name)
            if not os.path.isfile(script_path):
                install_script(script_name, self.scripts_directory, script_url)
        
        print("Installation completed.")
    
    def update_script_list(self):
        self.script_list_widget.clear()

        selected_website_item = self.website_list_widget.currentItem()
        if selected_website_item is None:
            return

        selected_website = selected_website_item.text()  # Retrieve website URL from the item's text
        scripts_url = f"{selected_website}/scripts.json"
        try:
            response = requests.get(scripts_url)
            response.raise_for_status()
            script_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while retrieving script information: {e}")
            QMessageBox.warning(self, "Error", "Error occurred while retrieving script information.")
            return

        scripts_to_install = script_data.get('scripts', [])
        if not scripts_to_install:
            QMessageBox.information(self, "No Scripts", "No scripts found to install.")
            return

        self.script_list_widget.clear()
        for script in scripts_to_install:
            script_name = script['name']
            item = QListWidgetItem(script_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.script_list_widget.addItem(item)

    def clear_script_list(self):
        self.script_list_widget.clear()
    
    def run_script(self):
        selected_item = self.script_list_widget.currentItem()
        if selected_item is None:
            return
        
        selected_script = selected_item.text()
        script_path = os.path.join(self.scripts_directory, selected_script)

        self.script_runner = ScriptRunner(script_path)
        self.script_runner.finished.connect(self.display_script_output)
        self.script_runner.start()
    
    def display_script_output(self, output):
        self.cmd_output.append(output)

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

def install_script(script_name, scripts_directory, script_url):
    script_path = os.path.join(scripts_directory, script_name)

    print(f"Downloading script '{script_name}'...")
    response = requests.get(script_url)
    response.raise_for_status()
    
    with open(script_path, 'wb') as file:
        file.write(response.content)
    
    print(f"Script '{script_name}' installed successfully.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScriptInstallerGUI()
    gui.show()
    sys.exit(app.exec())
