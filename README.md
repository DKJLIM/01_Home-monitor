# Home Monitor Display System

This is a personal repository for a smart home display system setup, using the WaveShare 7.5inch E-ink display on a Raspberry Pi.

## Features

- Live dashboard refreshed every 60 seconds
- TfL (Transport for London) live arrivals
- E-ink display integration with WaveShare 7.5" display
- Runs as a systemd service: starts on boot, restarts automatically on crash

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- WaveShare 7.5" E-ink display (V2)
- MicroSD card (16GB+ recommended)
- Internet connection

## Installation

1. Clone the repository to your Raspberry Pi:
   ```bash
   git clone https://github.com/DKJLIM/01_Home-monitor.git home-monitor
   cd home-monitor
   ```

2. Run the setup script:
   ```bash
   ./scripts/start.sh
   ```

This will:
- Enable the SPI interface (required for the e-ink display)
- Install required system and Python packages
- Create a virtual environment and install the project into it
- Install and start `home-monitor.service` via systemd, enabled to start on boot

Re-running `./scripts/start.sh` at any time is safe — setup steps are skipped
if already done, and the systemd service is reinstalled/restarted with
whatever's currently checked out.

## Usage

The dashboard runs as a systemd service (`home-monitor.service`), not a
foreground process — manage it with `systemctl`/`journalctl`:

```bash
# Check whether it's running
systemctl status home-monitor

# Follow live logs
journalctl -u home-monitor -f

# Restart it (e.g. after a manual code change without a full ./scripts/start.sh)
sudo systemctl restart home-monitor

# Stop it
sudo systemctl stop home-monitor

# Disable it from starting on boot
sudo systemctl disable home-monitor
```

### Optional: TfL API key

The dashboard works without one (unauthenticated requests, lower rate limit).
To use a key, put it in a `.env` file in the repo root on the Pi:
```
TFL_API_KEY=your_key_here
```
`home-monitor.service` reads this file automatically (`.env` is gitignored,
so it's never committed).

## Development

The dashboard can be iterated on entirely on your own machine — no Pi or
e-ink hardware needed:

```bash
# One-shot: render the current dashboard to dashboard_preview.png and exit
python src/run.py --preview

# Live iterate loop: re-renders on every save and auto-refreshes a browser tab
python scripts/dev_preview.py
```

`--preview` skips all display-hardware initialisation (`ScreenRenderer`
falls back automatically if the WaveShare driver isn't importable anyway),
so this works the same on macOS/Linux dev machines as it does on the Pi.

## Project Structure

```
├── src/
│   ├── run.py              # Entry point — the long-running dashboard loop
│   │                       #   (also supports `--preview` for one-shot local rendering)
│   └── modules/            # Custom Python modules (screen renderer, TfL client, etc.)
│   └── assets/
│       └── lib/            # Vendored WaveShare EPD driver
├── scripts/
│   ├── start.sh            # Setup + installs/starts the systemd service
│   ├── home-monitor.service  # systemd unit definition
│   └── dev_preview.py       # Local live-preview dev loop
```

## Troubleshooting

### Display Issues
- Ensure SPI is enabled: `sudo raspi-config` → Interface Options → SPI → Yes
- Check connections between Pi and display
- Verify display model matches the code (7.5" V2)

### Service Not Running
- Check status: `systemctl status home-monitor`
- View logs: `journalctl -u home-monitor -e`
- Re-run setup: `./scripts/start.sh`

### Common Error Messages
- **"SPI device not found"**: Enable SPI in raspi-config
- **"Permission denied"**: Check that the Pi user running the service (`dkjlim`) has access to `/dev/gpiomem` and `/dev/spidev*` (normally via the `gpio`/`spi` groups)

## Contributing

This is a personal project, but feel free to fork and adapt for your needs.

## License

Personal use license - see project for details.
