# ZMQ Ports (Level 2)

**Author** Dr. Jakob W. Kunzler

**Contact** jake.kunzler@gmail.com

**Last Updated** Nov 11 2025

**License** This curriculum is distributed under the creative commons license 4.0.

**Copyright Jakob W. Kunzler 2025**

## Scope

* Students with a basic understanding of the python language 
* 15 minutes of reading
* 15-30 minutes of lab

--- 

## Objectives

Learn:

* What the **ZeroMQ** library is.
* The different types of **communication models** (or “socket types”) it supports.
* Why the **Publisher/Subscriber (PUB/SUB)** model is so powerful.
* How these ideas apply to a simple chat program.
* How to apply these skills in a labratory exercise

---

## Theory

### What Is ZeroMQ?

**ZeroMQ**, often written as **ZMQ** or **ØMQ**, is a **messaging library** that helps two or more programs **talk to each other**, even if they are running on different computers.

You can think of it as a kind of **digital post office**:

* Each program is like a person with an address.
* ZMQ is the mail system that delivers their messages quickly and reliably.

The cool thing is — ZMQ works **across computers, networks, or even within one computer** — without needing to set up a big complicated server system.

---

### Why Use ZMQ?

Normally, to make two programs talk to each other, you’d use things like:

* **Sockets** in networking (which can be complicated).
* Or higher-level tools like **HTTP servers** (which can be slow or limited).

ZMQ gives you the **best of both worlds**:

* It’s as **fast** as a low-level socket.
* It’s as **easy** as sending a message with `.send()` and receiving with `.recv()`.

It does all the heavy lifting of managing connections, buffering, and retries — so you can focus on your program.

---

### Types of ZMQ Sockets

ZeroMQ uses **different socket types**, each representing a communication pattern.
Here are the main ones:

| Socket Type     | Pattern           | Description                                                                       | Example Use                         |
| --------------- | ----------------- | --------------------------------------------------------------------------------- | ----------------------------------- |
| **REQ / REP**   | Request–Reply     | A “question and answer” pair — one asks, one responds                             | Chatbot, command-response           |
| **PUB / SUB**   | Publish–Subscribe | One speaker (publisher) sends messages, many listeners (subscribers) receive them | News feed, stock ticker, group chat |
| **PUSH / PULL** | Pipeline          | One program pushes out tasks, another pulls them to work on                       | Task queues, data processing        |
| **PAIR / PAIR** | One-to-one        | Two programs connect directly, sending messages both ways                         | Direct chat between two devices     |

Let’s look closer at the one we’ll use for your **chat interface**.

---

### The PUB/SUB (Publish/Subscribe) Model

Imagine you’re the **DJ of a school radio station**.

* You (the DJ) are the **Publisher (PUB)**.
* The students listening in each classroom are the **Subscribers (SUB)**.

Whenever you send out an announcement, **everyone who is tuned in** hears it.
If someone isn’t subscribed, they don’t hear anything.

### Here’s How It Works in ZMQ:

* The **Publisher** socket uses `socket(zmq.PUB)` and sends messages with `.send_string()`.
* The **Subscriber** socket uses `socket(zmq.SUB)` and listens with `.recv_string()`.
* The Subscriber must tell ZMQ what kinds of messages to “subscribe” to.

For example:

```python
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
```

This means “receive **everything**.”
If we used `"weather"`, it would only receive messages starting with `"weather"`.

---

### How Messages Travel

When a Publisher sends a message:

1. It goes out to all the Subscribers who are connected.
2. The message can contain **text, numbers, or data** — anything you can send as a string.
3. The Subscribers each get their own copy.

You can even have **multiple Publishers and Subscribers** on a network:

* One message might come from your computer,
* Another from your friend’s,
* All arriving in real time.

That’s the foundation of **group chat**!

---

## 💡 Example — A Simple PUB/SUB Setup

Here’s a small example to show how this works.

**Publisher (the broadcaster):**

```python
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")  # Open a port on your computer

while True:
    message = input("Enter a message to publish: ")
    socket.send_string(message)
    print("Sent:", message)
```

**Subscriber (the listener):**

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")  # Connect to the publisher
socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages

print("Listening for messages...")
while True:
    message = socket.recv_string()
    print("Received:", message)
```

Run the subscriber first, then the publisher — and start typing!
You’ll see the messages appear in real time.

---

###  Why PUB/SUB Is Perfect for Chat

* Everyone connected can receive updates instantly.
* New subscribers can join any time.
* You can even use **topics** to separate rooms or channels.

  * Example: `"room1:Hello everyone!"`
  * Subscribers only listening to `"room1:"` will get it.

---

###  Summary

| Concept             | Description                                            |
| ------------------- | ------------------------------------------------------ |
| **ZeroMQ (ZMQ)**    | A fast library for messaging between programs          |
| **Socket types**    | Patterns like REQ/REP, PUB/SUB, PUSH/PULL, PAIR        |
| **PUB/SUB model**   | One-to-many broadcasting of messages                   |
| **Publisher**       | Sends messages                                         |
| **Subscriber**      | Listens for messages it cares about                    |
| **Why it’s useful** | Great for real-time chat, notifications, or data feeds |

---

## Lab Exercise

### Objective

Students will create and run two Python programs that use **ZeroMQ (ZMQ)** to send and receive messages in real time using the **Publish/Subscribe model**.

They’ll:

* Set up a Conda environment and install ZMQ.
* Create a **Publisher** and a **Subscriber** Python script.
* Run the programs on separate computers.
* Send messages across the network and observe real-time communication.


### Materials Needed

* Two computers connected to the **same local network (LAN)**.
* Python (3.8 or higher) installed.
* **Anaconda** or **Miniconda** installed.
* A terminal or command prompt window on each machine.

---

### Step 1: Create a Conda Environment

On **both computers**, open a terminal and create a new Conda environment for this project.

```bash
conda create -n zmqchat python=3.10 -y
```

Then activate it:

```bash
conda activate zmqchat
```

Check that you’re in the environment (your terminal should now start with `(zmqchat)`).

---

### Step 2: Install ZeroMQ

Install the Python bindings for ZeroMQ called **pyzmq**:

```bash
conda install pyzmq -y
```

You can check that it worked:

```bash
python -m zmq
```

If no error appears, ZMQ is installed correctly.

---

### Step 3: Find Your IP Address

On the **publisher’s computer**, you’ll need to know its **local IP address** so the subscriber can connect.

In the terminal, type:

```bash
hostname -I
```

This will print your computer’s local IP address, like:

```
192.168.1.12
```

Write it down — the **subscriber will use this IP** to connect.

---

### Step 4: Create the Publisher Program

On the **publisher’s computer**, open a new file named:

```
publisher.py
```

and paste this code inside:

```python
import zmq
import socket

# Show the computer's IP address for reference
host_ip = socket.gethostbyname(socket.gethostname())
print(f"Publisher running on host IP: {host_ip}")

context = zmq.Context()
socket = context.socket(zmq.PUB)

# Bind to all network interfaces on port 5555
socket.bind("tcp://*:5555")

print("Publisher ready. Type messages to broadcast.")
print("Press Ctrl+C to quit.\n")

try:
    while True:
        message = input("Enter message: ").strip()
        if message:
            socket.send_string(message)
            print(f"Sent: {message}")
except KeyboardInterrupt:
    print("\nPublisher shutting down...")
```

Save the file and exit the editor.

---

###  Step 5: Create the Subscriber Program

On the **subscriber’s computer**, open a new file named:

```
subscriber.py
```

and paste this code:

```python
import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)

# Replace 192.168.1.12 with your publisher's IP address
publisher_ip = "192.168.1.12"
socket.connect(f"tcp://{publisher_ip}:5555")

# Subscribe to all messages
socket.setsockopt_string(zmq.SUBSCRIBE, "")

print(f"Connected to publisher at {publisher_ip}")
print("Listening for messages...\n")

try:
    while True:
        message = socket.recv_string()
        print(f"Received: {message}")
except KeyboardInterrupt:
    print("\nSubscriber shutting down...")
```

⚠️ **Important:**
Make sure to change the line:

```python
publisher_ip = "192.168.1.12"
```

to match the **actual IP address** of the publisher’s computer from Step 3.

---

###  Step 6: Run the Chat

Now for the fun part!

#### On the Publisher Computer:

```bash
python publisher.py
```

You should see:

```
Publisher running on host IP: 192.168.1.12
Publisher ready. Type messages to broadcast.
```

#### On the Subscriber Computer:

```bash
python subscriber.py
```

You should see:

```
Connected to publisher at 192.168.1.12
Listening for messages...
```

Now type messages in the **publisher window**, and you’ll see them **appear instantly** on the subscriber’s terminal! 🎉

---

###  Step 7: Try It Both Ways (Optional Extension)

To make it a **two-way chat**, just **run both programs on both computers** — one as publisher and one as subscriber.

For example:

* Computer A runs both `publisher.py` and `subscriber.py` (connected to B’s IP)
* Computer B runs both `publisher.py` and `subscriber.py` (connected to A’s IP)

Each one can then both **send** and **receive** messages.

---

###  Step 8: Troubleshooting

| Problem                           | Possible Cause              | Solution                                                         |
| --------------------------------- | --------------------------- | ---------------------------------------------------------------- |
| Subscriber not receiving messages | Firewall blocking port 5555 | Temporarily disable firewall or allow port 5555                  |
| “Connection refused” error        | Wrong IP or port            | Double-check the publisher IP address                            |
| Typing messages but nothing shows | Subscriber not subscribed   | Ensure `socket.setsockopt_string(zmq.SUBSCRIBE, "")` is included |
| Conda command not found           | Conda not installed         | Install Anaconda or Miniconda first                              |

---

###  Step 9: Reflection Questions

1. What is the role of the **Publisher** in the PUB/SUB model?
2. How does a **Subscriber** know which messages to receive?
3. What would happen if you had multiple Subscribers?
4. How could this model be used in a **classroom chat system** or **notification system**?

---

### Step 10: Clean Up

When you’re done:

```bash
conda deactivate
```

You can remove the environment later with:

```bash
conda remove -n zmqchat --all
```

---

###  Optional Extension Challenges

Try these if you finish early:

1. Modify the subscriber to only receive messages that start with a certain keyword (like `"room1:"`).
2. Add colors to the messages using the `colorama` library.
3. Display timestamps for each message.
4. Create a script that logs all received messages into a text file.

