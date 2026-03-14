# Home Monitor Display System

This is a personal repository for a smart home display system setup, using the WaveShare 7.5inch E-ink display on a Raspberry Pi.

## Features

- Automated dashboard updates every 15 minutes
- Weather information display
- E-ink display integration with WaveShare 7.5" display
- Robust error handling and logging
- Easy deployment script for Raspberry Pi

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- WaveShare 7.5" E-ink display (V2)
- MicroSD card (16GB+ recommended)
- Internet connection

## Installation

### Quick Setup (Recommended)

1. Clone the repository to your Raspberry Pi:
   ```bash
   git clone https://github.com/DKJLIM/01_Home-monitor.git
   cd 01_Home-monitor
   ```

2. Make the deployment script executable and run it:
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

This will automatically:
- Install required Python packages
- Set up logging
- Create a cron job to run the dashboard every 15 minutes
- Create wrapper scripts for proper execution

### Manual Setup

If you prefer to set things up manually:

1. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip libfreetype6-dev libjpeg-dev build-essential
   ```

2. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Set up the cron job manually:
   ```bash
   crontab -e
   ```
   Add this line:
   ```
   */15 * * * * /path/to/01_Home-monitor/scripts/run_dashboard.sh # home-monitor
   ```

## Usage

### Available Commands

The deployment script supports several commands:

```bash
# Full deployment (install dependencies, setup cron, test)
./scripts/deploy.sh

# Install dependencies only
./scripts/deploy.sh install

# Setup cron job only
./scripts/deploy.sh setup-cron

# Test the script
./scripts/deploy.sh test

# View live logs
./scripts/deploy.sh logs

# Check status
./scripts/deploy.sh status

# Remove cron job
./scripts/deploy.sh remove
```

### Monitoring

- **View logs**: `./scripts/deploy.sh logs` or `tail -f logs/dashboard.log`
- **Check cron status**: `crontab -l`
- **Manual run**: `python3 tests/flash_dashboard_only_v2.py`

### Logs

Logs are stored in `logs/dashboard.log` and automatically rotated daily (keeping 7 days of history).

## Project Structure

```
├── assets/
│   ├── lib/                # WaveShare EPD library
│   └── pic/               # Images and fonts
├── src/
│   └── modules/           # Custom Python modules
├── tests/
│   └── flash_dashboard_only_v2.py  # Main dashboard script
├── scripts/
│   ├── deploy.sh          # Deployment script
│   └── run_dashboard.sh   # Cron wrapper script (auto-generated)
└── logs/
    └── dashboard.log      # Application logs
```

## Troubleshooting

### Display Issues
- Ensure SPI is enabled: `sudo raspi-config` → Interface Options → SPI → Yes
- Check connections between Pi and display
- Verify display model matches the code (7.5" V2)

### Script Not Running
- Check cron job: `crontab -l`
- View logs: `./scripts/deploy.sh logs`
- Test manually: `python3 tests/flash_dashboard_only_v2.py`

### Permission Issues
- Ensure scripts are executable: `chmod +x scripts/*.sh`
- Check file ownership: `sudo chown -R pi:pi /path/to/01_Home-monitor`

### Common Error Messages
- **"SPI device not found"**: Enable SPI in raspi-config
- **"Permission denied"**: Check file permissions and ownership
- **"Module not found"**: Verify PYTHONPATH and dependency installation

## Configuration

The main script (`flash_dashboard_only_v2.py`) can be customized by modifying:
- Display layout in the dashboard planning section
- Weather data sources
- Update intervals (modify cron schedule)

## Contributing

This is a personal project, but feel free to fork and adapt for your needs.

## License

Personal use license - see project for details.
