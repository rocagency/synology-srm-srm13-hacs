from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SynologySRMApi, SynologySRMApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SynologySRMCoordinator(DataUpdateCoordinator[list[dict]]):
    """Coordinate one SRM API poll for all clients."""

    def __init__(self, hass, api: SynologySRMApi, update_interval: timedelta) -> None:
        self.api = api
        self.clients: dict[str, dict] = {}
        super().__init__(
            hass,
            logger=_LOGGER,
            name="Synology SRM clients",
            update_interval=update_interval,
            always_update=False,
        )

    async def _async_update_data(self) -> list[dict]:
        try:
            data = await self.api.async_get_devices()
        except SynologySRMApiError as err:
            raise UpdateFailed(str(err)) from err

        self.clients = {
            str(device.get("mac", "")).lower(): device
            for device in data
            if device.get("mac")
        }
        return data
