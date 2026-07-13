# ==============================================================================
# SCRIPT: LegalRev42a.py
# VERSION: 2026.07.13__13.13.05
# TARGET: Python 3.14.5
#
# <LICENSE>
# GNU General Public License Version 3
# Copyright (C) 2026 dasfasdf
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
# </LICENSE>
# ==============================================================================
# <AI>
# <PROTECTED>
# ==============================================================================
# AI INSTRUCTIONS
# Copyright (c) 2026 pwshAgyjkcrg761
# License: MIT
# Source: https://codeberg.org/pwshAgyjkcrg761/AI_Instructions
#
# AI INSTRUCTIONS v2026.07.13__10.03.16 : 
#
# 1. MESSAGE STAMP: 
#    - Every response containing code MUST begin with a standalone version stamp.
#    - Use CHICAGO TIME (Central Time), 24-hour clock.
#    - Format: YYYY.MM.DD__HH.MM.SS.
#    - CRITICAL: Use the time provided in the prompt or at 
#      https://www.timeanddate.com/worldclock/usa/chicago. Ensure minutes are exact.
#
# 2. VERSION SNIPPET PROHIBITION:
#    - DO NOT provide code snippets, anchors, or steps to update the script's 
#      internal VERSION comment or $scriptVersion variable. 
#    - The user handles internal file versioning manually based on the Message Stamp.
#
# 3. SCRIPT OUTPUT (SURGICAL FIXES ONLY):
#    - Provide minimal, highly targeted, surgical edits. Do not rewrite large blocks or 
#      entire functions.
#    - Always use a codebox with a copy button.
#    - Multiple modifications MUST be presented strictly ONE step at a time. Wait for 
#      user confirmation before proceeding to the next step. 
#    - DO NOT modify or refactor any code inside <PROTECTED> tags.
#
# 4. VERBATIM ANCHOR PROTOCOL (FOR NOTEPAD++):
#    - To facilitate "Find" in Notepad++, always structure edits with:
#      - "Verbatim Anchor (Before)" - The exact lines of existing code immediately before 
#         the change.
#      - "Verbatim Anchor (After)" - The exact lines of existing code immediately after 
#         the change.
#      - "Snippet to REPLACE" - The exact code block to be deleted.
#      - "What to PASTE in its place" - The new code block to be inserted.
#    - Do not summarize, truncate, or refactor the existing code used as an anchor.
#    - Match spaces, comments, and symbols exactly as they appear in the file.
#
# 5. CONTENT PRESERVATION:
#    - Do not remove, modify, or strip out telemetry data or DevDebug information from any 
#      provided code.
# ==============================================================================
# </PROTECTED>
# </AI>

import sys
import os
import shutil
import urllib.request
import traceback
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, QRadioButton, 
    QButtonGroup, QProgressBar, QTextEdit, QFileDialog, QStyleFactory
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Easily maintainable application metadata configuration
APP_VERSION = "2026.07.13__13.13.05"

class UpdateWorker(QThread):
    progress_signal = pyqtSignal(int, str)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        src_dir = self.config['src_dir']
        base_name = os.path.basename(os.path.normpath(src_dir))
        parent_dir = os.path.dirname(os.path.normpath(src_dir))
        dest_dir = os.path.join(parent_dir, f"{base_name}_update-LegalRev42a")

        try:
            # 1. Duplicate Folder Structure Safely
            if os.path.exists(dest_dir):
                self.log_signal.emit(f"Removing existing target folder: {dest_dir}")
                shutil.rmtree(dest_dir)
            
            self.log_signal.emit(f"Copying workspace to: {dest_dir}")
            shutil.copytree(src_dir, dest_dir)
            
            # 2. Acquire Content Payloads
            license_content = self.get_payload(self.config['license_mode'], self.config['license_source'], 'license_fallback')
            ai_content = self.get_payload(self.config['ai_mode'], self.config['ai_source'], 'ai_fallback')

            # 3. Process Target Assets (Respecting Recursive Setting)
            target_files = []
            if self.config.get('recursive', True):
                for root, _, files in os.walk(dest_dir):
                    for file in files:
                        if file.endswith(('.py', '.ps1')):
                            target_files.append(os.path.join(root, file))
            else:
                # Non-recursive: only scan the immediate folder root files
                for file in os.listdir(dest_dir):
                    file_path = os.path.join(dest_dir, file)
                    if os.path.isfile(file_path) and file.endswith(('.py', '.ps1')):
                        target_files.append(file_path)

            if not target_files:
                self.finished_signal.emit(True, "Process completed. No editable .py or .ps1 files discovered.")
                return

            for index, file_path in enumerate(target_files):
                self.process_file(file_path, license_content, ai_content)
                progress_pct = int(((index + 1) / len(target_files)) * 100)
                self.progress_signal.emit(progress_pct, os.path.basename(file_path))

            self.finished_signal.emit(True, f"Successfully processed {len(target_files)} files.")

        except Exception as e:
            error_msg = f"Critical Error encountered:\n{str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(error_msg)
            self.finished_signal.emit(False, str(e))

    def get_payload(self, mode, source_path, fallback_key):
        if mode == 'url':
            self.log_signal.emit(f"Fetching remote content from: {source_path}")
            try:
                with urllib.request.urlopen(source_path, timeout=5) as response:
                    payload = response.read().decode('utf-8')
            except Exception as network_error:
                self.log_signal.emit(f"Network asset unavailable: {str(network_error)}. Looking for local fallback.")
                fallback_path = self.config.get(fallback_key, "")
                payload = self.read_local_file(fallback_path)
        else:
            payload = self.read_local_file(source_path)

        if fallback_key == 'license_fallback':
            if 'user_name' in self.config and self.config['user_name']:
                payload = payload.replace("<YOUR-NAME-HERE>", self.config['user_name'])
            if 'copyright_year' in self.config and self.config['copyright_year']:
                payload = payload.replace("<COPYRIGHT-YEAR>", self.config['copyright_year'])
        return payload

    def read_local_file(self, path):
        if not path or not os.path.exists(path):
            self.log_signal.emit(f"Warning: Payload path target assignment missing or invalid: {path}")
            return ""
        self.log_signal.emit(f"Reading localized configuration file: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def process_file(self, file_path, license_text, ai_text):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        import re
        modified = False
        
        if self.config['update_version'] and self.config['version_value']:
            # Targets both Python/Powershell comments (# VERSION:) and standard block formats
            new_ver = self.config['version_value']
            
            # Pattern matching # VERSION: followed by anything up to the end of the line
            content, count = re.subn(r'(#\s*VERSION:\s*).*', rf'\g<1>{new_ver}', content)
            if count > 0:
                modified = True
        
        # Injection Mechanism: Content Blocks wrapped cleanly inside comment tags
        if self.config['update_license'] and "# <LICENSE>" in content and "# </LICENSE>" in content:
            content = self.replace_tagged_block(content, "# <LICENSE>", "# </LICENSE>", license_text)
            modified = True

        if self.config['update_ai'] and "# <AI>" in content and "# </AI>" in content:
            content = self.replace_tagged_block(content, "# <AI>", "# </AI>", ai_text)
            modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)

    def replace_tagged_block(self, full_text, start_tag, end_tag, new_block):
        start_idx = full_text.find(start_tag) + len(start_tag)
        end_idx = full_text.find(end_tag)
        
        # Formulate and normalize lines with clean # character comment indentation
        raw_lines = new_block.strip().splitlines()
        formatted_lines = []
        for line in raw_lines:
            if line.strip() == "":
                formatted_lines.append("#")
            elif line.startswith("#"):
                formatted_lines.append(line)
            else:
                formatted_lines.append(f"# {line}")
                
        payload_string = "\n" + "\n".join(formatted_lines) + "\n"
        return full_text[:start_idx] + payload_string + full_text[end_idx:]


class ModernLegalUpdater(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LegalRev42a")
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        self.init_ui()
        self.read_settings()

    def read_settings(self):
        import json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(script_dir, "LegalRev42a_internal")
        config_path = os.path.join(config_dir, "LegalRev42a.config.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                if "geometry" in settings:
                    from PyQt6.QtCore import QByteArray
                    self.restoreGeometry(QByteArray.fromHex(settings["geometry"].encode('utf-8')))
                    if "dir_input" in settings:
                        self.dir_input.setText(settings["dir_input"])
                    if "name_input" in settings:
                        self.name_input.setText(settings["name_input"])
                    if "lic_combo" in settings:
                        self.lic_combo.setCurrentText(settings["lic_combo"])
                    if "version_input" in settings:
                        self.version_input.setText(settings["version_input"])
                    if "year_input" in settings:
                        self.year_input.setText(settings["year_input"])
                    # Legacy radio state bypassed
                    if "ai_source" in settings:
                        self.ai_source_input.setText(settings["ai_source"])
                    return
            except Exception:
                pass

        # Default first startup behavior: Center on screen without JSON
        self.resize(750, 600)
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        x = int(screen.x() + (screen.width() - size.width()) / 2)
        y = int(screen.y() + (screen.height() - size.height()) / 2)
        self.move(x, y)

    def closeEvent(self, event):
        import json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(script_dir, "LegalRev42a_internal")
        config_path = os.path.join(config_dir, "LegalRev42a.config.json")
        
        try:
            os.makedirs(config_dir, exist_ok=True)
            geom_hex = self.saveGeometry().toHex().data().decode('utf-8')
            settings = {
                "geometry": geom_hex,
                "dir_input": self.dir_input.text().strip(),
                "name_input": self.name_input.text().strip(),
                "lic_combo": self.lic_combo.currentText(),
                "version_input": self.version_input.text().strip(),
                "year_input": self.year_input.text().strip(),
                "ai_mode": "file",
                "ai_source": self.ai_source_input.text().strip()
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except Exception:
            pass
        super().closeEvent(event)

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # 1. Target Directory Section
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select the target working folder...")
        # Update preview and intercept manual typing to ensure backslash alignment
        def format_input_slashes(text):
            if "/" in text:
                # Store cursor location to keep typing natural
                pos = self.dir_input.cursorPosition()
                self.dir_input.setText(text.replace("/", "\\"))
                self.dir_input.setCursorPosition(pos)
            self.update_destination_preview(self.dir_input.text())
            
        self.dir_input.textChanged.connect(format_input_slashes)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(btn_browse)
        
        self.preview_lbl = QLabel("Output Path: N/A")
        self.preview_lbl.setStyleSheet("color: #888; font-style: italic;")

        layout.addWidget(QLabel("<b>Target Project Location:</b>"))
        layout.addLayout(dir_layout)
        layout.addWidget(self.preview_lbl)
        
        # Checkbox to toggle multi-tiered subfolder processing
        from PyQt6.QtWidgets import QCheckBox
        self.recursive_chk = QCheckBox("Process subfolders recursively")
        self.recursive_chk.setChecked(True) # Enabled by default to maintain previous behavior
        layout.addWidget(self.recursive_chk)
        layout.addSpacing(10)

        # 1b. Combine Licensee Name, Version, and Copyright into a Single Row
        from PyQt6.QtGui import QRegularExpressionValidator
        from PyQt6.QtCore import QRegularExpression

        metadata_row = QHBoxLayout()
        
        # Column 1: Licensee Name (Stretches to take more room)
        n_box = QVBoxLayout()
        n_box.addWidget(QLabel("<b>Licensee Name (<YOUR-NAME-HERE>):</b>"))
        self.name_input = QLineEdit("")
        n_box.addWidget(self.name_input)
        metadata_row.addLayout(n_box, 3) # Stretch factor 3
        
        # Column 2: Version Number
        v_box = QVBoxLayout()
        v_box.addWidget(QLabel("<b>Version Number:</b>"))
        self.version_input = QLineEdit("")
        v_box.addWidget(self.version_input)
        metadata_row.addLayout(v_box, 2) # Stretch factor 2
        
        # Column 3: Copyright Year (Fixed compact stretch)
        y_box = QVBoxLayout()
        y_box.addWidget(QLabel("<b>Copyright Year:</b>"))
        self.year_input = QLineEdit("2026")
        year_rx = QRegularExpression(r"^\d{4}$")
        self.year_input.setValidator(QRegularExpressionValidator(year_rx, self))
        self.year_input.setMaxLength(4)
        y_box.addWidget(self.year_input)
        metadata_row.addLayout(y_box, 1) # Stretch factor 1
        
        layout.addLayout(metadata_row)
        layout.addSpacing(10)

        # 2. License Selection Configuration
        layout.addWidget(QLabel("<b>License Configuration Block:</b>"))
        lic_layout = QHBoxLayout()
        self.lic_combo = QComboBox()
        self.lic_combo.addItems(["Apache 2.0", "CC BY 4.0", "CC0 1.0", "GNU GPLv3", "MIT"])
        
        self.lic_source_input = QLineEdit(r"LegalRev42a_internal\licenses\mit.txt")
        self.lic_source_input.setReadOnly(True)
        self.lic_source_input.setStyleSheet("background: transparent; border: none; color: #888; font-style: italic;")

        def toggle_license_source():
            selection = self.lic_combo.currentText()
            if selection == "MIT":
                self.lic_source_input.setText(r"LegalRev42a_internal\licenses\mit.txt")
            elif selection == "GNU GPLv3":
                self.lic_source_input.setText(r"LegalRev42a_internal\licenses\gpl3.txt")
            elif selection == "Apache 2.0":
                self.lic_source_input.setText(r"LegalRev42a_internal\licenses\apache2.txt")
            elif selection == "CC BY 4.0":
                self.lic_source_input.setText(r"LegalRev42a_internal\licenses\cca4.txt")
            elif selection == "CC0 1.0":
                self.lic_source_input.setText(r"LegalRev42a_internal\licenses\cc01.txt")

        self.lic_combo.currentTextChanged.connect(toggle_license_source)
        toggle_license_source()
        
        lic_layout.addWidget(self.lic_combo)
        lic_layout.addWidget(self.lic_source_input, 1)
        layout.addLayout(lic_layout)
        layout.addSpacing(10)

        # 3. AI Instructions Selection Configuration
        layout.addWidget(QLabel("<b>AI Core Instructions Configuration Block:</b>"))
        ai_layout = QHBoxLayout()
        
        self.ai_source_input = QLineEdit(r"LegalRev42a_internal\ai_instructions\AI_Instructions.txt")
        self.ai_source_input.setReadOnly(True)
        self.ai_source_input.setStyleSheet("background: transparent; border: none; color: #888; font-style: italic;")

        btn_download = QPushButton("Download AI Instructions Update")
        btn_download.clicked.connect(self.download_repository_updates)
        
        ai_layout.addWidget(btn_download)
        ai_layout.addWidget(self.ai_source_input, 1)
        layout.addLayout(ai_layout)
        layout.addSpacing(15)

        # 4. Action Initialization Execution Area
        self.btn_execute = QPushButton("Update Header")
        self.btn_execute.setStyleSheet("font-weight: bold; padding: 8px; background-color: #2b579a; color: white;")
        self.btn_execute.clicked.connect(self.start_processing)
        layout.addWidget(self.btn_execute)

        # Progress Status Metrics
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.status_lbl = QLabel("Status: Idle")
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_lbl)

        # Output Logs Context
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(QLabel("<b>Live Execution Logs:</b>"))
        layout.addWidget(self.log_output)

    def browse_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Identify Target Folder")
        if selected_dir:
            # Force standard Windows backslashes on selection
            self.dir_input.setText(os.path.normpath(selected_dir))

    def download_repository_updates(self):
        self.log_output.clear()
        self.log_output.append("Initiating repository asset update...")
        base_script_dir = os.path.dirname(os.path.abspath(__file__))
        
        import re
        from PyQt6.QtWidgets import QMessageBox

        url_instructions = "https://codeberg.org/pwshAgyjkcrg761/AI_Instructions/raw/branch/main/AI_Instructions.txt"
        local_dest = os.path.join(base_script_dir, "LegalRev42a_internal", "ai_instructions", "AI_Instructions.txt")

        local_version = None
        if os.path.exists(local_dest):
            try:
                with open(local_dest, 'r', encoding='utf-8') as lf:
                    local_content = lf.read()
                # Flexibly looks for "AI INSTRUCTIONS v" followed by numbers, dots, and underscores
                version_match = re.search(r'AI\s+INSTRUCTIONS\s+v([\d\._]+)', local_content, re.IGNORECASE)
                if version_match:
                    local_version = version_match.group(1).strip()
            except Exception as le:
                self.log_output.append(f"Debug Local Read Error: {str(le)}")

        self.log_output.append(f"Local version parsed: {local_version or 'None Found'}")
        self.log_output.append("Checking remote version string...")
        
        remote_version = None
        try:
            with urllib.request.urlopen(url_instructions, timeout=5) as response:
                head_bytes = response.read(4096)  # Increase buffer to be absolutely sure we capture it
                head_text = head_bytes.decode('utf-8', errors='ignore')
                remote_match = re.search(r'AI\s+INSTRUCTIONS\s+v([\d\._]+)', head_text, re.IGNORECASE)
                if remote_match:
                    remote_version = remote_match.group(1).strip()
        except Exception as check_err:
            self.log_output.append(f"Unable to parse remote headers: {str(check_err)}.")

        self.log_output.append(f"Remote version parsed: {remote_version or 'None Found'}")

        if local_version and remote_version and local_version == remote_version:
            self.log_output.append(f"Local content version ({local_version}) matches remote repository version exactly.")
            self.status_lbl.setText("Repository sync bypassed. Current version up to date.")
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Update Status")
            msg_box.setText("No Update Necessary you have the latest version.")
            msg_box.setIcon(QMessageBox.Icon.NoIcon)
            # Override standard sound mapping by resetting the window type hints prior to execution
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.CustomizeWindowHint)
            msg_box.exec()
            return
        
        try:
            os.makedirs(os.path.dirname(local_dest), exist_ok=True)
            self.log_output.append(f"Downloading core instructions from: {url_instructions}")
            
            with urllib.request.urlopen(url_instructions, timeout=10) as response:
                content = response.read()
                
            with open(local_dest, 'wb') as f:
                f.write(content)
                
            self.log_output.append(f"[SUCCESS] Core asset refreshed locally at: {local_dest}")
            self.status_lbl.setText("Repository sync complete.")
            
            display_version = remote_version if remote_version else "latest"
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Update Status")
            msg_box.setText(f"Updated AI_Instructions.txt to {display_version}.")
            msg_box.setIcon(QMessageBox.Icon.NoIcon)
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.CustomizeWindowHint)
            msg_box.exec()
        except Exception as e:
            self.log_output.append(f"[ERROR] Asset sync failed: {str(e)}")
            self.status_lbl.setText("Sync failed.")

    def update_destination_preview(self, text):
        if text.strip():
            normalized = os.path.normpath(text.strip())
            base_name = os.path.basename(normalized)
            parent_dir = os.path.dirname(normalized)
            preview_path = os.path.join(parent_dir, f"{base_name}_update-LegalRev42a")
            # Force all slashes to native Windows backslashes for visual consistency
            self.preview_lbl.setText(f"Output Path: {preview_path.replace('/', '\\')}")
        else:
            self.preview_lbl.setText("Output Path: N/A")

    def start_processing(self):
        src = self.dir_input.text().strip()
        if not src or not os.path.exists(src):
            self.log_output.append("Error: Invalid or non-existent source workspace directory configuration.")
            return

        selected_lic = self.lic_combo.currentText()
        year_text = self.year_input.text().strip()
        
        if selected_lic != "CC0 1.0":
            if not self.name_input.text().strip() or not year_text:
                self.log_output.append("Error: Both Licensee Name and Copyright Year are required for the selected license.")
                return
            if len(year_text) != 4 or not year_text.isdigit():
                self.log_output.append("Error: Copyright Year must be exactly 4 digits.")
                return
        self.progress_bar.setValue(0)
        self.log_output.clear()

        base_script_dir = os.path.dirname(os.path.abspath(__file__))
        resolved_license_path = os.path.join(base_script_dir, self.lic_source_input.text().strip())

        config = {
            'src_dir': src,
            'update_version': True,
            'version_value': self.version_input.text().strip(),
            'update_license': True,
            'update_ai': True,
            'license_mode': 'file',
            'license_source': os.path.abspath(resolved_license_path),
            'license_fallback': os.path.abspath(resolved_license_path),
            'ai_mode': 'file',
            'ai_source': os.path.join(base_script_dir, "LegalRev42a_internal", "ai_instructions", "AI_Instructions.txt"),
            'ai_fallback': os.path.join(base_script_dir, "LegalRev42a_internal", "instructions_fallback.txt"),
            'user_name': self.name_input.text().strip(),
            'copyright_year': self.year_input.text().strip(),
            'recursive': self.recursive_chk.isChecked()
        }

        self.worker = UpdateWorker(config)
        self.worker.progress_signal.connect(self.handle_progress)
        self.worker.log_signal.connect(self.handle_logs)
        self.worker.finished_signal.connect(self.handle_completion)
        self.worker.start()

    def handle_progress(self, val, filename):
        self.progress_bar.setValue(val)
        self.status_lbl.setText(f"Processing structural layout content updates: {filename}")

    def handle_logs(self, message):
        self.log_output.append(message)

    def handle_completion(self, success, summary):
        self.btn_execute.setEnabled(True)
        if success:
            self.status_lbl.setText("Execution Complete Workflow Process Succeeded.")
            self.log_output.append(f"\n[SUCCESS] {summary}")
        else:
            self.status_lbl.setText("Execution Interrupted Due to Fatal Fault Protocol.")
            self.log_output.append(f"\n[FAILURE] Run halted: {summary}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernLegalUpdater()
    window.show()
    sys.exit(app.exec())