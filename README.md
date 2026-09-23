# Synology SRM 1.3.x for Home Assistant

Custom Home Assistant integration for Synology SRM 1.3.x.

## v0.1.3

Critical authentication fix: Synology's Web API requires the returned session ID
to be sent as `_sid` on subsequent API requests when login uses `format=sid`.

The integration uses:
- `SYNO.API.Auth` v3
- `SYNO.Core.Network.NSM.Device` v5 / `get`
- `/webapi/auth.cgi`
- `/webapi/entry.cgi`

Credentials and `_sid` are masked in debug logs.
