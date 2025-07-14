# Claude Snip Helper

📸 Instantly save screenshots and paste them into Claude CLI on Windows with `Ctrl + V`, without disrupting your normal clipboard usage.

This lightweight tool listens for `Win + Shift + S` snips (via the Windows Snipping Tool), and when you left-click inside **VS Code**, it saves the screenshot as a `.png` file and copies the file path to your clipboard.

Perfect for quickly pasting images into Claude CLI or any tool that supports path-based image input.

---

## ✅ Features

- 🪟 **Windows only** (uses Windows clipboard + GUI APIs)
- 💬 Designed for **Claude CLI**
- 🖱️ Activates when clicking in **VS Code**
- 🧠 Ignores synthetic clicks after snipping
- 📋 **Clipboard-friendly**: if you paste the image in another app first, it won’t overwrite the clipboard
- 🔒 Prevents multiple instances using a local TCP lock

---

## 💡 How It Works

1. Press `Win + Shift + S` to take a screenshot (snip)
2. Left-click inside **VS Code**
3. The image is saved to `Pictures\Screenshots`
4. The file path is copied to your clipboard
5. You can now paste (`Ctrl + V`) into **Claude CLI**

---

## 📦 Installation

1. Clone the repo:

git clone https://github.com/jacobhallgren/claude-snip-helper.git
cd claude-snip-helper

2.  Install required Python packages:
pip install -r requirements.txt

3.  python claude_snip_helper.py
python claude_snip_helper.py

## 🎁  Bonus

Start automatically 

## ⚙️ Auto-Start at Login (via Windows Task Scheduler)

To make Claude Snip Helper run automatically every time you log into Windows, you can configure it using **Task Scheduler**. This ensures the script runs silently in the background without needing to start it manually.

---

### ✅ Step-by-Step Instructions

#### 1. Open Task Scheduler
- Press `Win + S`, search for **Task Scheduler**, and open it.

#### 2. Create a New Task
- Click **"Create Task"** in the right panel (not "Basic Task").
- Name it something like: Start Claude Snip Helper

#### 3. General Tab
- Use your username under **"When running the task..."**
- Check:
- ✅ “Run only when user is logged on”
- ✅ “Run with highest privileges”
- Configure for: **Windows 10** or **Windows 11**

> ![General Tab](assets/general-tab.png)


#### 4. Triggers Tab
- Click **"New..."**
- **Begin the task**: `At log on`
- Choose:
- ✅ “Any user” *(or choose your username)*
- ✅ Enable the trigger
- You can optionally set a **delay** (e.g., 15 minutes)

> ![Triggers Tab](assets/trigger-tab.png)


#### 5. Actions Tab
- Click **"New..."**
- **Action**: `Start a program`
- **Program/script**: path to `pythonw.exe`  
Example: C:\Program Files\Python312\pythonw.exe

**Add arguments**: full path to your script  
Example: "C:\Users\YourName\Documents\Claude-Snip-Helper\claude_snip_helper.py"

#### 6. Conditions & Settings Tabs
- Leave defaults unless you want to adjust advanced behavior (e.g., stop after 3 days)


#### ✅ Done!
Click **OK** to save the task.

Now, your script will launch silently each time you log in to Windows. It will wait for `Win + Shift + S` snips and help you paste screenshots into Claude CLI with zero manual setup.
