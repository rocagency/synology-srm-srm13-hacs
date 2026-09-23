import logging, voluptuous as vol
from homeassistant import config_entries
from .api import SynologySRMApi,SynologySRMApiError,SynologySRMAuthError
from .const import *
_LOGGER=logging.getLogger(__name__)
class SynologySRMConfigFlow(config_entries.ConfigFlow,domain=DOMAIN):
 VERSION=1
 async def async_step_user(self,user_input=None):
  errors={}
  if user_input:
   scan=user_input.get(CONF_SCAN_INTERVAL,DEFAULT_SCAN_INTERVAL)
   api=SynologySRMApi(self.hass,user_input[CONF_HOST],user_input[CONF_PORT],user_input[CONF_USERNAME],user_input[CONF_PASSWORD],user_input[CONF_SSL],user_input[CONF_VERIFY_SSL])
   try: await api.async_get_devices()
   except SynologySRMAuthError as err: _LOGGER.error("SRM authentication failed: %s",err); errors["base"]="invalid_auth"
   except SynologySRMApiError as err: _LOGGER.error("SRM connection failed: %s",err); errors["base"]="cannot_connect"
   except Exception: _LOGGER.exception("Unexpected SRM setup error"); errors["base"]="unknown"
   else:
    await self.async_set_unique_id(f'{user_input[CONF_HOST]}:{user_input[CONF_PORT]}'); self._abort_if_unique_id_configured()
    data=dict(user_input); data.pop(CONF_SCAN_INTERVAL,None)
    return self.async_create_entry(title=f'Synology SRM ({user_input[CONF_HOST]})',data=data,options={CONF_SCAN_INTERVAL:scan})
  schema=vol.Schema({vol.Required(CONF_HOST):str,vol.Required(CONF_PORT,default=DEFAULT_PORT):vol.Coerce(int),vol.Required(CONF_USERNAME):str,vol.Required(CONF_PASSWORD):str,vol.Required(CONF_SSL,default=False):bool,vol.Required(CONF_VERIFY_SSL,default=True):bool,vol.Optional(CONF_SCAN_INTERVAL,default=DEFAULT_SCAN_INTERVAL):vol.Coerce(int)})
  return self.async_show_form(step_id="user",data_schema=schema,errors=errors)
