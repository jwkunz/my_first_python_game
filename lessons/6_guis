# Building GUIs in Python (Level 3)

**Author** Dr. Jakob W. Kunzler

**Contact** jake.kunzler@gmail.com

**Last Updated** Nov 2 2025

**License** This curriculum is distributed under the creative commons license 4.0.

**Copyright Jakob W. Kunzler 2025**

## Scope

* Students with intermidiate python skills
* 45 minutes of reading
* 45 minutes of lab


## Objectives

By the end of this lesson, students will be able to:

1. Describe the difference between **immediate-mode** and **retained-mode** GUI systems.
2. Understand why **PySide / PyQt** uses an **immediate-mode** approach.
3. Identify the major components of a PySide GUI application.
4. Create a simple PySide application with a **button** and a **counter**.
5. Complete a lab exercise: build a tool that counts the number of words in a text box.

---

## Theory

### What is a GUI?

A **Graphical User Interface (GUI)** lets programs interact with people using windows, buttons, text boxes, sliders, and more.
Instead of typing into a terminal, users click and tap.

Qt (which PySide wraps) is one of the most popular GUI frameworks in the world.

---

### Two Styles of GUI Systems

#### A. Retained-Mode GUIs

A retained-mode GUI stores its **entire state** inside a scene graph (a hierarchy of UI objects).
The system “remembers” everything you draw.

Examples:

* Web browsers (DOM stores elements)
* Game engines (Unity, Godot using scenes)
* Some custom UI systems

In retained-mode, the programmer says:

* “Create a rectangle.”
* “Move it here.”
* “The engine will keep track of it forever.”

#### B. Immediate-Mode GUIs

In immediate-mode systems, the GUI is **redrawn every frame** (or every event).
You usually say:

* “Draw the label here.”
* “Draw the button here.”
* “If it's clicked, update X.”

The system does *not* store a large scene graph. Instead, the UI is reconstructed from scratch (logically) whenever needed.

Examples:

* Dear ImGui
* Some game engine debug UIs

#### How does PySide/PyQt fit in?

Qt is *kind of hybrid*, but **PySide behaves closest to an immediate-mode system**:

* You create widgets (buttons, text boxes).
* The layout engine draws them every time the window repaints.
* When signals fire (like button clicks), you redraw or update elements.
* The UI is not a persistent scene graph like a DOM.

This is why PyQt/PySide GUIs often feel “event-driven,” which is a classic immediate-mode style.

---

### Structure of a PySide GUI Program

Most PySide6 applications follow this pattern:

1. **Import** PySide6 modules.
2. Create a **QApplication** — the object that runs the event loop.
3. Define a **main window** (usually a subclass of `QWidget` or `QMainWindow`).
4. Put widgets inside layouts (like VBox or HBox).
5. Connect **signals** (like `button.clicked.connect(...)`).
6. Show the window.
7. Start the **event loop** with `app.exec()`.

---

### Using Qt Designer (optional)

Qt Designer is a drag-and-drop GUI tool included with Qt.

* You design windows visually (like building with LEGO).
* It outputs **.ui files** (an XML layout description).
* Python code can load these using:

```python
from PySide6.QtUiTools import QUiLoader
```

Or convert them to .py files using:

```
pyside6-uic mywindow.ui -o mywindow_ui.py
```

For this lesson we will write the code manually so students understand the fundamentals.

---

### Example: A Push Button Counter

We’ll build a GUI with:

* A label (“Count: 0”)
* A button (“Increment”)

When the button is pressed, the number increases.

---

### Complete Example Code

```python
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
import sys

class CounterWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.count = 0  # internal state

        # --- Create Widgets ---
        self.label = QLabel("Count: 0")
        self.button = QPushButton("Increment")

        # --- Connect Signals ---
        self.button.clicked.connect(self.increment_count)

        # --- Create Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        # --- Apply Layout ---
        self.setLayout(layout)

        # --- Window Title ---
        self.setWindowTitle("Button Counter")

    def increment_count(self):
        self.count += 1
        self.label.setText(f"Count: {self.count}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = CounterWindow()
    window.show()

    app.exec()
```

---

### Why This Program Works

#### 1. `CounterWindow` subclass

We create our own widget that represents the whole window.

#### 2. Widgets

* `QLabel` shows the current number.
* `QPushButton` triggers a signal when clicked.

#### 3. Signals

The line:

```python
self.button.clicked.connect(self.increment_count)
```

tells Qt:

> When the button is clicked, run the method `increment_count`.

#### 4. Layouts

Qt layouts automatically position widgets.

#### 5. Event Loop

`app.exec()` starts the system that listens for events (clicks, resizing, repainting).

---

### Summary

Students have now learned:

* What GUIs are and how they work.
* The difference between **immediate-mode** and **retained-mode** UIs.
* How PySide/PyQt uses a mostly immediate-mode event-driven system.
* The essential components of a PySide GUI program.
* How to build a basic window with buttons, labels, layouts, and signals.
* How to complete their own GUI project: a word-counting tool.


## Lab Exercise

### Objective

Create a GUI tool that counts the number of **words** in a text box.

---

### Required Features

Your GUI must include:

1. A large `QTextEdit` box for the user to type text.
2. A button labeled **"Count Words"**.
3. A label that displays the output:

   * Example: `"Word Count: 17"`
4. A function that:

   * Reads the text from the text box
   * Splits it into words
   * Updates the label

---

### Hints

#### A. Use the TextEdit widget

```python
from PySide6.QtWidgets import QTextEdit
```

#### B. Get text

```python
text = self.textbox.toPlainText()
```

#### C. Count words

A simple way:

```python
words = text.split()
count = len(words)
```

#### D. Update the label

```python
self.output_label.setText(f"Word Count: {count}")
```

---

### Starter Template (Fill In Key Parts)

```python
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QLabel, QVBoxLayout
import sys

class WordCounter(QWidget):
    def __init__(self):
        super().__init__()

        # TODO: Create widgets
        self.textbox = QTextEdit()
        self.button = QPushButton("Count Words")
        self.output_label = QLabel("Word Count: 0")

        # TODO: Connect button signal
        self.button.clicked.connect(self.count_words)

        # TODO: Layout
        layout = QVBoxLayout()
        layout.addWidget(self.textbox)
        layout.addWidget(self.button)
        layout.addWidget(self.output_label)
        self.setLayout(layout)

        self.setWindowTitle("Word Counter Tool")

    def count_words(self):
        # TODO: Implement logic
        text = self.textbox.toPlainText()
        count = len(text.split())
        self.output_label.setText(f"Word Count: {count}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = WordCounter()
    window.show()

    app.exec()
```


