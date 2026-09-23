from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT

from .entity import SRMClientEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = entry.runtime_data
    known: set[tuple[str, str]] = set()

    def add_new_clients() -> None:
        entities = []
        for mac in coordinator.clients:
            for kind in ("signal", "connection", "band", "ssid", "device_type"):
                key = (mac, kind)
                if key in known:
                    continue
                known.add(key)
                entities.append(SRMClientSensor(coordinator, mac, kind))
        if entities:
            async_add_entities(entities)

    add_new_clients()
    entry.async_on_unload(coordinator.async_add_listener(add_new_clients))


class SRMClientSensor(SRMClientEntity, SensorEntity):
    """Diagnostic data exposed by SRM for one client."""

    def __init__(self, coordinator, mac: str, kind: str) -> None:
        super().__init__(coordinator, mac)
        self.kind = kind
        self._attr_unique_id = f"{mac}-{kind}"
        self._attr_entity_category = None
        self._attr_device_class = None
        self._attr_native_unit_of_measurement = None
        self._attr_state_class = None
        self._attr_name = {
            "signal": "Signal strength",
            "connection": "Connection",
            "band": "Wi-Fi band",
            "ssid": "SSID",
            "device_type": "Device type",
        }[kind]
        if kind == "signal":
            self._attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
            self._attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        d = self.client
        if self.kind == "signal":
            value = d.get("signalstrength", d.get("signal_strength"))
            try:
                return float(value) if value is not None else None
            except (TypeError, ValueError):
                return None
        if self.kind == "connection":
            return d.get("connection")
        if self.kind == "band":
            return d.get("band")
        if self.kind == "ssid":
            return d.get("wifi_ssid", d.get("ssid"))
        return d.get("dev_type", d.get("device_type"))
