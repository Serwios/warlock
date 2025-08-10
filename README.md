# **Warlock Monitor** 🧙‍♂️  
*Lightweight CLI-based system monitoring and alerting with Telegram integration.*

---

## **Overview**
Warlock Monitor is a command-line tool for real-time system monitoring and alerting.  
It allows you to define flexible alert rules for various system metrics (CPU, memory, disk, network, etc.) and receive instant notifications via Telegram.  

Designed for developers, system administrators, and enthusiasts who value simplicity, extensibility.

---

## **Key Features**
- Monitors **10+ system metrics** including:
  - CPU usage
  - Memory usage
  - Disk usage
  - Disk I/O
  - Network traffic (send/receive)
  - System load average
  - Number of running processes
  - Swap usage
  - Uptime
  - Per-core CPU usage
  - And much more
- **Custom alert rules** based on thresholds and comparators
- **Telegram integration** for instant alerts
- Minimal dependencies, works on Linux and macOS
- Configuration via simple `YAML` files
- Modular design for easy extension

---

## **Installation**
### **Requirements**
- Python **3.8+**
- `pip` package manager

### **Install from source**

```bash
git clone https://github.com/<your-username>/warlock.git
cd warlock

# Recommended: create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS

# Upgrade pip and install package in editable mode
pip install --upgrade pip
pip install --editable .

# If you encounter the "externally-managed-environment" error
# ensure you are inside a virtual environment.
# Avoid using --break-system-packages unless you fully understand the risks.
```

| Command                                 | Description          |
| --------------------------------------- | -------------------- |
| `warlock m ls`                          | List all available system metrics |
| `warlock a cr`                          | Create a new alert interactively |
| `warlock a ls`                          | List all configured alerts |
| `warlock a rm <id>`                     | Remove an alert by its ID |
| `warlock r`                             | Run the monitoring loop with alerts |
| `warlock c -b <bot_token>`              | Set Telegram bot token |
| `warlock c -c <chat_id>`                | Set Telegram chat ID |
| `warlock c -b <bot_token> -c <chat_id>` | Set both bot token and chat ID |



## Author
Developed by @Serwios
