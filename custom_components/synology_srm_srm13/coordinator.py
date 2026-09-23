"""Data coordinator for Synology SRM."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SynologySRMApi, SynologySRMApiError
from .const import DOMAIN


class SynologySRMCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Coordinate SRM client updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SynologySRMApi,
        update_interval: timedelta,
    ) -> None:
        self.api = api
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(DOMAIN),
            name="Synology SRM clients",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> list[dict[str, Any]]:
        try:
            return await self.api.async_get_devices()
        except SynologySRMApiError as err:
            raise UpdateFailed(str(err)) from err
