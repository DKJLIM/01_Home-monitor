#!/bin/bash

# Home Monitor Deployment Script for Raspberry Pi
# This script sets up the home monitor to run flash_dashboard_only_v2.py every 15 minutes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="home-monitor"
SCRIPT_NAME="flash_dashboard_only_v2.py"
RUN_INTERVAL="*/15 * * * *"  # Every 15 minutes
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="${PROJECT_DIR}/tests/${SCRIPT_NAME}"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/dashboard.log"
PYTHON_CMD="python3"

echo -e "${GREEN}=== Home Monitor Deployment Script ===${NC}"
echo -e "Project Directory: ${PROJECT_DIR}"
echo -e "Script Path: ${SCRIPT_PATH}"
echo -e "Log File: ${LOG_FILE}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    print_status "Checking if running on Raspberry Pi..."
    if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null && ! grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
        print_warning "This doesn't appear to be a Raspberry Pi, but continuing anyway..."
    else
        print_status "Raspberry Pi detected!"
    fi
}

# Check if script exists
check_script_exists() {
    print_status "Checking if script exists..."
    if [ ! -f "${SCRIPT_PATH}" ]; then
        print_error "Script ${SCRIPT_PATH} not found!"
        exit 1
    fi
    print_status "Script found: ${SCRIPT_PATH}"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Update package list
    sudo apt-get update -qq
    
    # Install system dependencies
    sudo apt-get install -y python3 python3-pip python3-venv libfreetype6-dev libjpeg-dev build-essential
    
    # Install Python packages
    ${PYTHON_CMD} -m pip install --upgrade pip
    ${PYTHON_CMD} -m pip install Pillow spidev RPi.GPIO gpiozero
    
    # Install waveshare epd library if not already present
    if [ -d "${PROJECT_DIR}/assets/lib/waveshare_epd" ]; then
        print_status "Waveshare EPD library found in assets/lib"
    else
        print_warning "Waveshare EPD library not found, you may need to install it manually"
    fi
}

# Create log directory
setup_logging() {
    print_status "Setting up logging..."
    mkdir -p "${LOG_DIR}"
    touch "${LOG_FILE}"
    chmod 644 "${LOG_FILE}"
    
    # Create log rotation configuration
    sudo tee /etc/logrotate.d/home-monitor > /dev/null <<EOF
${LOG_FILE} {
    daily
    missingok
    rotate 7
    compress
    notifempty
    copytruncate
}
EOF
    print_status "Log rotation configured"
}

# Create wrapper script for cron
create_wrapper_script() {
    print_status "Creating wrapper script for cron execution..."
    
    WRAPPER_SCRIPT="${PROJECT_DIR}/scripts/run_dashboard.sh"
    
    cat > "${WRAPPER_SCRIPT}" <<EOF
#!/bin/bash

# Wrapper script for running flash_dashboard_only_v2.py
# This script ensures proper environment and logging for cron execution

# Set environment
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH="${PROJECT_DIR}/src:${PROJECT_DIR}/assets/lib:\$PYTHONPATH"

# Change to project directory
cd "${PROJECT_DIR}"

# Create lock file to prevent multiple instances
LOCK_FILE="/tmp/home-monitor.lock"
if [ -f "\$LOCK_FILE" ]; then
    echo "\$(date): Another instance is running, exiting..." >> "${LOG_FILE}"
    exit 1
fi

echo \$$ > "\$LOCK_FILE"

# Function to cleanup on exit
cleanup() {
    rm -f "\$LOCK_FILE"
}
trap cleanup EXIT

# Log start time
echo "\$(date): Starting dashboard update..." >> "${LOG_FILE}"

# Run the Python script with timeout (10 minutes max)
timeout 600 ${PYTHON_CMD} "${SCRIPT_PATH}" >> "${LOG_FILE}" 2>&1

EXIT_CODE=\$?

if [ \$EXIT_CODE -eq 0 ]; then
    echo "\$(date): Dashboard update completed successfully" >> "${LOG_FILE}"
elif [ \$EXIT_CODE -eq 124 ]; then
    echo "\$(date): Dashboard update timed out" >> "${LOG_FILE}"
else
    echo "\$(date): Dashboard update failed with exit code \$EXIT_CODE" >> "${LOG_FILE}"
fi

# Cleanup
cleanup
EOF

    chmod +x "${WRAPPER_SCRIPT}"
    print_status "Wrapper script created: ${WRAPPER_SCRIPT}"
}

# Setup cron job
setup_cron() {
    print_status "Setting up cron job to run every 15 minutes..."
    
    # Remove existing cron jobs for this project
    (crontab -l 2>/dev/null | grep -v "${PROJECT_NAME}" || true) | crontab -
    
    # Add new cron job
    (crontab -l 2>/dev/null || true; echo "${RUN_INTERVAL} ${PROJECT_DIR}/scripts/run_dashboard.sh # ${PROJECT_NAME}") | crontab -
    
    print_status "Cron job added:"
    echo -e "  ${RUN_INTERVAL} ${PROJECT_DIR}/scripts/run_dashboard.sh"
    echo ""
    print_status "Current crontab:"
    crontab -l | grep "${PROJECT_NAME}" || echo "  (no entries found)"
}

# Test the script
test_script() {
    print_status "Testing the script execution..."
    echo "This will run the dashboard script once to test it..."
    read -p "Do you want to run a test? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Running test..."
        cd "${PROJECT_DIR}"
        ${PYTHON_CMD} "${SCRIPT_PATH}" 2>&1 | tee -a "${LOG_FILE}"
        print_status "Test completed. Check the display and log file for any issues."
    else
        print_status "Skipping test."
    fi
}

# Main deployment function
main() {
    echo -e "${GREEN}Starting deployment...${NC}"
    echo ""
    
    check_raspberry_pi
    check_script_exists
    install_dependencies
    setup_logging
    create_wrapper_script
    setup_cron
    
    echo ""
    print_status "Deployment completed successfully!"
    echo ""
    echo -e "${GREEN}=== Summary ===${NC}"
    echo -e "• Script will run every 15 minutes"
    echo -e "• Logs will be written to: ${LOG_FILE}"
    echo -e "• Wrapper script: ${PROJECT_DIR}/scripts/run_dashboard.sh"
    echo -e "• To view logs: tail -f ${LOG_FILE}"
    echo -e "• To check cron status: crontab -l"
    echo -e "• To remove cron job: crontab -e (and delete the ${PROJECT_NAME} line)"
    echo ""
    
    test_script
}

# Handle command line arguments
case "${1:-}" in
    "install")
        install_dependencies
        ;;
    "setup-cron")
        setup_cron
        ;;
    "test")
        test_script
        ;;
    "logs")
        tail -f "${LOG_FILE}"
        ;;
    "status")
        echo "Cron jobs:"
        crontab -l | grep "${PROJECT_NAME}" || echo "No cron jobs found"
        echo ""
        echo "Recent logs:"
        tail -10 "${LOG_FILE}" 2>/dev/null || echo "No logs found"
        ;;
    "remove")
        print_status "Removing cron job..."
        (crontab -l 2>/dev/null | grep -v "${PROJECT_NAME}" || true) | crontab -
        print_status "Cron job removed"
        ;;
    *)
        if [ $# -eq 0 ]; then
            main
        else
            echo "Usage: $0 [install|setup-cron|test|logs|status|remove]"
            echo ""
            echo "Commands:"
            echo "  install     - Install dependencies only"
            echo "  setup-cron  - Setup cron job only"
            echo "  test        - Test script execution"
            echo "  logs        - View live logs"
            echo "  status      - Show current status"
            echo "  remove      - Remove cron job"
            echo "  (no args)   - Full deployment"
            exit 1
        fi
        ;;
esac