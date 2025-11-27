import os
import sys

# Import your real module
import cli
from cli import THEMES, create_pdf
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


# Worker Thread to run create_pdf() without freezing UI
class PdfWorker(QThread):
    finished = Signal(bool, str)  # success, message

    def __init__(self, args):
        super().__init__()
        self.args = args

    def run(self):
        try:
            success = create_pdf(**self.args)
            message = "PDF created successfully!" if success else "PDF creation failed."
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, str(e))


class CppdfGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("cppdf — GUI Wrapper")
        self.setMinimumWidth(650)

        layout = QVBoxLayout()

        # Code file picker

        file_row = QHBoxLayout()
        self.file_input = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)

        file_row.addWidget(QLabel("Input C++ file:"))
        file_row.addWidget(self.file_input)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        # Output PDF name + folder

        out_row = QHBoxLayout()
        self.out_input = QLineEdit()
        self.out_input.setPlaceholderText("submission")
        out_row.addWidget(QLabel("Output PDF name:"))
        out_row.addWidget(self.out_input)
        out_row.addWidget(QLabel(".pdf"))
        layout.addLayout(out_row)

        folder_row = QHBoxLayout()
        self.folder_label = QLabel("Folder: (default: code file folder)")
        folder_btn = QPushButton("Choose Folder")
        folder_btn.clicked.connect(self.choose_folder)
        folder_row.addWidget(self.folder_label)
        folder_row.addWidget(folder_btn)
        layout.addLayout(folder_row)

        self.output_folder = None  # store user-chosen folder

        # Student Metadata

        self.name_input = QLineEdit()
        self.title_input = QLineEdit()
        self.course_input = QLineEdit()

        layout.addWidget(QLabel("Student Name:"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Assignment Title:"))
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Course:"))
        layout.addWidget(self.course_input)

        # Theme dropdown

        self.theme_box = QComboBox()
        for theme in THEMES.keys():
            self.theme_box.addItem(theme)

        layout.addWidget(QLabel("Theme:"))
        layout.addWidget(self.theme_box)

        # Include project checkbox

        self.project_box = QCheckBox("Include entire project (recommended)")
        self.project_box.setChecked(True)
        layout.addWidget(self.project_box)

        # Run button

        run_btn = QPushButton("Generate PDF")
        run_btn.clicked.connect(self.run_cppdf)
        layout.addWidget(run_btn)

        # Output console

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        self.setLayout(layout)

    # File pickers
    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select C++ File", "", "*.cpp *.h *.hpp *.c"
        )
        if path:
            self.file_input.setText(path)
            # Auto-suggest PDF name based on code file
            base_name = os.path.splitext(os.path.basename(path))[0]
            self.out_input.setText(base_name)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.output_folder = folder
            self.folder_label.setText(f"Folder: {folder}")

    # Runners
    def run_cppdf(self):
        code_file = self.file_input.text().strip()
        if not code_file:
            self.console.append("ERROR: No input file selected.\n")
            return

        output_name = self.out_input.text().strip() or "submission"
        if not output_name.lower().endswith(".pdf"):
            output_name += ".pdf"

        output_dir = self.output_folder or os.path.dirname(code_file)
        output_pdf = os.path.join(output_dir, output_name)

        args = {
            "code_file": code_file,
            "output_pdf": output_pdf,
            "student_name": self.name_input.text().strip(),
            "assignment_title": self.title_input.text().strip(),
            "course": self.course_input.text().strip(),
            "include_project": self.project_box.isChecked(),
        }

        cli.SELECTED_THEME = self.theme_box.currentText()
        self.console.append("\nRunning cppdf...\n")

        self.worker = PdfWorker(args)
        self.worker.finished.connect(self.finish)
        self.worker.start()

    # When finished
    def finish(self, success, message):
        if success:
            self.console.append(f"SUCCESS: {message}\n")
            pdf_path = self.worker.args["output_pdf"]
            if pdf_path and os.path.exists(pdf_path):
                try:
                    if sys.platform.startswith("win"):
                        os.startfile(pdf_path)
                    elif sys.platform.startswith("darwin"):
                        import subprocess

                        subprocess.run(["open", pdf_path], check=False)
                    else:
                        import subprocess

                        subprocess.run(["xdg-open", pdf_path], check=False)
                    self.console.append(f"Opened PDF: {pdf_path}\n")
                except Exception as e:
                    self.console.append(f"ERROR: Could not open PDF: {e}\n")
            else:
                self.console.append("ERROR: PDF file not found to open.\n")
        else:
            self.console.append(f"ERROR: {message}\n")


# Entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CppdfGUI()
    window.show()
    sys.exit(app.exec_())
