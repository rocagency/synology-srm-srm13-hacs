"""Device tracker entities for Synology SRM 1.3.x."""
from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import ScannerEntity, SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_BAND,
    ATTR_CONNECTION,
    ATTR_DEVICE_TYPE,
    ATTR_HOSTNAME,
    ATTR_IP,
    ATTR_MAC,
    ATTR_SIGNAL,
    ATTR_SSID,
    ATTR_WIRELESS,
    DOMAIN,
    NAME,
)
from .coordinator import SynologySRMCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    coordinator: SynologySRMCoordinator = entry.runtime_data
    known = {str(device["mac"]).lower() for device in coordinator.data}

    def _add_new_devices() -> None:
        new_entities = []
        for device in coordinator.data:
            mac = str(device.get("mac", "")).lower()
            if mac and mac not in known:
                known.add(mac)
                new_entities.append(SRMDeviceTracker(coordinator, device))
        if new_entities:
            async_add_entities(new_entities, update_before_add=True)

    async_add_entities(
        [SRMDeviceTracker(coordinator, device) for device in coordinator.data],
        update_before_add=True,
    )
    coordinator.async_add_listener(_add_new_devices)


class SRMDeviceTracker(CoordinatorEntity[SynologySRMCoordinator], ScannerEntity):
    """Represent a client tracked by SRM."""

    _attr_source_type = SourceType.ROUTER

    def __init__(self, coordinator: SynologySRMCoordinator, device: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._mac = str(device["mac"]).lower()
        self._device = device
        self._attr_unique_id = self._mac
        self._attr_name = self._display_name(device)

    @property
    def device_info(self) -> DeviceInfo:
        d = self._device
        return DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=self._display_name(d),
            manufacturer="Synology",
            model="SRM network client",
            via_device=(DOMAIN, "router"),
        )

    @property
    def is_connected(self) -> bool:
        return bool(self._device.get("is_online", False))

    @property
    def mac_address(self) -> str:
        return self._mac

    @property
    def ip_address(self) -> str | None:
        return self._device.get("ip_addr")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self._device
        return {
            ATTR_IP: d.get("ip_addr"),
            ATTR_MAC: d.get("mac"),
            ATTR_HOSTNAME: d.get("hostname"),
            ATTR_CONNECTION: d.get("connection"),
            ATTR_WIRELESS: d.get("is_wireless"),
            ATTR_BAND: d.get("band"),
            ATTR_SIGNAL: d.get("signalstrength"),
            ATTR_SSID: d.get("wifi_ssid"),
            ATTR_DEVICE_TYPE: d.get("dev_type"),
        }

    async def async_update(self) -> None:
        for device in self.coordinator.data:
            if str(device.get("mac", "")).lower() == self._mac:
                self._device = device
                if device.get("hostname"):
                    self._attr_name = self._display_name(device)
                break

    def _display_name(self, device: dict[str, Any]) -> str:
        return str(
            device.get("hostname")
            or device.get("ip_addr")
            or device.get("mac")
            or "SRM client"
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
