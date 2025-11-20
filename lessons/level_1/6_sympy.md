# Introduction to Sympy for Symbolic Math (Level 1)

**Author** Dr. Jakob W. Kunzler

**Contact** jake.kunzler@gmail.com

**Last Updated** Nov 17 2025

**License** This curriculum is distributed under the creative commons license 4.0.

**Copyright Jakob W. Kunzler 2025**

## Scope

* Beginner students grades 7 - 12 with no prior programming expierence  
* Students with high school and some college math
* 30 minutes of reading

## Objectives

SymPy is Python’s symbolic mathematics library. It lets you manipulate algebraic expressions, solve equations, take derivatives/integrals, and more — all exactly, not numerically.

This tutorial covers:

1. Installing & importing SymPy
2. Creating symbolic variables
3. Building expressions
4. Simplifying expressions
5. Differentiation & integration
6. Solving equations
7. Working with matrices
8. Pretty printing in Jupyter

---

## 1. Installation & Import

SymPy usually comes preinstalled in many Python/Jupyter setups. If you need to install:

```bash
pip install sympy
```

### In your notebook:

```python
import sympy as sp

# Enables pretty rendering of math expressions
sp.init_printing()
```

---

## 2. Creating Symbolic Variables

```python
x, y = sp.symbols('x y')
```

You can also specify assumptions:

```python
a = sp.symbols('a', positive=True)
```

---

## 3. Building Symbolic Expressions

```python
expr = x**2 + 3*x + 2
expr
```

More complicated:

```python
expr2 = sp.sin(x) * sp.exp(x) + x**3
expr2
```

---

## 4. Simplifying Expressions

SymPy has several simplifying tools:

```python
sp.simplify((x**2 - 1)/(x - 1))
```

Factor and expand:

```python
sp.factor(x**2 - 5*x + 6)

sp.expand((x + 2)*(x + 3))
```

Trig simplification:

```python
sp.simplify(sp.sin(x)**2 + sp.cos(x)**2)
```

---

## 5. Differentiation & Integration

### Derivatives:

```python
sp.diff(expr, x)
```

Higher-order derivative:

```python
sp.diff(sp.sin(x), x, 3)
```

### Integrals:

Indefinite:

```python
sp.integrate(sp.cos(x), x)
```

Definite:

```python
sp.integrate(sp.exp(-x), (x, 0, sp.oo))
```

---

## 6. Solving Equations

### Solve algebraic equation:

```python
sp.solve(x**2 - 4, x)
```

Solve symbolic linear equation:

```python
sp.solve(sp.Eq(3*x + 2, 11), x)
```

Systems of equations:

```python
f1 = x + y - 4
f2 = x - y - 2

sp.solve([f1, f2], [x, y])
```

---

## 7. Symbolic Matrices

Create a symbolic matrix:

```python
A = sp.Matrix([[1, x],
               [y, 2]])
A
```

Matrix algebra:

```python
A.det()
```

```python
A.inv()
```

Eigenvalues:

```python
A.eigenvals()
```

---

## 8. Pretty Printing in Jupyter

To display results in LaTeX-style output:

```python
sp.init_printing()
```

To manually pretty-print:

```python
sp.pprint(expr)
```

Or inline latex:

```python
sp.latex(expr)
```

---

## Final Example: Everything Together

Try this full cell:

```python
import sympy as sp
sp.init_printing()

x = sp.symbols('x')

expr = (x**2 - 1)/(x - 1)

display(sp.simplify(expr))

d = sp.diff(expr, x)
i = sp.integrate(expr, x)

solve_example = sp.solve(sp.Eq(x**2 + 3*x + 2, 0), x)

display(d)
display(i)
display(solve_example)
```


