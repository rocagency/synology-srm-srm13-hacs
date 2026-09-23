"""Minimal async client for Synology SRM 1.3.x APIs."""
from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession
from homeassistant.core import HomeAssistant

from .const import (
    API_AUTH,
    API_DEVICE,
    API_VERSION_AUTH,
    API_VERSION_DEVICE,
)


class SynologySRMApiError(Exception):
    """Raised when Synology SRM returns an API error."""


class SynologySRMAuthError(SynologySRMApiError):
    """Raised when authentication fails."""


class SynologySRMApi:
    """Async client for the SRM 1.3.x WebAPI."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool,
        verify_ssl: bool,
    ) -> None:
        self._hass = hass
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        self._session: ClientSession = async_get_clientsession(hass)
        self._sid: str | None = None
        self._lock = asyncio.Lock()

    @property
    def base_url(self) -> str:
        scheme = "https" if self.use_ssl else "http"
        return f"{scheme}://{self.host}:{self.port}/webapi"

    async def close(self) -> None:
        """Close is a no-op because Home Assistant owns the shared session."""

    async def async_login(self) -> None:
        """Authenticate and obtain a session ID."""
        params = {
            "api": API_AUTH,
            "version": API_VERSION_AUTH,
            "method": "login",
            "account": self.username,
            "passwd": self.password,
            "session": "HomeAssistant",
            "format": "sid",
        }
        data = await self._request("auth.cgi", params, auth_request=True)
        if not data.get("success"):
            raise SynologySRMAuthError(self._format_error(data))
        self._sid = data.get("data", {}).get("sid")
        if not self._sid:
            raise SynologySRMAuthError("SRM did not return a session ID")

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Return devices known by SRM 1.3.x."""
        async with self._lock:
            if not self._sid:
                await self.async_login()

            params = {
                "api": API_DEVICE,
                "version": API_VERSION_DEVICE,
                "method": "get",
                "sid": self._sid,
            }
            try:
                data = await self._request("entry.cgi", params)
            except SynologySRMApiError:
                self._sid = None
                await self.async_login()
                params["sid"] = self._sid
                data = await self._request("entry.cgi", params)

        if not data.get("success"):
            raise SynologySRMApiError(self._format_error(data))

        devices = data.get("data", {}).get("devices", [])
        if not isinstance(devices, list):
            raise SynologySRMApiError("Unexpected SRM device-list response")
        return [d for d in devices if isinstance(d, dict) and d.get("mac")]

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
        auth_request: bool = False,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        ssl = self.verify_ssl if self.use_ssl else False

        try:
            async with self._session.get(
                url,
                params=params,
                ssl=ssl,
                timeout=15,
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, asyncio.TimeoutError, ValueError) as err:
            raise SynologySRMApiError(str(err)) from err

        if not isinstance(payload, dict):
            raise SynologySRMApiError("Invalid JSON response from SRM")

        if not payload.get("success") and auth_request:
            raise SynologySRMAuthError(self._format_error(payload))

        return payload

    @staticmethod
    def _format_error(payload: dict[str, Any]) -> str:
        error = payload.get("error") or {}
        code = error.get("code")
        if code is not None:
            return f"Synology SRM API error {code}"
        return "Synology SRM API request failed"
