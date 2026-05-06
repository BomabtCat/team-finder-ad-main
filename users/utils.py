from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


RUSSIAN_LOCAL_PHONE_PREFIX = "8"
RUSSIAN_INTERNATIONAL_PHONE_PREFIX = "+7"
RUSSIAN_LOCAL_PHONE_LENGTH = 11
RUSSIAN_INTERNATIONAL_PHONE_LENGTH = 12
PHONE_HASH_MODULO = 10_000_000
PHONE_DIGITS_WIDTH = 7
PLACEHOLDER_PHONE_PREFIX = "+7900"
PHONE_HASH_STEP = 1

AVATAR_BG_BLUE = "#dbeafe"
AVATAR_BG_GREEN = "#dcfce7"
AVATAR_BG_YELLOW = "#fef3c7"
AVATAR_BG_PINK = "#fce7f3"
AVATAR_BG_INDIGO = "#e0e7ff"
AVATAR_BACKGROUND_COLORS = [
    AVATAR_BG_BLUE,
    AVATAR_BG_GREEN,
    AVATAR_BG_YELLOW,
    AVATAR_BG_PINK,
    AVATAR_BG_INDIGO,
]
AVATAR_TEXT_COLOR = "#1f2937"
AVATAR_SIZE = 256
AVATAR_FONT_SIZE = 128
AVATAR_TEXT_Y_OFFSET = 8
CENTER_DIVISOR = 2
BBOX_LEFT = 0
BBOX_TOP = 1
BBOX_RIGHT = 2
BBOX_BOTTOM = 3
FIRST_CHARACTER_INDEX = 1
DEFAULT_AVATAR_LETTER = "U"
AVATAR_FONT_NAME = "DejaVuSans-Bold.ttf"
AVATAR_IMAGE_MODE = "RGB"
AVATAR_IMAGE_FORMAT = "PNG"
AVATAR_UPLOAD_DIR = "avatars"


def normalize_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    if (
        phone.startswith(RUSSIAN_LOCAL_PHONE_PREFIX)
        and len(phone) == RUSSIAN_LOCAL_PHONE_LENGTH
    ):
        return RUSSIAN_INTERNATIONAL_PHONE_PREFIX + phone[FIRST_CHARACTER_INDEX:]
    return phone


def generate_avatar_name(user):
    safe_email = user.email.replace("@", "_").replace(".", "_")
    return f"{AVATAR_UPLOAD_DIR}/{safe_email}.png"


def generate_placeholder_phone(email, user_model):
    number = _email_to_phone_number(email)
    phone = _format_placeholder_phone(number)
    while user_model.objects.filter(phone=phone).exists():
        number = (number + PHONE_HASH_STEP) % PHONE_HASH_MODULO
        phone = _format_placeholder_phone(number)
    return phone


def generate_avatar(user):
    color = _avatar_background_for_email(user.email)
    image = Image.new(AVATAR_IMAGE_MODE, (AVATAR_SIZE, AVATAR_SIZE), color)
    draw = ImageDraw.Draw(image)
    letter = (
        user.name[:FIRST_CHARACTER_INDEX]
        or user.email[:FIRST_CHARACTER_INDEX]
        or DEFAULT_AVATAR_LETTER
    ).upper()
    try:
        font = ImageFont.truetype(AVATAR_FONT_NAME, AVATAR_FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((BBOX_LEFT, BBOX_LEFT), letter, font=font)
    x = (AVATAR_SIZE - (bbox[BBOX_RIGHT] - bbox[BBOX_LEFT])) / CENTER_DIVISOR
    y = (
        (AVATAR_SIZE - (bbox[BBOX_BOTTOM] - bbox[BBOX_TOP])) / CENTER_DIVISOR
        - AVATAR_TEXT_Y_OFFSET
    )
    draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)
    buffer = BytesIO()
    image.save(buffer, format=AVATAR_IMAGE_FORMAT)
    return ContentFile(buffer.getvalue())


def _email_to_phone_number(email):
    return sum(
        (index + PHONE_HASH_STEP) * ord(char)
        for index, char in enumerate(email)
    ) % PHONE_HASH_MODULO


def _format_placeholder_phone(number):
    return f"{PLACEHOLDER_PHONE_PREFIX}{number:0{PHONE_DIGITS_WIDTH}d}"


def _avatar_background_for_email(email):
    color_index = sum(ord(char) for char in email) % len(AVATAR_BACKGROUND_COLORS)
    return AVATAR_BACKGROUND_COLORS[color_index]
