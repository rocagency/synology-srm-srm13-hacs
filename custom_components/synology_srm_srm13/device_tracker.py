from homeassistant.components.device_tracker import ScannerEntity,SourceType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import *
async def async_setup_entry(hass,entry,async_add_entities):
 async_add_entities([SRMTracker(entry.runtime_data,d) for d in entry.runtime_data.data],update_before_add=True)
class SRMTracker(CoordinatorEntity,ScannerEntity):
 _attr_source_type=SourceType.ROUTER
 def __init__(self,c,d):
  super().__init__(c); self.mac=d["mac"].lower(); self.d=d; self._attr_unique_id=self.mac; self._attr_name=d.get("hostname") or self.mac
 @property
 def device_info(self): return DeviceInfo(identifiers={(DOMAIN,self.mac)},name=self._attr_name,manufacturer="Synology",model="SRM network client")
 @property
 def is_connected(self): return bool(self.d.get("is_online"))
 @property
 def mac_address(self): return self.mac
 @property
 def ip_address(self): return self.d.get("ip_addr")
 @property
 def extra_state_attributes(self): return {ATTR_IP:self.d.get("ip_addr"),ATTR_MAC:self.d.get("mac"),ATTR_HOSTNAME:self.d.get("hostname"),ATTR_CONNECTION:self.d.get("connection"),ATTR_WIRELESS:self.d.get("is_wireless"),ATTR_BAND:self.d.get("band"),ATTR_SIGNAL:self.d.get("signalstrength"),ATTR_SSID:self.d.get("wifi_ssid"),ATTR_DEVICE_TYPE:self.d.get("dev_type")}
 async def async_update(self):
  for d in self.coordinator.data:
   if str(d.get("mac","")).lower()==self.mac: self.d=d; break
