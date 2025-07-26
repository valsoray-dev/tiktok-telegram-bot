import re
from os import getenv
from typing import Final

from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN: Final[str] = getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    msg = "BOT_TOKEN must be set in .env file"
    raise ValueError(msg)

# TikTok API settings (optional)
INSTALL_ID: Final[str] = getenv("INSTALL_ID", "")
DEVICE_ID: Final[str] = getenv("DEVICE_ID", "")

# For error handling (optional)
OWNER_ID: Final[str] = getenv("OWNER_ID", "")

# Constants
TIKWM_PLAY_URL: Final[str] = "https://www.tikwm.com/video/media/play/{}.mp4"
TIKWM_HD_URL: Final[str] = "https://www.tikwm.com/video/media/hdplay/{}.mp4"
TIKTOK_URL_PATTERN: Final[re.Pattern[str]] = re.compile(r"((?:www|vm|vt)\.tiktok\.com)/[^\s]+")
AWEME_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?:video|photo|v)/(\d{19})")
