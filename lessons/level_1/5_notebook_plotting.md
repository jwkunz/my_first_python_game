# Introduction to Sympy for Symbolic Math (Level 1)

**Author** Dr. Jakob W. Kunzler

**Contact** jake.kunzler@gmail.com

**Last Updated** Nov 17 2025

**License** This curriculum is distributed under the creative commons license 4.0.

**Copyright Jakob W. Kunzler 2025**

## Scope

* Beginner students with high school and some college math and no prior programming expierence  
* 30 minutes of reading

## Introduction

The scientific Python ecosystem is built around three core libraries:

| Library        | Purpose                                                                           |
| -------------- | --------------------------------------------------------------------------------- |
| **NumPy**      | Fast arrays, linear algebra, random numbers                                       |
| **SciPy**      | Scientific computing: optimization, signal processing, interpolation, integration |
| **Matplotlib** | Plotting and visualization                                                        |

In Jupyter, these tools work together to create fast, interactive plots for scientific or educational work.

---

## Setup

Run this cell to import the essential tools:

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, optimize, interpolate
```

Enable inline plotting:

```python
%matplotlib inline
```

---

## Basic Plotting with Matplotlib

### Creating a simple line plot

Generate some data with NumPy:

```python
x = np.linspace(0, 10, 400)
y = np.sin(x)
```

Plot it:

```python
plt.figure(figsize=(8, 4))
plt.plot(x, y, label="sin(x)")
plt.title("Basic Sine Wave")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True)
plt.legend()
plt.show()
```

---

## Using NumPy for Data Generation

### Example: Noisy sine wave

```python
np.random.seed(0)
noise = 0.3 * np.random.randn(len(x))
y_noisy = y + noise

plt.figure(figsize=(8, 4))
plt.plot(x, y_noisy, '.', label="noisy data")
plt.plot(x, y, 'r', label="true signal")
plt.legend()
plt.title("Noisy Data Example")
plt.show()
```

---

## Using SciPy for Analysis

SciPy contains many useful tools. Below are three common ones:

---

## SciPy Signal Processing Example

### Smooth noisy data with a low-pass Butterworth filter

```python
# Design a low-pass filter
b, a = signal.butter(4, 0.1)  # 4th order, normalized cutoff 0.1
y_filtered = signal.filtfilt(b, a, y_noisy)

plt.figure(figsize=(8, 4))
plt.plot(x, y_noisy, '.', alpha=0.5, label="noisy")
plt.plot(x, y_filtered, 'k', linewidth=2, label="filtered")
plt.legend()
plt.title("Butterworth Low-Pass Filter")
plt.show()
```

---

## SciPy Interpolation Example

### Interpolate using a cubic spline

```python
# Pick sparse sample points
x_sparse = x[::20]
y_sparse = y_noisy[::20]

# Build cubic spline
spline = interpolate.CubicSpline(x_sparse, y_sparse)
y_interp = spline(x)

plt.figure(figsize=(8, 4))
plt.plot(x_sparse, y_sparse, 'o', label="sample points")
plt.plot(x, y_interp, 'r', label="cubic spline")
plt.legend()
plt.title("Cubic Spline Interpolation")
plt.show()
```

---

## SciPy Optimization Example

### Fit a sine function to noisy data

Define model:

```python
def sine_model(x, A, w, p, C):
    return A * np.sin(w*x + p) + C
```

Define error function and fit:

```python
params0 = [1, 1, 0, 0]  # initial guess

def error(params):
    A, w, p, C = params
    return np.sum((sine_model(x, A, w, p, C) - y_noisy)**2)

best_params = optimize.fmin(error, params0)
best_params
```

Plot the result:

```python
A, w, p, C = best_params
plt.figure(figsize=(8, 4))
plt.plot(x, y_noisy, '.', alpha=0.4, label="noisy")
plt.plot(x, sine_model(x, A, w, p, C), 'k', label="fitted model")
plt.legend()
plt.title("SciPy Optimization: Fitting a Sine Wave")
plt.show()
```

---

## Multiple Subplots

```python
fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

axes[0].plot(x, y_noisy, '.', label="noisy")
axes[0].set_title("Top plot")

axes[1].plot(x, y_filtered, 'r', label="filtered")
axes[1].set_title("Bottom plot")

for ax in axes:
    ax.grid(True)
    ax.legend()

plt.tight_layout()
plt.show()
```

---

## 3-D Plot Example

```python
from mpl_toolkits.mplot3d import Axes3D

X = np.linspace(-3, 3, 100)
Y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(X, Y)
Z = np.sin(np.sqrt(X**2 + Y**2))

fig = plt.figure(figsize=(8, 5))
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(X, Y, Z)
plt.title("3D Surface Plot")
plt.show()
```

---

## Summary

You now know how to:

*  Generate data with **NumPy**
*  Plot with **Matplotlib**
*  Filter, fit, and interpolate data using **SciPy**
*  Create multi-panel plots
*  Visualize 3-D surfaces

These are the core skills for scientific visualization in Python notebooks.
