from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SynologySRMCoordinator


class SRMClientEntity(CoordinatorEntity[SynologySRMCoordinator]):
    """Base entity for one SRM network client."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SynologySRMCoordinator, mac: str) -> None:
        super().__init__(coordinator)
        self.mac = mac.lower()
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.mac)},
            name=self.client_name,
            manufacturer="Synology",
            model="SRM network client",
        )

    @property
    def client(self) -> dict:
        return self.coordinator.clients.get(self.mac, {})

    @property
    def client_name(self) -> str:
        data = self.coordinator.clients.get(self.mac, {})
        return data.get("hostname") or self.mac

    @property
    def available(self) -> bool:
        return self.mac in self.coordinator.clients

    def refresh_device_info(self) -> None:
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.mac)},
            name=self.client_name,
            manufacturer="Synology",
            model="SRM network client",
        )
