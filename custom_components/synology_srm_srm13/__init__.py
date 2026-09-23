"""Synology SRM 1.3.x integration for Home Assistant."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SynologySRMApi, SynologySRMApiError
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .coordinator import SynologySRMCoordinator

PLATFORMS: list[Platform] = [Platform.DEVICE_TRACKER, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = SynologySRMApi(
        hass=hass,
        host=entry.data["host"],
        port=entry.data["port"],
        username=entry.data["username"],
        password=entry.data["password"],
        use_ssl=entry.data["ssl"],
        verify_ssl=entry.data["verify_ssl"],
    )
    coordinator = SynologySRMCoordinator(
        hass,
        api,
        update_interval=timedelta(
            seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        ),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        await api.close()
        raise UpdateFailed(f"Unable to contact Synology SRM: {err}") from err

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.api.close()
    return unloaded
