import argparse
import asyncio
import logging
from .monitor import (
    list_metrics,
    list_alerts,
    create_alert,
    remove_alert,
    Monitor,
)
from .config import load_config, save_config
from telegram import Bot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def configure_cli(args):
    config = load_config()
    telegram_cfg = config.setdefault("telegram", {})
    changed = False

    if args.bot_token:
        telegram_cfg["token"] = args.bot_token
        print(f"✅ Telegram bot token updated.")
        changed = True

    if args.chat_id:
        telegram_cfg["chat_id"] = args.chat_id
        print(f"✅ Telegram chat_id updated.")
        changed = True

    if changed:
        save_config(config)
    else:
        print("❌ No configuration changes provided.")


def main():
    parser = argparse.ArgumentParser(prog="warlock", description="System monitoring CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    # Metrics command
    metrics_parser = subparsers.add_parser("m", help="metrics commands")
    metrics_parser.add_argument("subcommand", choices=["ls"], help="metrics list")

    # Alerts command
    alerts_parser = subparsers.add_parser("a", help="alerts commands")
    alerts_parser.add_argument("subcommand", choices=["ls", "cr", "rm"], help="list, create, remove alerts")
    alerts_parser.add_argument("alert_id", nargs="?", help="Alert ID to remove")

    # Run monitoring
    run_parser = subparsers.add_parser("r", help="run monitoring")

    # Configure command
    config_parser = subparsers.add_parser("c", help="configure telegram settings")
    config_parser.add_argument("-b", "--bot-token", type=str, help="Telegram bot token")
    config_parser.add_argument("-c", "--chat-id", type=str, help="Telegram chat ID")

    args = parser.parse_args()

    if args.command == "m":
        if args.subcommand == "ls":
            list_metrics()

    elif args.command == "a":
        if args.subcommand == "ls":
            list_alerts()
        elif args.subcommand == "cr":
            create_alert()
        elif args.subcommand == "rm":
            if not args.alert_id:
                print("Error: alert_id required for remove command")
                return
            remove_alert(args.alert_id)

    elif args.command == "r":
        config = load_config()
        token = config.get("telegram", {}).get("token")
        chat_id = config.get("telegram", {}).get("chat_id")
        if not token or not chat_id:
            print("❌ Please set Telegram token and chat_id in config.yaml first!")
            return
        bot = Bot(token=token)
        monitor = Monitor(config.get("alerts", []), bot=bot, chat_id=chat_id)
        asyncio.run(monitor.run())

    elif args.command == "c":
        configure_cli(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
