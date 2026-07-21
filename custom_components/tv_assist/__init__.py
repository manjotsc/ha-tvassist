"""The TV Assist integration.

Registers custom services ``tv_assist.notify`` and ``tv_assist.clear`` that push to one or more
TVs running the TV Assist app. The TV is chosen from a **device dropdown** (``device_id``), a
stable ``target`` identifier, or a manual ``host``.
"""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    ATTR_BACKGROUND_COLOR,
    ATTR_BACKGROUND_OPACITY,
    ATTR_ATTRIBUTE,
    ATTR_BORDER_COLOR,
    ATTR_CAMERA,
    ATTR_CAMERA_STREAM,
    ATTR_COLOR,
    ATTR_ENTITY,
    ATTR_LABEL,
    ATTR_DEVICE_ID,
    ATTR_DURATION,
    ATTR_ENLARGE_TIMEOUT,
    ATTR_EXPIRATION,
    ATTR_FLASH,
    ATTR_FLASH_BORDER_COLOR,
    ATTR_FLASH_BORDER_SPEED,
    ATTR_FLASH_BORDER_TYPE,
    ATTR_FLASH_COLOR,
    ATTR_FLASH_ICON_COLOR,
    ATTR_FLASH_ICON_SPEED,
    ATTR_FLASH_ICON_TYPE,
    ATTR_FLASH_SPEED,
    ATTR_HOST,
    ATTR_ICON,
    ATTR_ICON_BACKGROUND,
    ATTR_ICON_BACKGROUND_OPACITY,
    ATTR_ICON_COLOR,
    ATTR_ICON_SIZE,
    ATTR_ICON_URL,
    ATTR_ID,
    ATTR_IMAGE,
    ATTR_INTERACTIVE,
    ATTR_INTERRUPT,
    ATTR_LANGUAGE,
    ATTR_MEDIA_TYPE,
    ATTR_MEDIA_URL,
    ATTR_MESSAGE,
    ATTR_MESSAGE_COLOR,
    ATTR_PLAYER,
    ATTR_POSITION,
    ATTR_SHAPE,
    ATTR_SIZE,
    ATTR_SMALL_ICON,
    ATTR_SMALL_ICON_BACKGROUND,
    ATTR_SMALL_ICON_BACKGROUND_OPACITY,
    ATTR_SMALL_ICON_COLOR,
    ATTR_SMALL_ICON_SIZE,
    ATTR_SMALL_ICON_URL,
    ATTR_SOUND,
    ATTR_SOUND_REPEAT,
    ATTR_SPEAK_REPEAT,
    ATTR_SOURCE,
    ATTR_SOURCE2,
    ATTR_SOURCE_COLOR,
    ATTR_SPEAK,
    ATTR_SPEAK_MODE,
    ATTR_SPEAK_REPEAT_GAP,
    ATTR_SPEAK_TEXT,
    ATTR_TARGET,
    ATTR_TITLE,
    ATTR_TITLE_COLOR,
    ATTR_DUCK,
    ATTR_VOLUME,
    CONF_DEVICE_IDENTIFIER,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_TOKEN,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    PASSTHROUGH_STRING_ATTRS,
    SERVICE_CLEAR,
    SERVICE_NOTIFY,
    SERVICE_PERSISTENT,
    SERVICE_PLAY_SOUND,
    SERVICE_SPEAK,
    FLASH_SPEED_MAX_MS,
    FLASH_SPEED_MIN_MS,
    VALID_FLASH,
    VALID_FLASH_SPEED,
    VALID_FLASH_TYPE,
    VALID_MEDIA_TYPE,
    VALID_PILL_SPEAK,
    VALID_REPEAT,
    VALID_SPEAK_MODE,
    VALID_PLAYER,
    VALID_POSITIONS,
    VALID_SHAPES,
    VALID_SIZES,
)

_LOGGER = logging.getLogger(__name__)

# Flash speed accepts either the legacy words (slow/medium/fast) or a precise ms-per-cycle value
# from the slider; lower = faster.
FLASH_SPEED_VALUE = vol.Any(
    vol.In(VALID_FLASH_SPEED),
    vol.All(vol.Coerce(int), vol.Range(min=FLASH_SPEED_MIN_MS, max=FLASH_SPEED_MAX_MS)),
)


def _drop_none(data: dict[str, Any]) -> dict[str, Any]:
    """Strip keys whose value is ``None`` before schema validation.

    An optional field left blank in the UI (its checkbox ticked but no text entered) is
    sent by Home Assistant as ``null``; ``cv.string`` would reject that with "string value
    is None". Dropping those keys treats a blank field as "not set", which is what the
    handlers already assume.
    """
    return {k: v for k, v in data.items() if v is not None}

NOTIFY_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_HOST): cv.string,
        vol.Optional(ATTR_TITLE): cv.string,
        vol.Optional(ATTR_SOURCE): cv.string,
        vol.Optional(ATTR_SOURCE2): cv.string,
        vol.Optional(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_ICON): cv.string,
        vol.Optional(ATTR_ICON_URL): cv.string,
        vol.Optional(ATTR_ICON_SIZE): cv.positive_int,
        vol.Optional(ATTR_SMALL_ICON): cv.string,
        vol.Optional(ATTR_SMALL_ICON_URL): cv.string,
        vol.Optional(ATTR_SMALL_ICON_SIZE): cv.positive_int,
        vol.Optional(ATTR_COLOR): cv.string,
        vol.Optional(ATTR_ICON_COLOR): cv.string,
        vol.Optional(ATTR_SMALL_ICON_COLOR): cv.string,
        vol.Optional(ATTR_TITLE_COLOR): cv.string,
        vol.Optional(ATTR_SOURCE_COLOR): cv.string,
        vol.Optional(ATTR_MESSAGE_COLOR): cv.string,
        vol.Optional(ATTR_BACKGROUND_COLOR): cv.string,
        vol.Optional(ATTR_BACKGROUND_OPACITY): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_ICON_BACKGROUND): cv.string,
        vol.Optional(ATTR_ICON_BACKGROUND_OPACITY): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_SMALL_ICON_BACKGROUND): cv.string,
        vol.Optional(ATTR_SMALL_ICON_BACKGROUND_OPACITY): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_DURATION): cv.positive_int,
        vol.Optional(ATTR_POSITION): vol.In(VALID_POSITIONS),
        vol.Optional(ATTR_SIZE): vol.In(VALID_SIZES),
        vol.Optional(ATTR_IMAGE): cv.string,
        vol.Optional(ATTR_CAMERA): cv.string,
        vol.Optional(ATTR_CAMERA_STREAM): cv.string,
        vol.Optional(ATTR_MEDIA_URL): cv.string,
        vol.Optional(ATTR_MEDIA_TYPE): vol.In(VALID_MEDIA_TYPE),
        vol.Optional(ATTR_PLAYER): vol.In(VALID_PLAYER),
        vol.Optional(ATTR_FLASH): vol.In(VALID_FLASH),
        vol.Optional(ATTR_FLASH_COLOR): cv.string,
        vol.Optional(ATTR_FLASH_SPEED): FLASH_SPEED_VALUE,
        vol.Optional(ATTR_ID): cv.string,
        # OK enlarges (fullscreen camera), BACK dismisses — via the remote.
        vol.Optional(ATTR_INTERACTIVE): cv.boolean,
        # Seconds to keep an opened (enlarged) interactive notification before auto-closing (0 = until BACK).
        vol.Optional(ATTR_ENLARGE_TIMEOUT): vol.All(vol.Coerce(int), vol.Range(min=0, max=3600)),
        # Also voice this notification via TTS (title + message) and/or play a sound file.
        vol.Optional(ATTR_SPEAK): cv.boolean,
        # How the title/message are voiced; overrides the TV's Audio-settings default.
        vol.Optional(ATTR_SPEAK_MODE): vol.In(VALID_SPEAK_MODE),
        # Repeat speech / sound until the notification leaves the screen; overrides the TV defaults.
        vol.Optional(ATTR_SPEAK_REPEAT): vol.In(VALID_REPEAT),
        vol.Optional(ATTR_SPEAK_REPEAT_GAP): vol.All(vol.Coerce(int), vol.Range(min=0, max=60)),
        vol.Optional(ATTR_SOUND_REPEAT): vol.In(VALID_REPEAT),
        vol.Optional(ATTR_SOUND): cv.string,
        vol.Optional(ATTR_LANGUAGE): cv.string,
        vol.Optional(ATTR_VOLUME): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_DUCK): cv.boolean,
        vol.Optional(ATTR_INTERRUPT): cv.boolean,
    }
)

PERSISTENT_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_HOST): cv.string,
        vol.Required(ATTR_ID): cv.string,
        vol.Optional(ATTR_ICON): cv.string,
        vol.Optional(ATTR_ICON_URL): cv.string,
        vol.Optional(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_ENTITY): cv.string,
        vol.Optional(ATTR_ATTRIBUTE): cv.string,
        vol.Optional(ATTR_LABEL): cv.string,
        vol.Optional(ATTR_FLASH_BORDER_COLOR): cv.string,
        vol.Optional(ATTR_FLASH_ICON_COLOR): cv.string,
        vol.Optional(ATTR_FLASH_BORDER_TYPE): vol.In(VALID_FLASH_TYPE),
        vol.Optional(ATTR_FLASH_ICON_TYPE): vol.In(VALID_FLASH_TYPE),
        vol.Optional(ATTR_FLASH_ICON_SPEED): FLASH_SPEED_VALUE,
        vol.Optional(ATTR_FLASH_BORDER_SPEED): FLASH_SPEED_VALUE,
        vol.Optional(ATTR_SHAPE): vol.In(VALID_SHAPES),
        vol.Optional(ATTR_ICON_COLOR): cv.string,
        vol.Optional(ATTR_ICON_BACKGROUND): cv.string,
        vol.Optional(ATTR_ICON_BACKGROUND_OPACITY): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_MESSAGE_COLOR): cv.string,
        vol.Optional(ATTR_BORDER_COLOR): cv.string,
        vol.Optional(ATTR_BACKGROUND_COLOR): cv.string,
        vol.Optional(ATTR_BACKGROUND_OPACITY): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_POSITION): vol.In(VALID_POSITIONS),
        vol.Optional(ATTR_EXPIRATION): cv.positive_int,
        # Audio: a pill can voice itself / play a sound like a notification, looping until removed.
        # "Speak aloud" = "text" (label+message) or "custom" (speak_text); unset = silent.
        vol.Optional(ATTR_SPEAK): vol.In(VALID_PILL_SPEAK),
        vol.Optional(ATTR_SPEAK_TEXT): cv.string,
        vol.Optional(ATTR_SPEAK_REPEAT): vol.In(VALID_REPEAT),
        vol.Optional(ATTR_SPEAK_REPEAT_GAP): vol.All(vol.Coerce(int), vol.Range(min=0, max=60)),
        vol.Optional(ATTR_SOUND): cv.string,
        vol.Optional(ATTR_SOUND_REPEAT): vol.In(VALID_REPEAT),
        vol.Optional(ATTR_LANGUAGE): cv.string,
        vol.Optional(ATTR_VOLUME): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_DUCK): cv.boolean,
    }
)

# String fields forwarded from a persistent (pill) call to /notify_fixed.
_PERSISTENT_STRING_ATTRS = (
    ATTR_ICON, ATTR_ICON_URL, ATTR_MESSAGE, ATTR_SHAPE, ATTR_ICON_COLOR,
    ATTR_MESSAGE_COLOR, ATTR_BORDER_COLOR, ATTR_BACKGROUND_COLOR, ATTR_POSITION,
    ATTR_ENTITY, ATTR_ATTRIBUTE, ATTR_LABEL,
    ATTR_FLASH_BORDER_COLOR, ATTR_FLASH_ICON_COLOR,
    ATTR_FLASH_BORDER_TYPE, ATTR_FLASH_ICON_TYPE,
    ATTR_FLASH_ICON_SPEED, ATTR_FLASH_BORDER_SPEED,
    ATTR_ICON_BACKGROUND, ATTR_ICON_BACKGROUND_OPACITY, ATTR_BACKGROUND_OPACITY,
)

CLEAR_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_HOST): cv.string,
        vol.Optional(ATTR_ID): cv.string,
    }
)

SPEAK_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_HOST): cv.string,
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_LANGUAGE): cv.string,
        vol.Optional(ATTR_VOLUME): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_DUCK): cv.boolean,
        vol.Optional(ATTR_INTERRUPT): cv.boolean,
    }
)

PLAY_SOUND_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_HOST): cv.string,
        vol.Required(ATTR_SOUND): cv.string,
        vol.Optional(ATTR_VOLUME): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_DUCK): cv.boolean,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a TV Assist device from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    device_identifier = entry.data.get(CONF_DEVICE_IDENTIFIER, f"{host}:{port}")
    # An options-flow edit (adding/changing the token) wins over the initial setup value.
    token = (entry.options.get(CONF_TOKEN, entry.data.get(CONF_TOKEN, "")) or "").strip()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "name": name,
        "host": host,
        "port": port,
        "device_identifier": device_identifier,
        "token": token,
    }

    # Reload when the options (token) change so the new token takes effect immediately.
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    # Register the TV in the device registry so it shows in the device_id dropdown.
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, device_identifier)},
        name=name,
        manufacturer=MANUFACTURER,
        model=MODEL,
    )

    if not hass.services.has_service(DOMAIN, SERVICE_NOTIFY):
        _async_register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if not hass.data.get(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_NOTIFY)
        hass.services.async_remove(DOMAIN, SERVICE_PERSISTENT)
        hass.services.async_remove(DOMAIN, SERVICE_CLEAR)
        hass.services.async_remove(DOMAIN, SERVICE_SPEAK)
        hass.services.async_remove(DOMAIN, SERVICE_PLAY_SOUND)
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry after its options (e.g. the access token) change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _parse_host_port(host_string: str) -> tuple[str, int]:
    """Parse a ``host`` or ``host:port`` string."""
    if ":" in host_string:
        host, _, port = host_string.rpartition(":")
        try:
            return host, int(port)
        except ValueError:
            return host_string, DEFAULT_PORT
    return host_string, DEFAULT_PORT


def _async_register_services(hass: HomeAssistant) -> None:
    """Register the tv_assist.notify, tv_assist.persistent and tv_assist.clear services."""

    def _devices() -> dict[str, dict[str, Any]]:
        return {k: v for k, v in hass.data.get(DOMAIN, {}).items() if isinstance(v, dict)}

    def _device_at(host: str, port: int) -> dict[str, Any] | None:
        for data in _devices().values():
            if data.get("host") == host and data.get("port") == port:
                return data
        return None

    def _token_for(host: str, port: int) -> str | None:
        data = _device_at(host, port)
        token = (data or {}).get("token") or ""
        return token.strip() or None

    def _name_for(host: str, port: int) -> str:
        data = _device_at(host, port)
        return (data or {}).get("name") or f"{host}:{port}"

    def _by_identifier(identifier: str) -> tuple[str, int] | None:
        for data in _devices().values():
            if data.get("device_identifier") == identifier:
                return data["host"], data["port"]
        return None

    def _by_device_id(device_id: str) -> tuple[str, int] | None:
        device = dr.async_get(hass).async_get(device_id)
        if device is None:
            return None
        for domain, identifier in device.identifiers:
            if domain == DOMAIN:
                return _by_identifier(identifier)
        return None

    def _resolve(call_data: dict[str, Any]) -> list[tuple[str, int]]:
        """Resolve the call's targeting fields to a list of (host, port)."""
        device_id = call_data.get(ATTR_DEVICE_ID)
        target = call_data.get(ATTR_TARGET)
        host = call_data.get(ATTR_HOST)

        if target:
            hp = _by_identifier(target)
            if hp:
                return [hp]
        if device_id:
            hp = _by_device_id(device_id) or _by_identifier(device_id)
            if hp:
                return [hp]
        if host:
            return [_parse_host_port(host)]

        # Nothing specified → send to every configured TV.
        targets = [(d["host"], d["port"]) for d in _devices().values()]
        if targets:
            return targets

        raise ServiceValidationError(
            "No TV target found. Pick a device, enter a Device Identifier, or a host:port."
        )

    async def _post(path: str, payload: dict[str, Any], targets: list[tuple[str, int]]) -> None:
        session = async_get_clientsession(hass)
        # (host, port, had_token) for each TV that answered 401 — surfaced as one clear error below.
        auth_failures: list[tuple[str, int, bool]] = []
        for host, port in targets:
            url = f"http://{host}:{port}{path}"
            token = _token_for(host, port)
            headers = {"X-Token": token} if token else {}
            try:
                async with session.post(
                    url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=8)
                ) as resp:
                    await resp.read()
                    if resp.status in (401, 403):
                        auth_failures.append((host, port, bool(token)))
                        _LOGGER.warning(
                            "TV Assist at %s rejected the notification (HTTP %s): access token %s.",
                            url, resp.status, "incorrect" if token else "missing",
                        )
            except Exception as err:  # noqa: BLE001 - best effort; the TV may be off
                _LOGGER.warning("TV Assist call to %s failed: %s", url, err)

        if auth_failures:
            host, port, had_token = auth_failures[0]
            name = _name_for(host, port)
            if had_token:
                raise ServiceValidationError(
                    f"TV '{name}' rejected the notification: the access token is incorrect. "
                    "Update it under Settings → Devices & Services → TV Assist → Configure to match "
                    "the token shown on the TV (Notifications settings)."
                )
            raise ServiceValidationError(
                f"TV '{name}' requires an access token, but none is set for it in Home Assistant. "
                "Add the token under Settings → Devices & Services → TV Assist → Configure — it must "
                "match the token on the TV (Notifications settings)."
            )

    async def async_notify(call: ServiceCall) -> None:
        targets = _resolve(call.data)
        payload: dict[str, Any] = {}
        for attr in PASSTHROUGH_STRING_ATTRS:
            value = call.data.get(attr)
            if value not in (None, ""):
                payload[attr] = value
        if ATTR_DURATION in call.data and call.data[ATTR_DURATION] is not None:
            payload[ATTR_DURATION] = call.data[ATTR_DURATION]
        # Text-to-speech: picking a speak mode turns TTS on. "default" uses the TV's own
        # Audio-settings mode (send `speak` only); the rest override it per call. A bare
        # `speak: true` with no mode is still honored for backward compatibility.
        mode = call.data.get(ATTR_SPEAK_MODE)
        if mode:
            payload[ATTR_SPEAK] = True
            if mode != "default":
                payload[ATTR_SPEAK_MODE] = mode
        elif call.data.get(ATTR_SPEAK):
            payload[ATTR_SPEAK] = True
        payload.setdefault(ATTR_MESSAGE, "")
        await _post("/notify", payload, targets)

    async def async_persistent(call: ServiceCall) -> None:
        targets = _resolve(call.data)
        payload: dict[str, Any] = {ATTR_ID: call.data[ATTR_ID]}
        for attr in _PERSISTENT_STRING_ATTRS:
            value = call.data.get(attr)
            if value not in (None, ""):
                payload[attr] = value
        if call.data.get(ATTR_EXPIRATION):
            payload[ATTR_EXPIRATION] = call.data[ATTR_EXPIRATION]
        # "Speak aloud" is one choice: "text" voices the pill's label+message, "custom" voices
        # speak_text. Either turns TTS on (the TV takes speak:true + optional speak_text).
        speak_choice = call.data.get(ATTR_SPEAK)
        if speak_choice:
            payload[ATTR_SPEAK] = True
            if speak_choice == "custom":
                speak_text = call.data.get(ATTR_SPEAK_TEXT)
                if speak_text not in (None, ""):
                    payload[ATTR_SPEAK_TEXT] = speak_text
        # Forward the remaining audio fields (looping/volume/etc.).
        for attr in (
            ATTR_SPEAK_REPEAT, ATTR_SPEAK_REPEAT_GAP, ATTR_SOUND, ATTR_SOUND_REPEAT,
            ATTR_LANGUAGE, ATTR_VOLUME, ATTR_DUCK,
        ):
            value = call.data.get(attr)
            if value not in (None, ""):
                payload[attr] = value
        await _post("/notify_fixed", payload, targets)

    async def async_clear(call: ServiceCall) -> None:
        targets = _resolve(call.data)
        notif_id = call.data.get(ATTR_ID, "")
        payload = {ATTR_ID: notif_id} if notif_id else {}
        # Clear both transient toasts and persistent pills with this id (or all).
        await _post("/notify/clear", payload, targets)
        await _post("/notify_fixed/clear", payload, targets)

    async def async_speak(call: ServiceCall) -> None:
        targets = _resolve(call.data)
        payload: dict[str, Any] = {ATTR_MESSAGE: call.data[ATTR_MESSAGE]}
        for attr in (ATTR_LANGUAGE, ATTR_VOLUME, ATTR_DUCK, ATTR_INTERRUPT):
            if attr in call.data and call.data[attr] is not None:
                payload[attr] = call.data[attr]
        await _post("/speak", payload, targets)

    async def async_play_sound(call: ServiceCall) -> None:
        targets = _resolve(call.data)
        payload: dict[str, Any] = {ATTR_SOUND: call.data[ATTR_SOUND]}
        for attr in (ATTR_VOLUME, ATTR_DUCK):
            if attr in call.data and call.data[attr] is not None:
                payload[attr] = call.data[attr]
        await _post("/play", payload, targets)

    hass.services.async_register(DOMAIN, SERVICE_NOTIFY, async_notify, schema=vol.All(_drop_none, NOTIFY_SCHEMA))
    hass.services.async_register(DOMAIN, SERVICE_PERSISTENT, async_persistent, schema=vol.All(_drop_none, PERSISTENT_SCHEMA))
    hass.services.async_register(DOMAIN, SERVICE_CLEAR, async_clear, schema=vol.All(_drop_none, CLEAR_SCHEMA))
    hass.services.async_register(DOMAIN, SERVICE_SPEAK, async_speak, schema=vol.All(_drop_none, SPEAK_SCHEMA))
    hass.services.async_register(DOMAIN, SERVICE_PLAY_SOUND, async_play_sound, schema=vol.All(_drop_none, PLAY_SOUND_SCHEMA))
