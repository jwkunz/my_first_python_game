# Getting Started (Level 1)

**Author** Dr. Jakob W. Kunzler

**Contact** jake.kunzler@gmail.com

**Last Updated** Oct 26 2025

**License** This curriculum is distributed under the creative commons license 4.0.

**Copyright Jakob W. Kunzler 2025**

## Scope

* Beginner students grades 7 - 12 with no prior programming expierence  
* 45 minutes of reading
* 15 minutes of lab


## Objectives

* Learn about:
  * Python 
  * Distributions
  * Environments
  * Installing Packages
  * Scripts vs Jupyter Notebooks
* Set up a python environment using the [Anaconda](https://www.anaconda.com/) distribution 
* Write a simple "Hello World" in a jupyter notebook to prove things are working


## Instructions

1. Students should begin with the first parts of the lab by downloading and running the anaconda distribution.  
2. While waiting for the installation to complete, students should read the theory section focusing on the main concepts and skipping over the small details.  
3. Once the installer completes, students should proceed with the lab instructions to create the hello world jupyter notebook.  
4. After creating the notebook, students should return again to the theory section and focus on the smaller details.  
5. Lastly, students should then practice the commands described in the theory section on their own machines.


## Laboratory Instructions

This section describes to "get up" with Python using Anaconda.  If you have problems, see the troubleshooting guide at the end of this page.

### How to Download and Install Anaconda

**Anaconda** is free and works on **Windows**, **Mac**, and **Linux** computers. Follow these steps to get started!


#### Step 1: Go to the Anaconda Website

1. Open your web browser (like Chrome, Edge, or Safari).
2. Go to the official website: [https://www.anaconda.com/download](https://www.anaconda.com/download)
3. Click the **Download** button under **“Anaconda Distribution.”**


#### Step 2: Choose Your Operating System

You’ll see options for:

* **Windows**
* **Mac**
* **Linux**

Click on the one that matches your computer.


#### Step 3: Download the Installer

Download the version for **Python 3.x** (the most recent version).
You can choose between:

* **64-Bit Graphical Installer** — easiest for most users
* **64-Bit Command Line Installer** — for advanced users

Most students should pick the **Graphical Installer**.


#### Step 4: Install on Windows

1. Double-click the downloaded **.exe** file.
2. When the setup window opens, click **Next** and accept the license agreement.
3. Choose **Just Me** unless you share the computer with others who also need Anaconda.
4. Leave the installation location as the default, then click **Next**.
5. When asked about adding Anaconda to your PATH, **leave it unchecked** (the installer will handle it).
6. Click **Install** and wait for it to finish.
7. Click **Finish** to complete the setup.



#### Step 5: Install on Mac

1. Open the **.pkg** file you downloaded.
2. Follow the on-screen steps to install.
3. The installer will automatically set up everything you need.
4. When it’s done, close the installer.



#### Step 6: Install on Linux

1. Open a **terminal** window.
2. Navigate to the folder where you downloaded the **.sh** file.
3. Run this command (replace the filename with the one you downloaded):

   ```bash
   bash Anaconda3-2025.XX-Linux-x86_64.sh
   ```
4. Press **Enter** to review the license, then type **yes** to accept.
5. Press **Enter** again to confirm the install location.
6. When finished, close and reopen your terminal.
7. Type:

   ```bash
   conda list
   ```

   If you see a list of packages, your installation worked!



#### Step 7: Launch Anaconda

After installation, open **Anaconda Navigator** — a friendly app that helps you launch tools like:

* **Jupyter Notebook** (to write and run code)
* **Spyder** (a professional-style coding editor)
* **Anaconda Prompt** (for advanced command-line use)

You can find Anaconda Navigator:

* On **Windows**: In the Start Menu under “Anaconda3”
* On **Mac**: In your Applications folder
* On **Linux**: Type `anaconda-navigator` in the terminal



#### You’re Ready to Code!

Once Anaconda opens, you can start exploring Python. Try launching **Jupyter Notebook** and typing:

```python
print("Hello, Python!")
```

If it prints that message — congratulations, your setup is complete!


## Theory


### What is Python?

**Python** is a popular computer programming language that’s known for being **easy to read and easy to learn**. People use Python to create all kinds of programs — from simple games and websites to advanced tools that use **artificial intelligence**, **data science**, and **robotics**.

Unlike some programming languages that use lots of symbols and punctuation, Python uses **plain English words** and **simple structure**, which makes it great for beginners. At the same time, it’s powerful enough for professional programmers who build apps used by millions of people.

With Python, you can:

* Write code that **automates tasks** or solves math problems
* Create **games and graphics**
* Work with **data** to make charts or predictions
* Control **robots** or sensors
* Build **websites and apps**

Python encourages clear thinking and creativity. Learning Python helps students understand how computers “think” and teaches valuable problem-solving skills that apply in many areas — from science and engineering to art and business.



### What is a Python Distribution?

A **Python distribution** is a **package** that includes everything you need to start using Python — the main programming language, plus extra tools and libraries that make it easier to write and run programs.

Think of it like a **starter kit** for coding in Python. Instead of downloading Python and all the extra parts one by one, a distribution bundles them together so you can get started right away.

One of the most popular Python distributions is called **Anaconda**.

**Anaconda** is designed especially for students, scientists, and data analysts. It includes:

* The **Python language** itself
* Many useful **libraries** for math, science, and data (like NumPy, pandas, and Matplotlib)
* A program called **Jupyter Notebook**, which lets you write and run Python code in a friendly, interactive way
* **Conda**, a tool that helps you install and manage more Python packages easily

Anaconda makes learning and experimenting with Python simple because everything you need is already set up and ready to use. It’s a great choice for students who want to explore data, make graphs, or learn how programming connects to real-world problems.

### Jupyter Notebooks vs. Traditional Python Scripts

When you write Python programs, you can do it in **two main ways**:

1. Using a **Jupyter Notebook**
2. Writing a **Python script** (a file that ends in `.py`)

Both use the **same Python language**, but they’re designed for **different ways of working**.

#### What Is a Jupyter Notebook?

A **Jupyter Notebook** is an **interactive workspace** where you can write code, run it, and immediately see the results — all in the same window.

It’s organized into **cells**:

* Some cells contain **Python code**
* Other cells can contain **text**, **headings**, **math**, or even **images**

This makes notebooks perfect for:

* **Learning and experimenting** with code
* **Explaining** what your code does step-by-step
* **Creating projects** that mix code, notes, and graphs
* **Data science and visualization** (since you can show charts right below your code!)

💡 Example:
In one cell, you might write:

```python
x = 5
y = 3
x + y
```

When you run the cell, the notebook shows the answer **8** right below it.
You can then add another cell to explain what you did using Markdown text:

```
This calculation adds two numbers, 5 and 3, to get 8.
```


#### What Is a Python Script?

A **Python script** is a regular **text file** that contains Python code from start to finish — no separate cells, no built-in notes.
These files have names like `hello.py` or `game.py`.

You write your code in a **code editor** (like Spyder, VS Code, or IDLE), and when you’re ready, you **run the entire file at once**.

Python scripts are perfect for:

* **Larger programs** or projects
* **Games, apps, and automation**
* Code that will be **shared** or used by other people or systems

💡 Example:
A Python script might look like this:

```python
def greet(name):
    print(f"Hello, {name}!")

greet("Student")
```

When you run the script, it prints:

```
Hello, Student!
```



#### Key Differences

| Feature                  | **Jupyter Notebook**                    | **Python Script (.py)**                |
| ------------------------ | --------------------------------------- | -------------------------------------- |
| **Best for**             | Learning, exploring, data analysis      | Building programs and applications     |
| **Structure**            | Split into separate cells               | One continuous file                    |
| **Output**               | Shows results right below your code     | Shows results in a console or terminal |
| **Includes text & math** | Yes — great for notes and documentation | No — code only                         |
| **Run style**            | Run one cell at a time                  | Runs the whole file at once            |
| **File type**            | `.ipynb`                                | `.py`                                  |




#### When to Use Each

* Use **Jupyter Notebook** when you’re:

  * Learning new concepts
  * Doing math, graphs, or experiments
  * Writing a project you want to explain visually

* Use a **Python Script** when you’re:

  * Building something that needs to run automatically
  * Writing code others will use or install
  * Working on a big project with many files



#### Summary

Both Jupyter Notebooks and Python scripts help you write code —
but **Jupyter is like a science lab**, where you experiment and explain your thinking,
and a **Python script is like a finished machine**, ready to do its job efficiently.


### What Is a Python Environment?

A **Python environment** is like a **workspace** where all the tools and settings for your Python projects are kept.
It contains:

* The version of **Python** you’re using
* The **packages** (libraries and tools) you’ve installed
* The **settings** that tell Python how to run your code

You can think of a Python environment as a **sandbox** — a safe space where you can build and experiment without messing up other projects.

#### Why Environments Matter

Sometimes, different projects need **different tools or versions** of Python.
For example:

* One project might use **Python 3.10** and the **NumPy** library.
* Another project might use **Python 3.12** and a newer version of **NumPy**.

If both projects shared the same setup, they could **interfere** with each other — like two students using the same art supplies but needing different colors!

A Python environment keeps each project’s setup **separate** and **organized** so that everything works the way it should.

#### Types of Environments

There are usually two main kinds:

1. **Base Environment**

   * Created automatically when you install Anaconda.
   * Includes the most common libraries for science, math, and data.
   * Great for getting started.

2. **Custom Environments**

   * You create these when you need special tools for a project.
   * Each one can have its own version of Python and its own libraries.

Example:

```bash
conda create --name robotics python=3.11
conda activate robotics
```

This creates a new environment called **robotics** with Python 3.11 — perfect for experiments or coding robots!

#### Managing Environments

Here are some useful commands you can run in **Anaconda Prompt** (Windows) or **Terminal** (Mac/Linux):

| Action                        | Command                                 |
| -- | -- |
| Create a new environment      | `conda create --name myenv python=3.11` |
| List all environments         | `conda env list`                        |
| Switch to an environment      | `conda activate myenv`                  |
| Leave the current environment | `conda deactivate`                      |
| Remove an environment         | `conda env remove --name myenv`         |


#### Think of It Like This

A **Python environment** is like a **locker** for your project:

* You can fill it with just the tools you need.
* Everything stays neat and separate.
* You can open and close it anytime with `conda activate` and `conda deactivate`.

This keeps your coding projects organized, reliable, and easy to manage — especially as you start exploring more advanced programming topics.


### Using Conda to Manage and Install Packages

When you install **Anaconda**, you also get a powerful tool called **Conda**.
Conda helps you **install**, **update**, and **organize** the different **packages** (extra tools and libraries) that make Python so useful.

You can think of Conda like an **app store for Python**, but instead of games or social media apps, you’re installing tools for coding, math, science, or data analysis!


### Opening Conda

To use Conda, you’ll type commands into a special window called a **terminal** or **prompt**.

* **Windows:** Open the **Anaconda Prompt** (found in the Start Menu under “Anaconda3”).
* **Mac:** Open the **Terminal** app (found in Applications → Utilities).
* **Linux:** Open your system **Terminal**.

You’ll know it’s ready when you see a line that looks like this:

```
(base) C:\Users\YourName>
```

The word **(base)** means you’re in the main Conda environment.



### Checking What’s Installed

To see what packages are already available, type:

```bash
conda list
```

You’ll see a list of all the tools that came with Anaconda, such as **numpy**, **pandas**, and **matplotlib**.



### Installing a New Package

If you want to add a new library that’s not already installed, use this command:

```bash
conda install package_name
```

For example, to install a library called **seaborn** (used for making beautiful charts):

```bash
conda install seaborn
```

Conda will find it, download it, and set it up automatically.
You can also install more than one package at a time:

```bash
conda install numpy scipy matplotlib
```

### Updating Packages

To keep your tools up to date, you can tell Conda to update everything:

```bash
conda update --all
```

Or just one package:

```bash
conda update pandas
```

### Creating a Separate Environment

Sometimes you might want to try a new library or project without changing your main setup.
Conda lets you create a **separate environment** — like a sandbox where you can experiment safely.

Here’s how to create one called “test_env” with Python 3.11:

```bash
conda create --name test_env python=3.11
```

Then, to **activate** it:

* **Windows:**

  ```bash
  conda activate test_env
  ```
* **Mac/Linux:**

  ```bash
  conda activate test_env
  ```

When you’re done using it, switch back to the main base environment:

```bash
conda deactivate
```

You can see all your environments by typing:

```bash
conda env list
```

### **Removing a Package or Environment**

If you no longer need a package:

```bash
conda remove package_name
```

If you want to delete an entire environment:

```bash
conda env remove --name test_env
```

### Tips for Using Conda

* Always open the **Anaconda Prompt** or **Terminal** before using Conda.
* Use **Tab** to auto-complete package names — it saves time!
* Avoid using both **pip** and **conda** for the same environment unless you understand how they work together.


## Lab Troubleshooting Guide

If something doesn’t work the first time, don’t worry — it’s very common when setting up programming tools!
Here are some simple ways to fix the most common issues:



#### Problem 1: The Installer Won’t Open

**Possible cause:** Your computer’s security settings might be blocking it.

**Fix:**

* On **Windows**: Right-click the installer file and choose **“Run as administrator.”**
* On **Mac**: If you see a warning about unidentified developers, open **System Settings → Privacy & Security** and click **“Open Anyway.”**
* On **Linux**: Make sure the installer file is executable by running

  ```bash
  chmod +x Anaconda3-*.sh
  ```

  then try running it again.



#### Problem 2: The Installation Takes Too Long or Freezes

**Possible cause:** Anaconda is a large program (over 3 GB) and can take time to install, especially on older computers.

**Fix:**

* Be patient — it might take **10–20 minutes** to finish.
* Close other apps while installing.
* If it seems truly stuck, restart your computer and try again.



#### Problem 3: “Anaconda Navigator” Won’t Open (Windows)

**Fix:**

1. Open the **Start Menu** and search for **Anaconda Prompt**.
2. Click it to open a black command window.
3. Type:

   ```bash
   anaconda-navigator
   ```
4. Press **Enter.**
   If it opens, your installation works — you can use this method anytime.



#### Problem 4: Python or Conda Commands Don’t Work

**Possible cause:** The computer can’t find where Anaconda is installed.

**Fix:**

* Always open **Anaconda Prompt (Windows)** or **Terminal (Mac/Linux)** instead of the regular system prompt.
* Type:

  ```bash
  conda list
  ```

  If you see a list of packages, everything is set up correctly.

If you still get an error, try restarting your computer — this often helps the system recognize new software.



#### Problem 5: You Installed the Wrong Version

**Fix:**

1. Uninstall the old version:

   * **Windows:** Use *Add or Remove Programs* in Settings.
   * **Mac/Linux:** Delete the `anaconda3` folder from your home directory.
2. Download the latest **Anaconda Distribution** again from [https://www.anaconda.com/download](https://www.anaconda.com/download).
3. Reinstall following the earlier steps.



#### Problem 6: You See “Permission Denied” or “Access Denied” Errors

**Fix:**

* Try installing **“Just for Me”** instead of **“All Users”** on Windows.
* On Mac or Linux, use a user folder you have full permission to write to.
* Avoid installing in system folders like `/usr/bin` or `C:\Program Files`.



#### When All Else Fails

If nothing seems to work:

1. Visit [https://docs.anaconda.com/free/anaconda/](https://docs.anaconda.com/free/anaconda/) for official help.
2. Ask a teacher or classmate for assistance — sometimes a fresh pair of eyes can spot the problem!
3. As a last resort, uninstall and reinstall Anaconda from scratch.




