import os
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
VK_GROUP_ID = os.getenv("VK_GROUP_ID")
LOGO_ATTACHMENT = os.getenv("LOGO_ATTACHMENT")

if not VK_TOKEN:
    raise ValueError("Не найден VK_TOKEN в .env")

if not VK_GROUP_ID:
    raise ValueError("Не найден VK_GROUP_ID в .env")

VK_GROUP_ID = int(VK_GROUP_ID)