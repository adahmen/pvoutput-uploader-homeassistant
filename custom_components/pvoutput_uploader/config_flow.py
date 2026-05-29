"""Config flow for PVOutput Uploader integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_API_KEY,
    CONF_ENERGY_ENTITY,
    CONF_END_TIME,
    CONF_NAME,
    CONF_POWER_ENTITY,
    CONF_START_TIME,
    CONF_SYSTEM_ID,
    CONF_TEMPERATURE_ENTITY,
    CONF_UPLOAD_INTERVAL,
    DEFAULT_END_TIME,
    DEFAULT_START_TIME,
    DEFAULT_UPLOAD_INTERVAL,
    DOMAIN,
)


def _build_schema(defaults: dict = {}) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
            vol.Required(CONF_API_KEY, default=defaults.get(CONF_API_KEY, "")): str,
            vol.Required(CONF_SYSTEM_ID, default=defaults.get(CONF_SYSTEM_ID, "")): str,
            vol.Required(CONF_POWER_ENTITY, default=defaults.get(CONF_POWER_ENTITY, "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"])
            ),
            vol.Required(CONF_ENERGY_ENTITY, default=defaults.get(CONF_ENERGY_ENTITY, "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"])
            ),
            vol.Optional(CONF_TEMPERATURE_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"])
            ),
            vol.Optional(
                CONF_UPLOAD_INTERVAL,
                default=defaults.get(CONF_UPLOAD_INTERVAL, DEFAULT_UPLOAD_INTERVAL),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=5, max=60, step=5, mode="box")
            ),
            vol.Optional(
                CONF_START_TIME,
                default=defaults.get(CONF_START_TIME, DEFAULT_START_TIME),
            ): str,
            vol.Optional(
                CONF_END_TIME,
                default=defaults.get(CONF_END_TIME, DEFAULT_END_TIME),
            ): str,
        }
    )


def _options_schema(defaults: dict = {}) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_POWER_ENTITY, default=defaults.get(CONF_POWER_ENTITY, "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"])
            ),
            vol.Required(CONF_ENERGY_ENTITY, default=defaults.get(CONF_ENERGY_ENTITY, "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"])
            ),
            vol.Optional(CONF_TEMPERATURE_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"])
            ),
            vol.Optional(
                CONF_UPLOAD_INTERVAL,
                default=defaults.get(CONF_UPLOAD_INTERVAL, DEFAULT_UPLOAD_INTERVAL),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=5, max=60, step=5, mode="box")
            ),
            vol.Optional(
                CONF_START_TIME,
                default=defaults.get(CONF_START_TIME, DEFAULT_START_TIME),
            ): str,
            vol.Optional(
                CONF_END_TIME,
                default=defaults.get(CONF_END_TIME, DEFAULT_END_TIME),
            ): str,
        }
    )


class PVOutputUploaderConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PVOutput Uploader."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            unique_id = f"{user_input[CONF_SYSTEM_ID]}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PVOutputUploaderOptionsFlow(config_entry)


class PVOutputUploaderOptionsFlow(config_entries.OptionsFlow):
    """Handle options for PVOutput Uploader."""

    async def async_step_init(self, user_input=None):
        """Handle options step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(current),
        )
