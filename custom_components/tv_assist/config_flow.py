"""Config flow for TV Assist — one entry per TV (a device)."""
from __future__ import annotations

import re

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_DEVICE_IDENTIFIER,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_TOKEN,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)

_VALID_IDENTIFIER = re.compile(r"^[a-z0-9_]+$")


def _sanitize_identifier(name: str) -> str:
    """Turn a name into a stable lowercase identifier (e.g. 'Bedroom TV' -> 'bedroom_tv')."""
    identifier = re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_"))
    identifier = re.sub(r"_+", "_", identifier).strip("_")
    return identifier or "tv"


class TvAssistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TV Assist. Each entry is one TV (a device)."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input.get(CONF_NAME) or DEFAULT_NAME
            identifier = (user_input.get(CONF_DEVICE_IDENTIFIER) or "").strip() or _sanitize_identifier(name)
            if not _VALID_IDENTIFIER.match(identifier):
                errors[CONF_DEVICE_IDENTIFIER] = "invalid_identifier"
            else:
                await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                        CONF_DEVICE_IDENTIFIER: identifier,
                        CONF_TOKEN: (user_input.get(CONF_TOKEN) or "").strip(),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_DEVICE_IDENTIFIER, default=""): str,
                # Only needed if you set an access token on the TV (Notifications settings).
                vol.Optional(CONF_TOKEN, default=""): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TvAssistOptionsFlow(config_entry)


class TvAssistOptionsFlow(config_entries.OptionsFlow):
    """Edit a configured TV's access token after setup (e.g. after adding a token on the TV)."""

    def __init__(self, config_entry) -> None:
        # Stored privately: HA sets self.config_entry automatically on newer cores, and assigning
        # it here would trip a deprecation warning.
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_TOKEN: (user_input.get(CONF_TOKEN) or "").strip()}
            )

        current = self._entry.options.get(
            CONF_TOKEN, self._entry.data.get(CONF_TOKEN, "")
        )
        schema = vol.Schema({vol.Optional(CONF_TOKEN, default=current): str})
        return self.async_show_form(step_id="init", data_schema=schema)
