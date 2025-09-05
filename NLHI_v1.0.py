import sys
import json
import os
import hashlib
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QComboBox, QScrollArea, QFileDialog, QDateEdit, QListWidget,
    QMessageBox, QDialog, QInputDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


UNIT_CONVERSION = {
    "Day(s)": 1 / 365.25,
    "Week(s)": 1 / 52.1429,
    "Month(s)": 1 / 12.0,
    "Year(s)": 1.0,
}

CREDENTIALS_FILE = "credentials.json"
DATA_FILE = "nlhi_data.json"      
OLD_DATA_FILE = "nlchi_data.json" 

REGIONS_FILE = "regions.json"     


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def safe_float(s, default=0.0):
    try:
        return float(str(s).strip())
    except Exception:
        return default


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)
        self.setLayout(self.layout)
        self.successful_login = False

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not os.path.exists(CREDENTIALS_FILE):
            QMessageBox.warning(self, "Error", "No users registered.")
            return
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials = json.load(f)
        if username in credentials and credentials[username] == hash_password(password):
            self.successful_login = True
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")

    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if username == "" or password == "":
            QMessageBox.warning(self, "Error", "Username and password cannot be empty.")
            return
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
        else:
            credentials = {}
        if username in credentials:
            QMessageBox.warning(self, "Error", "Username already exists.")
            return
        credentials[username] = hash_password(password)
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f)
        QMessageBox.information(self, "Success", "User registered successfully.")

class ChangeCredentialsDialog(QDialog):
    def __init__(self, current_user):
        super().__init__()
        self.setWindowTitle("Change Username/Password")
        self.current_user = current_user
        self.layout = QVBoxLayout()
        self.new_username_input = QLineEdit()
        self.new_username_input.setPlaceholderText("New Username")
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New Password")
        self.new_password_input.setEchoMode(QLineEdit.Password)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_changes)

        self.layout.addWidget(self.new_username_input)
        self.layout.addWidget(self.new_password_input)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

    def save_changes(self):
        new_user = self.new_username_input.text().strip()
        new_pass = self.new_password_input.text()
        if new_user == "" or new_pass == "":
            QMessageBox.warning(self, "Error", "Username and password cannot be empty.")
            return
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials = json.load(f)
        
        if self.current_user in credentials:
            del credentials[self.current_user]
        credentials[new_user] = hash_password(new_pass)
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f)
        QMessageBox.information(self, "Success", "Credentials updated. Please restart app.")
        self.accept()


class NLHIApp(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Newfoundland and Labrador Health Index (NLHI) v1.0 - © 2025 Mirza Niaz Zaman Elin. All rights reserved.")
        self.username = username
        self.data = {}   

        
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                try:
                    self.data = json.load(f)
                except json.JSONDecodeError:
                    self.data = {}
        elif os.path.exists(OLD_DATA_FILE):
            with open(OLD_DATA_FILE, "r") as f:
                try:
                    self.data = json.load(f)
                except json.JSONDecodeError:
                    self.data = {}

        self.regions_file = REGIONS_FILE

        
        self.domain_rows = []

        self.init_ui()

    
    def init_ui(self):
        layout = QVBoxLayout()

        
        layout.addWidget(QLabel(f"Logged in as: {self.username}"))
        self.change_credentials_btn = QPushButton("Change Username/Password")
        self.change_credentials_btn.clicked.connect(self.change_credentials)
        layout.addWidget(self.change_credentials_btn)

        
        layout.addWidget(QLabel("Registered Regions:"))
        regions_row = QHBoxLayout()
        self.region_list = QListWidget()
        self.region_list.itemClicked.connect(self.load_region_data)
        regions_buttons = QVBoxLayout()
        self.register_region_btn = QPushButton("Add Region")
        self.register_region_btn.clicked.connect(self.register_new_region)
        self.delete_region_btn = QPushButton("Delete Selected Region")
        self.delete_region_btn.clicked.connect(self.delete_selected_region)
        regions_buttons.addWidget(self.register_region_btn)
        regions_buttons.addWidget(self.delete_region_btn)
        regions_buttons.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        regions_row.addWidget(self.region_list, 3)
        regions_row.addLayout(regions_buttons, 1)
        layout.addLayout(regions_row)

        
        layout.addWidget(QLabel("Selected Region:"))
        self.region_input = QLineEdit()
        self.region_input.setPlaceholderText("Enter or Select Region Name")
        layout.addWidget(self.region_input)

        layout.addWidget(QLabel("Date:"))
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(self.date_input)

        layout.addWidget(QLabel("Average Age (years):"))
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("e.g., 32.5")
        layout.addWidget(self.age_input)

        layout.addWidget(QLabel("Population Size:"))
        self.pop_input = QLineEdit()
        self.pop_input.setPlaceholderText("e.g., 52000")
        layout.addWidget(self.pop_input)

        layout.addWidget(QLabel("Average Life Expectancy (years):"))
        self.le_input = QLineEdit()
        self.le_input.setPlaceholderText("e.g., 80.7")
        layout.addWidget(self.le_input)

        
        layout.addWidget(QLabel("Domains (add/remove as needed):"))
        self.domains_layout = QVBoxLayout()
        layout.addLayout(self.domains_layout)

        domains_btn_row = QHBoxLayout()
        self.add_domain_btn = QPushButton("Add Domain")
        self.add_domain_btn.clicked.connect(self.add_domain_row)
        self.clear_domains_btn = QPushButton("Clear All Domains")
        self.clear_domains_btn.clicked.connect(self.clear_domains)
        domains_btn_row.addWidget(self.add_domain_btn)
        domains_btn_row.addWidget(self.clear_domains_btn)
        layout.addLayout(domains_btn_row)

        
        actions_row = QHBoxLayout()
        self.calc_button = QPushButton("Calculate and Save")
        self.calc_button.clicked.connect(self.calculate_and_save)
        self.view_button = QPushButton("View Dashboard")
        self.view_button.clicked.connect(self.view_dashboard)
        actions_row.addWidget(self.calc_button)
        actions_row.addWidget(self.view_button)
        layout.addLayout(actions_row)

        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        self.load_regions()

    
    def add_domain_row(self, preset=None):
        """
        Add a row with: [Domain Name] [TLIPHS value] [Unit] [Mortality] [Remove]
        preset: optional dict with keys: name, tliphs, unit, mortality
        """
        row_layout = QHBoxLayout()

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Domain name (e.g., Respiratory)")

        tliphs_edit = QLineEdit()
        tliphs_edit.setPlaceholderText("TLIPHS value")

        unit_combo = QComboBox()
        unit_combo.addItems(list(UNIT_CONVERSION.keys()))

        mort_edit = QLineEdit()
        mort_edit.setPlaceholderText("Total Mortality (domain-specific)")

        remove_btn = QPushButton("Remove")
        
        row_dict = {
            "layout": row_layout,
            "name_edit": name_edit,
            "tliphs_edit": tliphs_edit,
            "unit_combo": unit_combo,
            "mort_edit": mort_edit,
            "remove_btn": remove_btn,
        }
        def remove_this():
            self.remove_domain_row(row_dict)
        remove_btn.clicked.connect(remove_this)

        
        if preset:
            name_edit.setText(str(preset.get("name", "")))
            tliphs_edit.setText(str(preset.get("tliphs", "")))
            unit = str(preset.get("unit", "Day(s)"))
            if unit in UNIT_CONVERSION:
                unit_combo.setCurrentText(unit)
            mort_edit.setText(str(preset.get("mortality", "")))

        
        row_layout.addWidget(QLabel("Domain:"))
        row_layout.addWidget(name_edit, 2)
        row_layout.addWidget(QLabel("TLIPHS:"))
        row_layout.addWidget(tliphs_edit, 1)
        row_layout.addWidget(unit_combo, 1)
        row_layout.addWidget(QLabel("Mortality:"))
        row_layout.addWidget(mort_edit, 1)
        row_layout.addWidget(remove_btn)

        self.domains_layout.addLayout(row_layout)
        self.domain_rows.append(row_dict)

    def remove_domain_row(self, row_dict):
        
        layout = row_dict["layout"]
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        
        self.domains_layout.removeItem(layout)
        
        self.domain_rows = [r for r in self.domain_rows if r is not row_dict]

    def clear_domains(self):
        for row in list(self.domain_rows):
            self.remove_domain_row(row)

    
    def register_new_region(self):
        text, ok = QInputDialog.getText(self, "New Region", "Enter Region Name:")
        if ok and text.strip():
            region = text.strip()
            if region not in self.data:
                self.data[region] = {}
                self.region_list.addItem(region)
                self.region_input.setText(region)
                self.save_regions()
                self.save_data()
            else:
                QMessageBox.information(self, "Info", f"Region '{region}' already exists.")

    def delete_selected_region(self):
        selected = self.region_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Select a region to delete.")
            return
        region = selected.text()
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete region '{region}' and all its data?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            if region in self.data:
                del self.data[region]
            row = self.region_list.row(selected)
            self.region_list.takeItem(row)
            self.save_regions()
            self.save_data()
            if self.region_input.text().strip() == region:
                self.region_input.clear()
            QMessageBox.information(self, "Deleted", f"Region '{region}' deleted.")

    def load_regions(self):
        
        if os.path.exists(self.regions_file):
            with open(self.regions_file, 'r') as f:
                try:
                    region_list = json.load(f)
                    for region in region_list:
                        if region not in self.data:
                            self.data[region] = {}
                        self.region_list.addItem(region)
                except json.JSONDecodeError:
                    pass
        else:
            
            for region in self.data.keys():
                self.region_list.addItem(region)
            self.save_regions()

    def save_regions(self):
        with open(self.regions_file, 'w') as f:
            json.dump(list(self.data.keys()), f)

    def load_region_data(self, item):
        self.region_input.setText(item.text())

    def change_credentials(self):
        dlg = ChangeCredentialsDialog(self.username)
        dlg.exec_()

    
    def calculate_and_save(self):
        region = self.region_input.text().strip()
        if not region:
            QMessageBox.warning(self, "Input Error", "Please enter/select a region.")
            return

        date_str = self.date_input.date().toString("yyyy-MM-dd")

        age = safe_float(self.age_input.text(), None)
        pop = safe_float(self.pop_input.text(), None)
        le  = safe_float(self.le_input.text(), None)

        if age is None or pop is None or le is None or age <= 0 or pop <= 0 or le <= 0:
            QMessageBox.warning(self, "Input Error", "Enter valid positive values for Average Age, Population, and Life Expectancy.")
            return

        if le <= age:
            QMessageBox.warning(self, "Note", "Average Life Expectancy is less than or equal to Mean Age. The mortality term may be zero or negative. Proceeding.")

        
        dsavs = {}
        domains_detail = {}
        N = 0

        for row in self.domain_rows:
            name = row["name_edit"].text().strip()
            if not name:
                
                continue

            tliphs_val = safe_float(row["tliphs_edit"].text(), 0.0)
            unit = row["unit_combo"].currentText()
            mortality = safe_float(row["mort_edit"].text(), 0.0)

            tliphs_years = tliphs_val * UNIT_CONVERSION.get(unit, 1.0)
            dstlya = tliphs_years + (mortality * (le - age))
            
            dsav = (dstlya * 100.0) / (age * pop) if (age * pop) != 0 else 0.0

            dsavs[name] = dsav
            domains_detail[name] = {
                "TLIPHS": tliphs_val,
                "TLIPHS_unit": unit,
                "Mortality": mortality,
                "TLIPHS_years": tliphs_years,
                "DSTLYA": dstlya,
                "DSAV": dsav,
            }
            N += 1

        if N == 0:
            QMessageBox.warning(self, "No Domains", "Add at least one domain before calculating.")
            return

        nlhi = sum(dsavs.values()) / float(N)

        
        if region not in self.data:
            self.data[region] = {}
            self.region_list.addItem(region)
            self.save_regions()

        
        record = {
            "MeanAge": age,
            "Population": pop,
            "AvgLifeExpectancy": le,
            "domains": domains_detail,
            "DSAV": dsavs, 
            "NLHI": nlhi,
        }
        self.data[region][date_str] = record

        self.save_data()

        QMessageBox.information(
            self, "Success",
            f"Data saved for {region} on {date_str}.\nNLHI = {nlhi:.4f}"
        )

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    
    def view_dashboard(self):
        if not self.data:
            QMessageBox.warning(self, "No Data", "No data available to display.")
            return

        
        for region in self.data:
            if not self.data[region]:
                continue
            
            dates = sorted(self.data[region].keys())
            
            nlhi_values = [self._extract_nlhi(self.data[region][d]) for d in dates]

            
            domain_order = []
            domain_set = set()
            for d in dates:
                entry = self.data[region][d]
                dsav_map = self._extract_dsav_map(entry)
                for dom in dsav_map.keys():
                    if dom not in domain_set:
                        domain_set.add(dom)
                        domain_order.append(dom)

            if not domain_order:
                continue

            
            matrix = np.zeros((len(dates), len(domain_order)))
            for i, d in enumerate(dates):
                dsav_map = self._extract_dsav_map(self.data[region][d])
                for j, dom in enumerate(domain_order):
                    matrix[i, j] = dsav_map.get(dom, 0.0)

            
            fig, axs = plt.subplots(2, 1, figsize=(12, 8))
            axs[0].plot(dates, nlhi_values, marker='o')
            axs[0].set_title(f"NLHI Over Time - {region}")
            axs[0].set_ylabel("NLHI (avg DSAV %)")
            axs[0].grid(True)

            im = axs[1].imshow(matrix.T, aspect='auto', cmap='viridis')
            axs[1].set_title("DSAV Heatmap (Domains × Time)")
            axs[1].set_yticks(np.arange(len(domain_order)))
            axs[1].set_yticklabels(domain_order)
            axs[1].set_xticks(np.arange(len(dates)))
            axs[1].set_xticklabels(dates, rotation=45, ha='right')
            fig.colorbar(im, ax=axs[1], orientation='vertical', label='DSAV (%)')
            plt.tight_layout()
            plt.show()

    def _extract_nlhi(self, entry):
        
        if isinstance(entry, dict):
            if "NLHI" in entry:
                return safe_float(entry["NLHI"], 0.0)
            if "NLCHI" in entry:
                return safe_float(entry["NLCHI"], 0.0)
        return 0.0

    def _extract_dsav_map(self, entry):
        
        if isinstance(entry, dict):
            if "DSAV" in entry and isinstance(entry["DSAV"], dict):
                return {str(k): safe_float(v, 0.0) for k, v in entry["DSAV"].items()}
            if "domains" in entry and isinstance(entry["domains"], dict):
                return {str(k): safe_float(v.get("DSAV", 0.0), 0.0) for k, v in entry["domains"].items()}
        return {}


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted and login.successful_login:
        window = NLHIApp(login.username_input.text().strip())
        window.show()
        sys.exit(app.exec_())
