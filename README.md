# TikTok Telegram Bot

This bot allows users to download video or slide show from TikTok directly through Telegram. Currently all bot messages are in Ukranian.

## Setup

### Prerequisites

- Telegram Bot API token. You can obtain it by contacting [@BotFather](https://t.me/botfather).

### Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/valsoray-dev/tiktok-telegram-bot.git
    cd tiktok-telegram-bot
    ```

2. Create a virtual environment:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Rename the `.env.example` file to `.env` and replace `BOT_TOKEN` with your Telegram bot token.

5. Run the bot:

    ```bash
    python3 bot.py
    ```

## License

[MIT License](LICENSE).

## Disclaimer

This project is not affiliated with TikTok. Use it responsibly and respect the terms of service of the platforms you are downloading content from.
