# Python Fundamentals (Level 1)

**Author** Dr. Jakob W. Kunzler

**Contact** jake.kunzler@gmail.com

**Last Updated** Nov 2 2025

**License** This curriculum is distributed under the creative commons license 4.0.

**Copyright Jakob W. Kunzler 2025**

## Scope

* Beginner students grades 7 - 12 with no prior programming expierence  
* 60 minutes of reading


## Objectives

By the end of this lesson, students will learn the basics of the python language through small examples.

---

### Variables

A **variable** is a name that stores a value.

Python automatically decides the type based on the value you assign.

```python
x = 10          # integer
pi = 3.14159    # float
name = "Alice"  # string
is_student = True   # boolean

print(x, pi, name, is_student)
```

Variables can change value:

```python
x = 5
x = x + 2   # now x is 7
```

---

### Basic Data Types

Python has several built-in types you will use often:

| Type    | Example            | Notes                 |
| ------- | ------------------ | --------------------- |
| `int`   | `42`               | Whole numbers         |
| `float` | `3.14`             | Numbers with decimals |
| `str`   | `"hello"`          | Text                  |
| `bool`  | `True`, `False`    | Logic values          |
| `list`  | `[1, 2, 3]`        | Collection of items   |
| `dict`  | `{"a": 1, "b": 2}` | Key–value pairs       |

---

### Lists

A **list** holds multiple items in order.

```python
numbers = [10, 20, 30]
print(numbers)
```

You can access items by index (starting at zero):

```python
print(numbers[0])  # 10
```

You can modify lists:

```python
numbers.append(40)
numbers[1] = 25
print(numbers)
```

Looping through a list:

```python
for n in numbers:
    print(n)
```

---

### Loops

#### For loops

Used to repeat a block of code a known number of times:

```python
for i in range(5):
    print("Hello", i)
```

#### While loops

Repeat until a condition becomes false:

```python
count = 0
while count < 3:
    print("Count is", count)
    count += 1
```

---

### Functions

Functions group code into reusable blocks.

```python
def greet(name):
    print("Hello,", name)

greet("Alice")
greet("Bob")
```

Functions can return values:

```python
def square(x):
    return x * x

print(square(5))
```

---

### Conditionals

Use `if`, `elif`, and `else` to make decisions.

```python
age = 15

if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teen")
else:
    print("Child")
```

---

### Importing Libraries

Python has many built-in and external libraries you can import.

```python
import math

print(math.sqrt(16))
```

You can give a module a shortcut name:

```python
import numpy as np
print(np.arange(5))
```

Or import specific functions:

```python
from math import sin, cos
print(sin(0))
```

---

### File Input / Output (I/O)

#### Writing to a file

```python
with open("output.txt", "w") as f:
    f.write("Hello world!\n")
    f.write("This is a file.\n")
```

#### Reading from a file

```python
with open("output.txt", "r") as f:
    for line in f:
        print("Line:", line.strip())
```

`with open(...)` automatically closes the file when done.

---

### The if __name__ == __main__ Pattern

This is a special Python idiom that allows a file to be:

1. **Run directly**, or
2. **Imported as a module** without automatically running the main code.

Example:

```python
def main():
    print("Running main program logic!")

def helper():
    print("Helper function")

if __name__ == "__main__":
    main()   # Only runs if file is executed directly
```

Why useful?

* You can test code in one file.
* Other files can import your functions without triggering the main code.

It is best practice to write your code in small testible chunks that can "unit tested" in the main section.

---

### Comments

Use comments to explain your code:

```python
# This is a single-line comment

"""
This is a multi-line comment (technically a string literal).
Useful for documentation.
"""
```

---

### Tuples

Like lists but cannot be changed:

```python
point = (3, 4)
```
---

### Dictionaries

Store data as key–value pairs:

```python
student = {
    "name": "Bob",
    "age": 16,
    "grade": "A"
}

print(student["name"])
```
---

### List Comprehensions

A shorthand for building lists:

```python
squares = [x*x for x in range(10)]
```
---

### Putting It All Together — Example Mini Program

Here is a simple program combining variables, input, lists, loops, functions, and file I/O.

```python
def load_names(filename):
    """Load a list of names from a file."""
    names = []
    with open(filename, "r") as f:
        for line in f:
            names.append(line.strip())
    return names

def greet_all(names):
    """Greet every name in the list."""
    for name in names:
        print("Hello,", name)

def main():
    print("Loading names...")
    names = load_names("names.txt")
    greet_all(names)
    print("Done!")

if __name__ == "__main__":
    main()
```







