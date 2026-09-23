# Synology SRM 1.3.x for Home Assistant

Custom HACS integration for Synology routers running SRM 1.3.x, including the RT6600ax.

## v0.2.0

- Uses the SRM 1.3.x `SYNO.Core.Network.NSM.Device` API.
- Correctly passes the authentication session as `_sid`.
- One Home Assistant device per discovered network client (MAC address).
- Automatic discovery of clients that appear after startup.
- Device tracker with online/offline state, MAC, IP and hostname.
- Diagnostic sensors for signal strength, connection, Wi-Fi band, SSID and device type when SRM provides those fields.
- Centralized polling through `DataUpdateCoordinator`.

Home Assistant recommends a coordinator for a single periodic API poll shared by multiple entities, and `ScannerEntity` is the network device-tracker model for clients identified by MAC address. See the Home Assistant developer documentation for those models.

## Installation

1. In HACS, add this repository as a custom repository of type **Integration**.
2. Install **Synology SRM 1.3.x**.
3. Restart Home Assistant.
4. Add the integration from **Settings → Devices & services**.
5. Enter the SRM address, API port (usually 8000), credentials and polling interval.

## Notes

This integration is local-only and does not send SRM credentials to an external service.
