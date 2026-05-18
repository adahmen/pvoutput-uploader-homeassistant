# PVOutput Uploader for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration that uploads solar PV data from your HA sensors to [PVOutput.org](https://pvoutput.org).

## Features

- Upload power and energy data to PVOutput every 5 minutes (configurable)
- Support for multiple PVOutput systems (e.g. Garage + Roof)
- Optional temperature upload
- Configurable upload time window (default: 06:00–22:00)
- UI-based configuration (no YAML needed)
- Uses existing HA sensor entities as data source

## Installation via HACS

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots (⋮) → **Custom repositories**
4. Add: `https://github.com/adahmen/ha-pvoutput-uploader` as **Integration**
5. Find **PVOutput Uploader** in HACS and install it
6. Restart Home Assistant

## Manual Installation

1. Copy the `custom_components/pvoutput_uploader` folder to your HA `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **PVOutput Uploader**
3. Fill in:
   - **Name**: A label for this system (e.g. "Garage" or "Roof")
   - **API Key**: Your PVOutput API key (from PVOutput account settings)
   - **System ID**: Your PVOutput System ID
   - **Power entity**: HA sensor with current power in Watts
   - **Energy entity**: HA sensor with daily energy in Wh
   - **Temperature entity**: HA sensor with temperature in °C (optional)
   - **Upload interval**: How often to upload (default: 5 minutes)
   - **Start time**: When to start uploading (default: 06:00)
   - **End time**: When to stop uploading (default: 22:00)

4. Repeat for each PVOutput system (e.g. add a second entry for your second system)

## Requirements

- Home Assistant 2023.1.0 or newer
- A [PVOutput.org](https://pvoutput.org) account with API access enabled
- Existing HA sensors providing power (W) and daily energy (Wh) values

## Logs

Check the HA logs for upload status:
- Successful uploads are logged at `INFO` level
- Errors are logged at `ERROR` level
- Enable `DEBUG` logging for detailed information:

```yaml
logger:
  logs:
    custom_components.pvoutput_uploader: debug
```

## License

MIT License
