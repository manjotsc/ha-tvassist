"""Constants for the TV Assist integration."""
from typing import Final

DOMAIN: Final = "tv_assist"

# Config keys
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_NAME: Final = "name"
CONF_DEVICE_IDENTIFIER: Final = "device_identifier"
# Optional access token that the TV's notification server requires (matches the token set on the
# TV under Notifications). Sent as the `X-Token` header on every push.
CONF_TOKEN: Final = "token"

DEFAULT_PORT: Final = 8455
DEFAULT_NAME: Final = "TV Assist"

MANUFACTURER: Final = "TV Assist"
MODEL: Final = "Android TV"

# Service names (registered under DOMAIN → tv_assist.notify, tv_assist.persistent, tv_assist.clear)
SERVICE_NOTIFY: Final = "notify"
SERVICE_PERSISTENT: Final = "persistent"
SERVICE_CLEAR: Final = "clear"
SERVICE_SPEAK: Final = "speak"
SERVICE_PLAY_SOUND: Final = "play_sound"

# Text-to-speech (tv_assist.speak, and `speak: true` on tv_assist.notify / tv_assist.persistent)
ATTR_SPEAK: Final = "speak"
# Optional custom words for a pill to speak instead of its label + message (tv_assist.persistent).
ATTR_SPEAK_TEXT: Final = "speak_text"
# tv_assist.persistent "Speak aloud" choice: voice the pill's own label+message ("text") or the
# custom `speak_text` ("custom"). Unset = don't speak. (The integration turns either into `speak:true`.)
VALID_PILL_SPEAK: Final[list[str]] = ["text", "custom"]
# How a spoken notification voices its title vs message (overrides the TV's Audio-settings default):
# both = one utterance "Title. Message"; separate = title then message as two utterances;
# message/title = only that field.
ATTR_SPEAK_MODE: Final = "speak_mode"
# Service-accepted speak modes. Picking any of these on tv_assist.notify turns TTS on, so no separate
# on/off flag is needed. "default" = use the TV's own Audio-settings mode (the integration sends
# `speak` only, with no per-call override); the rest override it.
VALID_SPEAK_MODE: Final[list[str]] = ["default", "both", "separate", "message", "title"]
ATTR_LANGUAGE: Final = "language"
ATTR_VOLUME: Final = "volume"
ATTR_DUCK: Final = "duck"
ATTR_INTERRUPT: Final = "interrupt"
# Sound files (tv_assist.play_sound, and `sound:` on tv_assist.notify) — a URL to an audio file.
ATTR_SOUND: Final = "sound"
# Repeat behavior for a notification's sound / speech: "once" or "loop" (until the notification leaves
# the screen; a pinned/persistent one is capped on the TV side). Overrides the TV's Audio defaults.
ATTR_SOUND_REPEAT: Final = "sound_repeat"
ATTR_SPEAK_REPEAT: Final = "speak_repeat"
VALID_REPEAT: Final[list[str]] = ["once", "loop"]
# Seconds of pause between repeats of a repeating spoken announcement (0-60; blank = TV default).
ATTR_SPEAK_REPEAT_GAP: Final = "speak_repeat_gap"
# Interactive notification: OK enlarges (fullscreen camera), BACK dismisses (via the remote).
ATTR_INTERACTIVE: Final = "interactive"
# Seconds an opened (enlarged) interactive notification is kept before auto-closing (0 = until BACK;
# blank = this TV's default).
ATTR_ENLARGE_TIMEOUT: Final = "enlarge_timeout"

# Service attribute keys
ATTR_DEVICE_ID: Final = "device_id"
ATTR_TARGET: Final = "target"
ATTR_HOST: Final = "host"
ATTR_TITLE: Final = "title"
ATTR_SOURCE: Final = "source"
ATTR_SOURCE2: Final = "source2"
ATTR_MESSAGE: Final = "message"
ATTR_ICON: Final = "icon"
ATTR_ICON_URL: Final = "icon_url"
ATTR_ICON_SIZE: Final = "icon_size"
ATTR_SMALL_ICON: Final = "small_icon"
ATTR_SMALL_ICON_URL: Final = "small_icon_url"
ATTR_SMALL_ICON_SIZE: Final = "small_icon_size"
ATTR_COLOR: Final = "color"
ATTR_ICON_COLOR: Final = "icon_color"
ATTR_SMALL_ICON_COLOR: Final = "small_icon_color"
ATTR_TITLE_COLOR: Final = "title_color"
ATTR_SOURCE_COLOR: Final = "source_color"
ATTR_MESSAGE_COLOR: Final = "message_color"
ATTR_BACKGROUND_COLOR: Final = "background_color"
ATTR_BACKGROUND_OPACITY: Final = "background_opacity"
ATTR_ICON_BACKGROUND: Final = "icon_background"
ATTR_ICON_BACKGROUND_OPACITY: Final = "icon_background_opacity"
ATTR_SMALL_ICON_BACKGROUND: Final = "small_icon_background"
ATTR_SMALL_ICON_BACKGROUND_OPACITY: Final = "small_icon_background_opacity"
ATTR_DURATION: Final = "duration"
ATTR_POSITION: Final = "position"
ATTR_SIZE: Final = "size"
ATTR_IMAGE: Final = "image"
ATTR_CAMERA: Final = "camera"
ATTR_CAMERA_STREAM: Final = "camera_stream"
ATTR_MEDIA_URL: Final = "media_url"
# Force how media_url is treated when the URL isn't an obvious rtsp/HLS/DASH stream: "video" or
# "image". Blank = auto-detect from the URL.
ATTR_MEDIA_TYPE: Final = "media_type"
VALID_MEDIA_TYPE: Final[list[str]] = ["video", "image"]
ATTR_PLAYER: Final = "player"
ATTR_FLASH: Final = "flash"
ATTR_FLASH_COLOR: Final = "flash_color"
ATTR_FLASH_SPEED: Final = "flash_speed"
ATTR_ID: Final = "id"

VALID_FLASH: Final[list[str]] = ["none", "glow", "flash", "blink"]
VALID_FLASH_SPEED: Final[list[str]] = ["slow", "medium", "fast"]
VALID_PLAYER: Final[list[str]] = ["auto", "exoplayer", "vlc"]
# Persistent-pill extras
ATTR_SHAPE: Final = "shape"
ATTR_BORDER_COLOR: Final = "border_color"
ATTR_EXPIRATION: Final = "expiration"
# Entity-bound pill (live value/icon/color from an entity's state; all optional)
ATTR_ENTITY: Final = "entity"
ATTR_ATTRIBUTE: Final = "attribute"
ATTR_LABEL: Final = "label"
# Pill flash — set a color to pulse that element; icon and border are independent.
ATTR_FLASH_BORDER_COLOR: Final = "flash_border_color"
ATTR_FLASH_ICON_COLOR: Final = "flash_icon_color"
# Per-element flash style (pulse / blink / glow); icon and border are independent.
ATTR_FLASH_BORDER_TYPE: Final = "flash_border_type"
ATTR_FLASH_ICON_TYPE: Final = "flash_icon_type"
VALID_FLASH_TYPE: Final[list[str]] = ["pulse", "blink", "glow"]
# Per-element flash tempo — ms per cycle (from the slider) or legacy slow/medium/fast; icon/border independent.
ATTR_FLASH_ICON_SPEED: Final = "flash_icon_speed"
ATTR_FLASH_BORDER_SPEED: Final = "flash_border_speed"
# Flash speed slider bounds (ms per cycle); lower = faster.
FLASH_SPEED_MIN_MS: Final = 200
FLASH_SPEED_MAX_MS: Final = 3000

VALID_SHAPES: Final[list[str]] = ["circle", "rounded", "rectangular"]

# String fields forwarded as-is from the service call to the TV's /notify payload.
PASSTHROUGH_STRING_ATTRS: Final[tuple[str, ...]] = (
    ATTR_MESSAGE, ATTR_TITLE, ATTR_SOURCE, ATTR_SOURCE2, ATTR_ICON, ATTR_ICON_URL, ATTR_ICON_SIZE,
    ATTR_SMALL_ICON, ATTR_SMALL_ICON_URL, ATTR_SMALL_ICON_SIZE, ATTR_COLOR,
    ATTR_ICON_COLOR, ATTR_SMALL_ICON_COLOR, ATTR_TITLE_COLOR, ATTR_SOURCE_COLOR,
    ATTR_MESSAGE_COLOR, ATTR_BACKGROUND_COLOR, ATTR_BACKGROUND_OPACITY,
    ATTR_ICON_BACKGROUND, ATTR_ICON_BACKGROUND_OPACITY, ATTR_SMALL_ICON_BACKGROUND,
    ATTR_SMALL_ICON_BACKGROUND_OPACITY, ATTR_POSITION, ATTR_SIZE,
    ATTR_IMAGE, ATTR_CAMERA, ATTR_CAMERA_STREAM, ATTR_MEDIA_URL, ATTR_MEDIA_TYPE, ATTR_PLAYER,
    ATTR_FLASH, ATTR_FLASH_COLOR, ATTR_FLASH_SPEED, ATTR_ID,
    ATTR_LANGUAGE, ATTR_VOLUME, ATTR_DUCK, ATTR_INTERRUPT,
    ATTR_SOUND, ATTR_SOUND_REPEAT, ATTR_SPEAK_REPEAT, ATTR_SPEAK_REPEAT_GAP, ATTR_INTERACTIVE,
    ATTR_ENLARGE_TIMEOUT,
)

VALID_POSITIONS: Final[list[str]] = [
    "top-left",
    "top-center",
    "top-right",
    "bottom-left",
    "bottom-center",
    "bottom-right",
]
VALID_SIZES: Final[list[str]] = ["extra-small", "small", "medium", "large"]
