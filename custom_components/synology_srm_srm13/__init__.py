from datetime import timedelta
from homeassistant.const import Platform
from .const import *
from .api import SynologySRMApi
from .coordinator import SynologySRMCoordinator
PLATFORMS=[Platform.DEVICE_TRACKER, Platform.SENSOR]
async def async_setup_entry(hass,entry):
 api=SynologySRMApi(hass,entry.data[CONF_HOST],entry.data[CONF_PORT],entry.data[CONF_USERNAME],entry.data[CONF_PASSWORD],entry.data[CONF_SSL],entry.data[CONF_VERIFY_SSL])
 c=SynologySRMCoordinator(hass,api,timedelta(seconds=entry.options.get(CONF_SCAN_INTERVAL,DEFAULT_SCAN_INTERVAL)))
 await c.async_config_entry_first_refresh(); entry.runtime_data=c
 await hass.config_entries.async_forward_entry_setups(entry,PLATFORMS); return True
async def async_unload_entry(hass,entry):
 ok=await hass.config_entries.async_unload_platforms(entry,PLATFORMS)
 if ok: await entry.runtime_data.api.close()
 return ok
