##Real-Time Automation & Data Processor

A complex automation system designed for **real-time stat optimization and task management in a simulated environment**. Built to demonstrate multithreaded logic, asynchronous processing, and data-driven decision making.

---

## Key Features

* **Smart Resource Management** – Automatically tracks and optimizes target metrics to maximize efficiency.
* **Boost & Enhancement Automation** – Monitors and applies resource enhancements to maintain optimal progression.
* **Continuous Operation** – Multithreaded system executes tasks and data capture concurrently in real time.
* **Dynamic Error Handling** – Detects runtime issues and recovers automatically or exits safely in critical cases.
* **Configurable Parameters** – Allows easy adjustment of thresholds, coordinates, and operational limits via JSON configuration files.

---

## Technologies Used

* **Languages:** Python 3.8+
* **Automation & Tools:** Playwright, Multithreading, JSON mapping, Logging & Error Handling
* **Libraries:** MSS (real-time screen capture), OpenCV (image filtering), PyTesseract (text extraction)
* **Development Practices:** Modular architecture, asynchronous programming (Async/Await), robust error management

---

## Setup & Installation

1. Clone or download the repository:
```bash
git clone https://github.com/meidan1200-wq/Dragon-ball-Rage-Automator.git
```
2. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```
3. Configure system parameters in `coordinates_data.json` and `Authentication.json`.
4. Run the automation engine:
```bash
python main.py
```
5. **Pause or stop execution:** Press the `Delete` key.

---

## Notes

* Safe exit protocols prevent data corruption or unintended loops.
* Always test in a controlled environment before full-scale execution.
* Credentials are stored locally only and used strictly for authentication.

---

## Learning Outcomes

* Design and implement **multithreaded automation pipelines**
* Build **asynchronous systems** coordinating multiple input streams
* Integrate **real-time data capture and processing**
* Apply **robust error handling and recovery mechanisms**
