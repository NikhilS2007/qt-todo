import json
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QLabel, QStyle
)

DATA_FILE = Path("todo.json")

class TodoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt To-Do")
        self.resize(480, 520)

        self.input = QLineEdit(placeholderText="Add a task and press Enter…")
        self.btn_add = QPushButton("Add")
        self.btn_add.setDefault(True)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input)
        input_row.addWidget(self.btn_add)

        self.list = QListWidget()
        self.list.setAlternatingRowColors(True)
        self.list.setSelectionMode(QListWidget.NoSelection)
        self.list.itemChanged.connect(self.auto_save)
        self.list.itemDoubleClicked.connect(self.enable_inline_edit)

        self.btn_clear_done = QPushButton("Clear Completed")

        bottom_row = QHBoxLayout()
        bottom_row.addStretch(1)
        bottom_row.addWidget(self.btn_clear_done)

        self.status = QLabel("")
        self.status.setStyleSheet("color: #666; font-size: 12px;")

        root = QVBoxLayout(self)
        root.addLayout(input_row)
        root.addWidget(self.list)
        root.addLayout(bottom_row)
        root.addWidget(self.status)

        self.btn_add.clicked.connect(self.add_task)
        self.input.returnPressed.connect(self.add_task)
        self.btn_clear_done.clicked.connect(self.clear_completed)

        self.load(DATA_FILE)

        style = self.style()
        self.btn_add.setIcon(style.standardIcon(QStyle.SP_DialogYesButton))
        self.btn_clear_done.setIcon(style.standardIcon(QStyle.SP_DialogResetButton))

    def add_task(self):
        text = self.input.text().strip()
        if not text:
            return
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
        item.setCheckState(Qt.Unchecked)
        self.list.addItem(item)
        self.input.clear()
        self.auto_save()
        self.update_status()

    def clear_completed(self):
        i = 0
        while i < self.list.count():
            if self.list.item(i).checkState() == Qt.Checked:
                self.list.takeItem(i)
            else:
                i += 1
        self.auto_save()
        self.update_status()

    def enable_inline_edit(self, item: QListWidgetItem):
        self.list.editItem(item)

    def to_dict(self):
        tasks = []
        for i in range(self.list.count()):
            it = self.list.item(i)
            tasks.append({
                "text": it.text(),
                "done": (it.checkState() == Qt.Checked),
            })
        return {"tasks": tasks}

    def from_dict(self, data: dict):
        self.list.clear()
        for t in data.get("tasks", []):
            it = QListWidgetItem(t["text"])
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
            it.setCheckState(Qt.Checked if t.get("done") else Qt.Unchecked)
            self.list.addItem(it)
        self.update_status()

    def auto_save(self):
        try:
            DATA_FILE.write_text(
                json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            self.status.setText(f"Saved to {DATA_FILE.name}")
        except Exception as e:
            self.status.setText(f"Save failed: {e}")

    def load(self, path: Path):
        if not path.exists():
            self.status.setText("New list")
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.from_dict(data)
            self.status.setText(f"Loaded {path.name}")
        except Exception as e:
            QMessageBox.warning(self, "Load error", f"Could not read {path}:\n{e}")

    def update_status(self):
        total = self.list.count()
        done = sum(self.list.item(i).checkState() == Qt.Checked for i in range(total))
        self.status.setText(f"{done}/{total} completed")

def main():
    app = QApplication(sys.argv)
    w = TodoApp()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
