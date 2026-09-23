from __future__ import annotations
import asyncio, logging
from aiohttp import ClientError, ClientSession
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import *
_LOGGER=logging.getLogger(__name__)
class SynologySRMApiError(Exception): pass
class SynologySRMAuthError(SynologySRMApiError): pass
class SynologySRMApi:
 def __init__(self,hass:HomeAssistant,host,port,username,password,use_ssl,verify_ssl):
  self.host,self.port,self.username,self.password=host,port,username,password
  self.use_ssl,self.verify_ssl=use_ssl,verify_ssl
  self._session:ClientSession=async_get_clientsession(hass); self._sid=None
 @property
 def base_url(self): return f'{"https" if self.use_ssl else "http"}://{self.host}:{self.port}/webapi'
 async def close(self): pass
 async def async_login(self):
  data=await self._request("auth.cgi",{"api":API_AUTH,"version":API_VERSION_AUTH,"method":"login","account":self.username,"passwd":self.password,"session":"HomeAssistant","format":"sid"})
  if not data.get("success"): raise SynologySRMAuthError(self._format_error(data))
  self._sid=(data.get("data") or {}).get("sid")
  if not self._sid: raise SynologySRMAuthError("SRM did not return a session ID")
 async def async_get_devices(self):
  if not self._sid: await self.async_login()
  p={"api":API_DEVICE,"version":API_VERSION_DEVICE,"method":"get","sid":self._sid}
  data=await self._request("entry.cgi",p)
  if not data.get("success"):
   self._sid=None; await self.async_login(); p["sid"]=self._sid; data=await self._request("entry.cgi",p)
  if not data.get("success"): raise SynologySRMApiError(self._format_error(data))
  devices=(data.get("data") or {}).get("devices",[])
  if not isinstance(devices,list): raise SynologySRMApiError("Unexpected SRM device-list response")
  return [d for d in devices if isinstance(d,dict) and d.get("mac")]
 async def _request(self,endpoint,params):
  safe=dict(params)
  if "passwd" in safe: safe["passwd"]="***"
  if "sid" in safe: safe["sid"]="***"
  _LOGGER.debug("SRM API request %s params=%s",endpoint,safe)
  try:
   async with self._session.get(f"{self.base_url}/{endpoint}",params=params,ssl=self.verify_ssl if self.use_ssl else False,timeout=15) as r:
    r.raise_for_status(); data=await r.json(content_type=None)
  except (ClientError,asyncio.TimeoutError,ValueError) as err:
   raise SynologySRMApiError(f"Transport error contacting {self.host}:{self.port}: {err}") from err
  _LOGGER.debug("SRM API response success=%s error=%s",data.get("success"),data.get("error"))
  return data
 @staticmethod
 def _format_error(payload):
  e=payload.get("error") or {}; parts=[]
  if "code" in e: parts.append(f"code={e['code']}")
  if e.get("reason"): parts.append(f"reason={e['reason']}")
  if e.get("details"): parts.append(f"details={e['details']}")
  return "Synology SRM API error: "+", ".join(parts) if parts else "SRM API request failed"
