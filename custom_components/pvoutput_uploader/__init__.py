"""PVOutput Uploader Integration for Home Assistant."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, time

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util
from datetime import timedelta

from .const import (
    CONF_API_KEY,
    CONF_ENERGY_ENTITY,
    CONF_END_TIME,
    CONF_POWER_ENTITY,
    CONF_START_TIME,
    CONF_SYSTEM_ID,
    CONF_TEMPERATURE_ENTITY,
    CONF_UPLOAD_INTERVAL,
    DEFAULT_END_TIME,
    DEFAULT_START_TIME,
    DEFAULT_UPLOAD_INTERVAL,
    DOMAIN,
    PVOUTPUT_URL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PVOutput Uploader from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    config = {**entry.data, **entry.options}

    uploader = PVOutputUploader(hass, config)
    hass.data[DOMAIN][entry.entry_id] = uploader

    interval_minutes = int(config.get(CONF_UPLOAD_INTERVAL, DEFAULT_UPLOAD_INTERVAL))

    async def _async_upload_at_interval(now):
        """Upload only at exact interval boundaries."""
        minute = now.minute
        if minute % interval_minutes == 0:
            await uploader.async_upload(now)

    cancel = async_track_time_interval(
        hass, _async_upload_at_interval, timedelta(minutes=1)
    )
    uploader.cancel_interval = cancel

    entry.async_on_unload(cancel)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


class PVOutputUploader:
    """Handles uploading data to PVOutput."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self.hass = hass
        self.config = config
        self.cancel_interval = None

    def _is_within_upload_window(self) -> bool:
        """Check if current time is within the configured upload window."""
        now = dt_util.now().time()

        start_str = self.config.get(CONF_START_TIME, DEFAULT_START_TIME)
        end_str = self.config.get(CONF_END_TIME, DEFAULT_END_TIME)

        try:
            start = time.fromisoformat(start_str)
            end = time.fromisoformat(end_str)
        except ValueError:
            _LOGGER.warning("Invalid start/end time format, using defaults")
            start = time(6, 0)
            end = time(22, 0)

        return start <= now <= end

    def _get_state_float(self, entity_id: str, convert_to_wh: bool = False) -> float | None:
        """Get numeric state of an entity, optionally converting kWh to Wh."""
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable", ""):
            _LOGGER.debug("Entity %s unavailable or unknown", entity_id)
            return None
        try:
            value = float(state.state)
            if convert_to_wh:
                unit = state.attributes.get("unit_of_measurement", "")
                if unit.lower() == "kwh":
                    value = value * 1000
                    _LOGGER.debug("Converted %s from kWh to Wh: %s", entity_id, value)
            return value
        except (ValueError, TypeError):
            _LOGGER.warning("Cannot convert state of %s to float: %s", entity_id, state.state)
            return None

    async def async_upload(self, now=None) -> None:
        """Upload data to PVOutput if within the time window."""
        if not self._is_within_upload_window():
            _LOGGER.debug("Outside upload window, skipping")
            return

        api_key = self.config.get(CONF_API_KEY)
        system_id = self.config.get(CONF_SYSTEM_ID)
        power_entity = self.config.get(CONF_POWER_ENTITY)
        energy_entity = self.config.get(CONF_ENERGY_ENTITY)
        temperature_entity = self.config.get(CONF_TEMPERATURE_ENTITY, "")

        power = self._get_state_float(power_entity)
        energy = self._get_state_float(energy_entity, convert_to_wh=True)
        temperature = self._get_state_float(temperature_entity)

        if power is None or energy is None:
            _LOGGER.warning(
                "Skipping upload for system %s: power or energy entity unavailable",
                system_id,
            )
            return

        current_time = dt_util.now()

        payload = {
            "d": current_time.strftime("%Y%m%d"),
            "t": current_time.strftime("%H:%M"),
            "v1": int(energy),
            "v2": int(power),
        }

        if temperature is not None:
            payload["v5"] = round(temperature, 1)

        headers = {
            "X-Pvoutput-Apikey": api_key,
            "X-Pvoutput-SystemId": system_id,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        _LOGGER.debug(
            "Uploading to PVOutput system %s: %s", system_id, payload
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    PVOUTPUT_URL, headers=headers, data=payload, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        _LOGGER.info(
                            "Successfully uploaded to PVOutput system %s: power=%sW energy=%sWh",
                            system_id,
                            int(power),
                            int(energy),
                        )
                    else:
                        text = await response.text()
                        _LOGGER.error(
                            "PVOutput upload failed for system %s: HTTP %s - %s",
                            system_id,
                            response.status,
                            text,
                        )
        except aiohttp.ClientError as err:
            _LOGGER.error(
                "Connection error uploading to PVOutput system %s: %s", system_id, err
            )
        except asyncio.TimeoutError:
            _LOGGER.error(
                "Timeout uploading to PVOutput system %s", system_id
            )