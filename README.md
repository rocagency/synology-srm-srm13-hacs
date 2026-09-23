# Synology SRM 1.3.x for Home Assistant

Custom Home Assistant integration for Synology Router Manager (SRM) 1.3.x, using the replacement API:

`SYNO.Core.Network.NSM.Device` version 5, method `get`.

This is intended for routers such as the RT6600ax running SRM 1.3.x.

## Why this exists

The built-in Home Assistant `synology_srm` integration uses the legacy `SYNO.SRM.*` API namespace. SRM 1.3.x removed that namespace, so the legacy integration can authenticate but return an empty device list.

This integration uses the SRM 1.3.x replacement endpoint.

## Features

For each client returned by SRM:

- Online/offline device tracker
- IP address
- MAC address
- Hostname
- Connection type
- Wireless flag
- Wi-Fi band
- Wi-Fi SSID
- Signal strength when SRM reports it
- Device type

## Installation with HACS

1. Create a public GitHub repository named `synology-srm-srm13`.
2. Upload this repository.
3. In HACS, open **Integrations**.
4. Open the three-dot menu and choose **Custom repositories**.
5. Add your GitHub repository URL.
6. Select category **Integration**.
7. Install **Synology SRM 1.3.x**.
8. Restart Home Assistant.
9. Go to **Settings → Devices & services → Add integration**.
10. Search for **Synology SRM 1.3.x**.

HACS requires the integration to be under `custom_components/<domain>/` and the repository to contain the required manifest metadata.

## RT6600ax / SRM 1.3.1

Typical settings:

- Host: the LAN IP of the RT6600ax
- Port: `8000` for HTTP or the appropriate HTTPS WebAPI port
- HTTPS: enable only if your SRM WebAPI is configured for HTTPS
- Verify HTTPS certificate: disable if you use a self-signed certificate
- Polling interval: 30 seconds is a reasonable starting point

## Important

This is a community custom integration. It is not an official Synology or Home Assistant integration.

The SRM API is not a public stable API contract, so future SRM updates may change its behavior.

The implementation deliberately does not use the third-party `synology-srm` Python package; it calls the SRM WebAPI directly through Home Assistant's aiohttp session.

## API reference

The replacement API documented in the Home Assistant issue below returns fields including:

`mac`, `ip_addr`, `hostname`, `is_online`, `is_wireless`, `connection`, `band`, `signalstrength`, and `wifi_ssid`.

See:
https://github.com/home-assistant/core/issues/164646

## Development

The repository can be validated with Home Assistant's development tooling. Add automated tests before considering this integration production-grade.
