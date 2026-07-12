# ==============================================================================
# SCRIPT: LegalRev42a.py
# VERSION: 2026.07.12__15.28.35
# TARGET: Python 3.14.5
#
# <LICENSE>
# Copyright (C) 2026 pwshAgyjkcrg761
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
# <PROTECTED>
# ==============================================================================
# <AI>
# AI INSTRUCTIONS
# Copyright (c) 2026 pwshAgyjkcrg761
# License: MIT
# Source: https://codeberg.org/pwshAgyjkcrg761/AI_Instructions
#
# AI INSTRUCTIONS v2026.07.11__15.41.51 : 
#
# 1. MESSAGE STAMP: 
#    - Every response containing code MUST begin with a standalone version stamp.
#    - Use CHICAGO TIME (Central Time), 24-hour clock.
#    - Format: YYYY.MM.DD__HH.MM.SS.
#    - CRITICAL: Use the time provided in the prompt or at https://www.timeanddate.com/worldclock/usa/chicago. Ensure minutes are exact.
#
# 2. VERSION SNIPPET PROHIBITION:
#    - DO NOT provide code snippets, anchors, or steps to update the script's internal VERSION comment or $scriptVersion variable. 
#    - The user handles internal file versioning manually based on the Message Stamp.
#
# 3. SCRIPT OUTPUT (SURGICAL FIXES ONLY):
#    - Provide minimal, highly targeted, surgical edits. Do not rewrite large blocks or entire functions.
#    - Always use a codebox with a copy button.
#    - Multiple modifications MUST be presented strictly ONE step at a time. Wait for user confirmation before proceeding to the next step. 
#    - DO NOT modify or refactor any code inside <PROTECTED> tags.
#
# 4. VERBATIM ANCHOR PROTOCOL (FOR NOTEPAD++):
#    - To facilitate "Find" in Notepad++, always structure edits with:
#      - "Verbatim Anchor (Before)" - The exact lines of existing code immediately before the change.
#      - "Verbatim Anchor (After)" - The exact lines of existing code immediately after the change.
#      - "Snippet to REPLACE" - The exact code block to be deleted.
#      - "What to PASTE in its place" - The new code block to be inserted.
#    - Do not summarize, truncate, or refactor the existing code used as an anchor.
#    - Match spaces, comments, and symbols exactly as they appear in the file.
#
# 5. CONTENT PRESERVATION:
#    - Do not remove, modify, or strip out telemetry data or DevDebug information from any provided code.
# </AI>
# ==============================================================================
# </PROTECTED>

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
APP_VERSION = "2026.07.12__15.28.35"

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
            license_content = self.get_payload(self.config['license_mode'], self.config['license_source'])
            ai_content = self.get_payload(self.config['ai_mode'], self.config['ai_source'])

            # 3. Process Target Assets
            target_files = []
            for root, _, files in os.walk(dest_dir):
                for file in files:
                    if file.endswith(('.py', '.ps1')):
                        target_files.append(os.path.join(root, file))

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

    def get_payload(self, mode, source_path):
        if mode == 'url':
            self.log_signal.emit(f"Fetching remote content from: {source_path}")
            try:
                with urllib.request.urlopen(source_path, timeout=5) as response:
                    return response.read().decode('utf-8')
            except Exception as network_error:
                self.log_signal.emit(f"Network asset unavailable: {str(network_error)}. Looking for local fallback.")
                fallback_path = self.config['license_fallback'] if 'license_fallback' in self.config else self.config['ai_fallback']
                return self.read_local_file(fallback_path)
        else:
            return self.read_local_file(source_path)

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

        modified = False
        
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
        self.setWindowTitle("Boilerplate & Legal Block Deployer")
        self.resize(750, 600)
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # 1. Target Directory Section
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select the target working folder...")
        self.dir_input.textChanged.connect(self.update_destination_preview)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(btn_browse)
        
        self.preview_lbl = QLabel("Output Path: N/A")
        self.preview_lbl.setStyleSheet("color: #888; font-style: italic;")

        layout.addWidget(QLabel("<b>Target Project Location:</b>"))
        layout.addLayout(dir_layout)
        layout.addWidget(self.preview_lbl)
        layout.addSpacing(10)

        # 2. License Selection Configuration
        layout.addWidget(QLabel("<b>License Configuration Block:</b>"))
        lic_layout = QHBoxLayout()
        self.lic_combo = QComboBox()
        self.lic_combo.addItems(["MIT", "GNU GPLv3", "Apache 2.0"])
        
        self.lic_url_radio = QRadioButton("Remote URL")
        self.lic_file_radio = QRadioButton("Local File")
        self.lic_file_radio.setChecked(True)
        lic_group = QButtonGroup(self)
        lic_group.addButton(self.lic_url_radio)
        lic_group.addButton(self.lic_file_radio)

        self.lic_source_input = QLineEdit("licenses/gpl3.txt")
        
        lic_layout.addWidget(self.lic_combo)
        lic_layout.addWidget(self.lic_url_radio)
        lic_layout.addWidget(self.lic_file_radio)
        lic_layout.addWidget(self.lic_source_input, 1)
        layout.addLayout(lic_layout)
        layout.addSpacing(10)

        # 3. AI Instructions Selection Configuration
        layout.addWidget(QLabel("<b>AI Core Instructions Configuration Block:</b>"))
        ai_layout = QHBoxLayout()
        
        self.ai_url_radio = QRadioButton("Remote URL")
        self.ai_url_radio.setChecked(True)
        self.ai_file_radio = QRadioButton("Local File")
        ai_group = QButtonGroup(self)
        ai_group.addButton(self.ai_url_radio)
        ai_group.addButton(self.ai_file_radio)

        self.ai_source_input = QLineEdit("https://codeberg.org/pwshAgyjkcrg761/AI_Instructions/raw/branch/main/AI_Instructions.txt")
        
        ai_layout.addWidget(self.ai_url_radio)
        ai_layout.addWidget(self.ai_file_radio)
        ai_layout.addWidget(self.ai_source_input, 1)
        layout.addLayout(ai_layout)
        layout.addSpacing(15)

        # 4. Action Initialization Execution Area
        self.btn_execute = QPushButton("Initialize Boilerplate Refactor Sync")
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
            self.dir_input.setText(selected_dir)

    def update_destination_preview(self, text):
        if text.strip():
            base_name = os.path.basename(os.path.normpath(text))
            parent_dir = os.path.dirname(os.path.normpath(text))
            preview_path = os.path.join(parent_dir, f"{base_name}_update-LegalRev42a")
            self.preview_lbl.setText(f"Output Path: {preview_path}")
        else:
            self.preview_lbl.setText("Output Path: N/A")

    def start_processing(self):
        src = self.dir_input.text().strip()
        if not src or not os.path.exists(src):
            self.log_output.append("Error: Invalid or non-existent source workspace directory configuration.")
            return

        self.btn_execute.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_output.clear()

        config = {
            'src_dir': src,
            'update_license': True,
            'update_ai': True,
            'license_mode': 'url' if self.lic_url_radio.isChecked() else 'file',
            'license_source': self.lic_source_input.text().strip(),
            'license_fallback': "licenses/gpl3.txt",
            'ai_mode': 'url' if self.ai_url_radio.isChecked() else 'file',
            'ai_source': self.ai_source_input.text().strip(),
            'ai_fallback': "instructions_fallback.txt"
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