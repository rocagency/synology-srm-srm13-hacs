from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator,UpdateFailed
from .const import DOMAIN
from .api import SynologySRMApi,SynologySRMApiError
class SynologySRMCoordinator(DataUpdateCoordinator):
 def __init__(self,hass,api,update_interval):
  self.api=api; super().__init__(hass,logging.getLogger(DOMAIN),name="Synology SRM clients",update_interval=update_interval)
 async def _async_update_data(self):
  try:return await self.api.async_get_devices()
  except SynologySRMApiError as err:raise UpdateFailed(str(err)) from err
