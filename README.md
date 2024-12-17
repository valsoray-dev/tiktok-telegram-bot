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
    pip install .
    ```

4. Rename the `.env.example` file to `.env` and replace `BOT_TOKEN` with your Telegram bot token.

5. Run the bot:

    ```bash
    python3 main.py
    ```

## License

Copyright (C) 2023 valsoray-dev

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Disclaimer

This project is not affiliated with TikTok. Use it responsibly and respect the terms of service of the platforms you are downloading content from.
