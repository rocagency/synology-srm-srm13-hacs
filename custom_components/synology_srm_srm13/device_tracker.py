from __future__ import annotations

from homeassistant.components.device_tracker import ScannerEntity, SourceType

from .entity import SRMClientEntity


def _macs(coordinator) -> set[str]:
    return set(coordinator.clients)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = entry.runtime_data
    known: set[str] = set()

    def add_new_clients() -> None:
        new_macs = _macs(coordinator) - known
        if not new_macs:
            return
        entities = [SRMTracker(coordinator, mac) for mac in sorted(new_macs)]
        known.update(new_macs)
        async_add_entities(entities)

    add_new_clients()

    def coordinator_updated() -> None:
        add_new_clients()

    entry.async_on_unload(coordinator.async_add_listener(coordinator_updated))


class SRMTracker(SRMClientEntity, ScannerEntity):
    """Presence tracker for one SRM client."""

    _attr_source_type = SourceType.ROUTER

    def __init__(self, coordinator, mac: str) -> None:
        super().__init__(coordinator, mac)
        self._attr_unique_id = f"{mac}-presence"
        self._attr_name = "Presence"

    @property
    def is_connected(self) -> bool:
        return bool(self.client.get("is_online", self.client.get("online", False)))

    @property
    def mac_address(self) -> str:
        return self.mac

    @property
    def ip_address(self) -> str | None:
        return self.client.get("ip_addr") or self.client.get("ip")

    @property
    def hostname(self) -> str | None:
        return self.client.get("hostname")
