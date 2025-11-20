# Introduction to Python Classes (Level 1)

**Author** Dr. Jakob W. Kunzler

**Contact** jake.kunzler@gmail.com

**Last Updated** Nov 2 2025

**License** This curriculum is distributed under the creative commons license 4.0.

**Copyright Jakob W. Kunzler 2025**

## Scope

* Beginner students grades 7 - 12 with no prior programming expierence  
* 15 minutes of reading

--- 

## Objectives

By the end of this lesson, students will learn:
*  What classes are
*  How to define them cleanly
*  Good style conventions
*  Useful dunder (“double-underscore”) methods
*  Examples they can experiment with

--- 

## Theory

### What is a Class?

A **class** is a blueprint for creating objects.
An **object** is an instance of a class, holding its own data (attributes) and behaviors (methods).

Classes allow us to:

* group data and functions together
* model real-world things (Students, Cars, BankAccounts, etc.)
* write cleaner, more reusable code

---

### A simple class representing a student:

```python
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def info(self):
        return f"{self.name} is in grade {self.grade}"
```

### Creating and using an object:

```python
s = Student("Alice", 8)
print(s.info())
```

---

### Anatomy of a Class

Inside a class we typically find:

1. **Attributes** — data that belongs to the object
2. **Methods** — functions that operate on the object's data
3. **Dunder methods** — special functions that define behavior for built-in Python operations

---

### Good Style for Writing Python Classes

Python has a style guide named **PEP 8**. Here is how it applies to classes:

#### Naming

* Class names use **CamelCase**:
  `Car`, `BankAccount`, `SodaMachineController`
* Attribute and method names use **snake_case**:
  `open_account()`, `add_student()`

####  Spacing

* One blank line after class docstring
* Two blank lines before starting a new class

####  Docstrings

Every class should have a short description:

```python
class BankAccount:
    """Simple bank account with deposit and withdrawal operations."""
```

#### Use `self` clearly

* Always use `self.attribute` so it’s obvious where data belongs.

#### Keep methods small

Each method should do one clear task.

---

### Dunder (Magic) Methods — What They Are

**Dunder methods** are special functions that start and end with double underscores:

Examples:

* `__init__` — initializer
* `__str__` — human-readable string
* `__repr__` — unambiguous developer string
* `__len__` — length
* `__eq__` — equality
* `__add__` — addition operator
* `__iter__`, `__next__` — iteration protocol

They allow your objects to behave like built-ins.

---

#### Example: Implementing Useful Dunder Methods

Here’s a clean example of a 2-D vector class:

```python
class Vector2D:
    """A simple 2D vector supporting length, printing, and addition."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector2D(x={self.x}, y={self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __len__(self):
        # length is the number of components
        return 2
```

### Usage:

```python
v1 = Vector2D(3, 4)
v2 = Vector2D(1, 2)

print(v1)       # calls __str__
print(repr(v1)) # calls __repr__

v3 = v1 + v2    # calls __add__
print(v3)
```

---

### Example: A Class With Behavior and Data

Let’s build something more real: a counter with good style.

```python
class Counter:
    """A simple incrementing counter."""

    def __init__(self, start=0):
        self.value = start

    def increment(self):
        """Increase the counter by 1."""
        self.value += 1

    def reset(self):
        """Reset the counter to zero."""
        self.value = 0

    def __str__(self):
        return f"Counter(value={self.value})"
```

Usage:

```python
c = Counter()
c.increment()
c.increment()
print(c)   # Counter(value=2)
c.reset()
print(c)
```

---

### When Should You Use a Class?

Use classes when:

* You have data AND functions that operate on that data
* You need many objects of the same “kind”
* You want to model something in the real world
* You want to extend or customize behavior

Do **not** use a class if:

* You just need a function
* You only need to group a few values (a dict or tuple is enough)

---

## Lab Exercise

**Write a class called `Book` that stores:**

* title
* author
* number of pages

Add methods:

1. `__str__` for nice printing
2. `is_long()` that returns True if pages > 300

Then create two book objects and compare them.


