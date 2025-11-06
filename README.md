# Roblox Automation Player - Dragon ball Rage

An automated bot designed to retrieve, train, and optimize your stats in Roblox — including intelligent Zenaki boost handling, stat tracking, and automatic recovery from in-game errors.

---

## ✨ Features

- **Smart Stat Management** – Automatically analyzes stats and selects the lowest stat to train.  
- **Zenaki Boost Automation** – Automatically updates Zenaki boost to allow progression to the next training level.  
- **Continuous Training** – Keeps training until the final Zenaki boost and maximum stats are reached.  
- **Level-Specific Adjustments** – Automatically uses the dragon when required for level 46 progression.  
- **Error Handling** – Detects runtime errors and restarts the game when possible.  
- **Safe Exit System** – Critical errors trigger an immediate and safe program termination.

---

## ⚙️ Setup

### Prerequisites

- Python 3.8 or higher  
- Playwright installed with **Chromium only**  
- Roblox desktop version  
- Proper coordinate capture setup  

---

### Installation

1. Clone or download the repository.  
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  
3. Ensure **Chromium** is installed (no need for other browsers):  
   ```bash
   playwright install chromium
   ```  
4. Verify Chromium exists at:  
   ```
   %LOCALAPPDATA%\ms-playwright\chromium-1187
   ```  
   *(If missing, install via Playwright as shown above.)*

---

## 🧩 Setup Notes

- **Coordinate Setup** – Configure your coordinates in `coordinates_data.json` using the **Capture Coordinates** script.  
  - 📍 **Training Limit** – To set this, capture any stat line from the training menu (e.g., “34M/50M”).  
  - ⚙️ **Error_code** – Optional parameter;  

- **Authentication Setup** – Add your **username and password** in `Authentication.json` to enable automatic recovery and login upon errors.  
  - 🔒 Credentials are stored **locally only** and used strictly for login purposes.

- **Game Preparation** – Ensure **all skills are reset** — otherwise, training may not behave as expected.  
- Confirm that the in-game option “Make sure \\” is **set to off** before launching.

---

## 🧠 Clarifications & Instructions

- To **start** the bot:
  ```bash
  python main.py
  ```
- To **pause** or **terminate**, press the **Delete** key.  
- Level 46 requires using the **Dragon** for Zenaki updates.  
- The bot automatically recovers from minor errors; critical ones will stop it safely.

---

## ⚠️ Safety Notes

- Safe exit protocols prevent corruption or repeated login loops.  
- Always test in a controlled environment before full automation.  
- Never share your authentication or state file.  
- If command keys (like **M** or **E**) don’t respond, wait briefly — Roblox may have a short input delay.

---

## 🧰 Troubleshooting

### Chromium not found
If Chromium is missing, reinstall it with:
```bash
playwright install chromium
```
Then verify the path:
```
%LOCALAPPDATA%\ms-playwright\chromium-1187
```

### Playwright not installed
If Playwright isn’t recognized, install it manually:
```bash
pip install playwright
```

### Authentication or coordinate errors
Ensure that:
- `Authentication.json` and `coordinates_data.json` exist in the project directory.  
- File names and paths are correct.  
- All credentials and coordinates are valid.

---

© 2025 Roblox Automation Player | Developed for automation and controlled stat training in Roblox Game Dragon Ball Rage.
