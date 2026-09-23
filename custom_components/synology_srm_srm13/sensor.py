"""Sensors for Synology SRM client details."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
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
    DOMAIN,
)
from .coordinator import SynologySRMCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    coordinator: SynologySRMCoordinator = entry.runtime_data
    known = {str(device["mac"]).lower() for device in coordinator.data}

    def _entities_for(device: dict[str, Any]) -> list[SensorEntity]:
        return [
            SRMSignalSensor(coordinator, device),
            SRMInfoSensor(coordinator, device, "connection", ATTR_CONNECTION),
            SRMInfoSensor(coordinator, device, "band", ATTR_BAND),
            SRMInfoSensor(coordinator, device, "ssid", ATTR_SSID),
        ]

    async_add_entities(
        [entity for device in coordinator.data for entity in _entities_for(device)],
        update_before_add=True,
    )

    def _add_new_devices() -> None:
        entities = []
        for device in coordinator.data:
            mac = str(device.get("mac", "")).lower()
            if mac and mac not in known:
                known.add(mac)
                entities.extend(_entities_for(device))
        if entities:
            async_add_entities(entities, update_before_add=True)

    coordinator.async_add_listener(_add_new_devices)


class _SRMSensorBase(CoordinatorEntity[SynologySRMCoordinator], SensorEntity):
    def __init__(self, coordinator: SynologySRMCoordinator, device: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._mac = str(device["mac"]).lower()
        self._device = device

    @property
    def device_info(self) -> DeviceInfo:
        d = self._device
        return DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=str(d.get("hostname") or d.get("ip_addr") or self._mac),
            manufacturer="Synology",
            model="SRM network client",
            via_device=(DOMAIN, "router"),
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_update(self) -> None:
        for device in self.coordinator.data:
            if str(device.get("mac", "")).lower() == self._mac:
                self._device = device
                break


class SRMSignalSensor(_SRMSensorBase):
    """Wi-Fi signal percentage sensor."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:wifi-strength-2"

    def __init__(self, coordinator, device) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._mac}_signal"
        self._attr_name = f"{device.get('hostname') or self._mac} signal"

    @property
    def native_value(self) -> int | None:
        value = self._device.get("signalstrength")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None


class SRMInfoSensor(_SRMSensorBase):
    """Generic SRM client information sensor."""

    def __init__(self, coordinator, device, suffix: str, field: str) -> None:
        super().__init__(coordinator, device)
        self._field = field
        self._attr_unique_id = f"{self._mac}_{suffix}"
        self._attr_name = f"{device.get('hostname') or self._mac} {suffix}"

    @property
    def native_value(self) -> str | None:
        value = self._device.get(self._field)
        return str(value) if value is not None else None
