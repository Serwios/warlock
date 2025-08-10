import asyncio
import logging
import time
from typing import List, Dict, Tuple, Optional
import psutil
from telegram import Bot
import uuid

from .config import load_config, save_config

logger = logging.getLogger(__name__)

METRICS = [
    "cpu_percent",
    "memory_percent",
    "swap_percent",
    "disk_percent_root",
    "disk_read_MBps",
    "disk_write_MBps",
    "net_sent_MBps",
    "net_recv_MBps",
    "process_count",
    "uptime_minutes",
]

class Monitor:
    def __init__(self, alerts: List[Dict], bot: Optional[Bot] = None, chat_id: Optional[str] = None):
        self.alerts = alerts
        self.bot = bot
        self.chat_id = chat_id
        self.prev_disk_io = psutil.disk_io_counters()
        self.prev_net_io = psutil.net_io_counters()

    def get_metrics(self) -> Tuple[Dict[str, float], None]:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        swap = psutil.swap_memory().percent
        disk_root = psutil.disk_usage("/").percent

        disk_io = psutil.disk_io_counters()
        read_MBps = (disk_io.read_bytes - self.prev_disk_io.read_bytes) / (1024 * 1024)
        write_MBps = (disk_io.write_bytes - self.prev_disk_io.write_bytes) / (1024 * 1024)

        net_io = psutil.net_io_counters()
        sent_MBps = (net_io.bytes_sent - self.prev_net_io.bytes_sent) / (1024 * 1024)
        recv_MBps = (net_io.bytes_recv - self.prev_net_io.bytes_recv) / (1024 * 1024)

        proc_count = len(psutil.pids())
        uptime_minutes = int(time.time() - psutil.boot_time()) // 60

        self.prev_disk_io = disk_io
        self.prev_net_io = net_io

        metrics = {
            "cpu_percent": cpu,
            "memory_percent": mem,
            "swap_percent": swap,
            "disk_percent_root": disk_root,
            "disk_read_MBps": read_MBps,
            "disk_write_MBps": write_MBps,
            "net_sent_MBps": sent_MBps,
            "net_recv_MBps": recv_MBps,
            "process_count": proc_count,
            "uptime_minutes": uptime_minutes,
        }
        return metrics

    def check_alerts(self, metrics: Dict[str, float]) -> List[Dict]:
        triggered = []
        for alert in self.alerts:
            metric_value = metrics.get(alert["metric"])
            if metric_value is None:
                logger.warning(f"Metric '{alert['metric']}' not found for alert '{alert['name']}'")
                continue
            comp = alert["comparator"]
            threshold = alert["threshold"]
            if comp == ">" and metric_value > threshold:
                triggered.append(alert)
            elif comp == "<" and metric_value < threshold:
                triggered.append(alert)
        return triggered

    async def send_telegram(self, message: str):
        if self.bot is None or self.chat_id is None:
            logger.error("Telegram bot or chat_id not configured")
            return
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    async def run(self, interval: int = 5):
        logger.info("Starting system monitor...")
        while True:
            metrics = self.get_metrics()
            triggered = self.check_alerts(metrics)
            for alert in triggered:
                val = metrics[alert["metric"]]
                logger.info(f"Alert triggered: {alert['name']} with value {val:.2f}")
                message = (
                    f"🚨 *{alert['name']}*\n"
                    f"Metric: `{alert['metric']}`\n"
                    f"Current value: `{val:.2f}`"
                )
                await self.send_telegram(message)
            await asyncio.sleep(interval)


def list_metrics():
    print("Available metrics:")
    for m in METRICS:
        print(f" - {m}")

def list_alerts():
    config = load_config()
    alerts = config.get("alerts", [])
    if not alerts:
        print("No alerts found.")
        return
    print("Existing alerts:")
    for i, alert in enumerate(alerts, 1):
        print(f"{i}. ID: {alert.get('id', 'N/A')} | Name: {alert['name']} | Metric: {alert['metric']} {alert['comparator']} {alert['threshold']}")

def create_alert():
    config = load_config()
    print("=== Create new alert ===")
    name = input("Alert name: ").strip()
    while True:
        metric = input(f"Metric name ({', '.join(METRICS)}): ").strip()
        if metric in METRICS:
            break
        print(f"Invalid metric name. Choose from {', '.join(METRICS)}")
    while True:
        comparator = input("Comparator (> or <): ").strip()
        if comparator in (">", "<"):
            break
        print("Comparator must be '>' or '<'")
    while True:
        threshold_input = input("Threshold value (number): ").strip()
        try:
            threshold = float(threshold_input)
            break
        except ValueError:
            print("Invalid number, please enter a numeric value.")

    new_alert = {
        "id": str(uuid.uuid4()),
        "name": name,
        "metric": metric,
        "comparator": comparator,
        "threshold": threshold,
    }
    config.setdefault("alerts", []).append(new_alert)
    save_config(config)
    print(f"✅ Alert saved! ID: {new_alert['id']}")

def remove_alert(alert_id: str):
    config = load_config()
    alerts = config.get("alerts", [])
    filtered_alerts = [a for a in alerts if a.get("id") != alert_id]
    if len(filtered_alerts) == len(alerts):
        print(f"❌ Alert with ID {alert_id} not found.")
        return
    config["alerts"] = filtered_alerts
    save_config(config)
    print(f"✅ Alert with ID {alert_id} has been removed.")
