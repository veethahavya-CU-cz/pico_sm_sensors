#!/bin/bash
source ~/.bashrc
set +x

# Define Runtime Directory
RUNTIME_DIR="./.flash_station_runtime"

# Define and clear logfile
LOGFILE="flash_station.log"
echo "" >"$LOGFILE"
exec > >(tee -a "$LOGFILE") 2> >(tee -a "$LOGFILE" >&2)

# Define a wrapper function to log and run commands
log_and_run() {
    "$@" >>"$LOGFILE" 2>&1
    status=$?
    if [ $status -ne 0 ]; then
        echo "ERROR: Command '$*' failed with exit code $status." | tee -a "$LOGFILE"
        exit $status
    fi
}

# Define the mpremote command abbreviations
lMPR="log_and_run mpremote "
lMPRr="log_and_run mpremote resume "

# Flag to control datetime.txt generation for datetime updation via external RTC (default: disabled);
## Automatically, the machine RTC is set from the host and then transferred to the external RTC
WRITE_DATETIME=false
READ_DATETIME=false

# Parse arguments, including optional flag
while getopts ":wm" opt; do
    case $opt in
    w)
        WRITE_DATETIME=true
        READ_DATETIME=true
        ;;
    m) 
        READ_DATETIME=true
        if [ ! -f "$RUNTIME_DIR/datetime.txt" ]; then
            echo "Error: Write datetime to $RUNTIME_DIR/datetime.txt when using [-m] in the format [yyyy, mm, dd, hh, mm, ss, dow, doy] without any trailing zeros!" | tee -a "$LOGFILE"
            exit 1
        fi
        ;;
    \?)
        echo "Invalid option: -$OPTARG" | tee -a "$LOGFILE"
        exit 1
        ;;
    esac
done

shift $((OPTIND - 1)) # Shift remaining arguments after options

# Parse the station ID, Location, and Notes from the command line argument
if [ $# -lt 3 ]; then
    echo "Error: Missing arguments." | tee -a "$LOGFILE"
    echo "  -w: Write the current datetime to the station controller via a temporary file" | tee -a "$LOGFILE"
    echo "  -m: Read the datetime from a manually created 'datetime.txt' placed in $RUNTIME_DIR" | tee -a "$LOGFILE"
    echo "Usage: $0 [-wm] <station_id (int)> <location (str)> <notes (str)>" | tee -a "$LOGFILE"
    exit 1
fi

if ! [[ $1 =~ ^[0-9]+$ ]]; then
    echo "Error: station_id must be an integer." | tee -a "$LOGFILE"
    exit 1
fi

sid=$1
loc=$2
notes=$3
mkdir -p $RUNTIME_DIR
echo "sid=$sid" > $RUNTIME_DIR/station.txt
echo "loc=$loc" >> $RUNTIME_DIR/station.txt
echo "notes=$notes" >> $RUNTIME_DIR/station.txt

# Generate datetime.txt only if the flag is set
if [[ $WRITE_DATETIME == true ]]; then
    yyyy=$(date +%Y)
    mm=$(date +%m | sed 's/^0//')
    dd=$(date +%d | sed 's/^0//')
    hh=$(date +%H)
    min=$(date +%M)
    ss=$(date +%S)
    dow=$(date +%w)
    doy=$(date +%j)

    echo "[$yyyy, $mm, $dd, $hh, $min, $ss, $dow, $doy]" > $RUNTIME_DIR/datetime.txt
fi

# Check if the station controller has any files on it and prompt the user to remove them
root_files=$(mpremote resume exec "import os; print(os.listdir())" | tr -d '[:space:]')
if [ $? -ne 0 ] || [ "$root_files" == "nodevicefound" ]; then
    echo "Error: No device found to flash!" | tee -a "$LOGFILE"
    echo -e "  If the device is connected, check if there are any terminals open elsewhere and close it.\n  Micropython REPL can only be accessed by one terminal at a time." | tee -a "$LOGFILE"
    exit 1
fi

if [[ "$root_files" != "[]" && "$root_files" != "['/']" ]]; then
    read -p "The station controller has some files on them: $root_files. Would you like to remove them for a clean install?? (y/n): " choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        $lMPRr run ./src/cleanup.py
    fi
fi

# Turn on the LED on the station controller for identification
$lMPRr exec "from machine import Pin; led = Pin('LED', Pin.OUT); led.on()"

# Install external libraries
echo "Installing libraries: 'upysh', 'os-path', and 'datetime'" && $lMPR mip install upysh os-path datetime
echo "Installing library: 'sdcard'" && $lMPR mip install sdcard
echo "Installing library: 'ds1307'" && $lMPR mip install github:brainelectronics/micropython-ds1307@0.1.1
echo "Installing library: 'dht'" && $lMPR mip install dht

# Install user-libraries
echo "Copying over user-libraries"
$lMPRr mkdir :/usr
$lMPRr mkdir :/usr/lib
$lMPRr cp ./src/lib/picostation_logging.py :/usr/lib/picostation_logging.py
$lMPRr cp ./src/lib/picostation_helper.py :/usr/lib/picostation_helper.py
$lMPRr cp ./src/lib/picostation_wrapper.py :/usr/lib/picostation_wrapper.py

# Copy over the main scripts
echo "Copying over scripts"
$lMPRr cp ./src/boot.py :boot.py
$lMPRr cp ./src/main.py :main.py

# Copy over the metadata and configuration files
echo "Copying over metadata and configuration files"
$lMPRr cp $RUNTIME_DIR/station.txt :station.txt
$lMPRr cp ./machine_config.py :machine_config.py
if [[ $READ_DATETIME == true ]]; then
    echo "Copying over datetime"
    $lMPRr cp $RUNTIME_DIR/datetime.txt :datetime.txt
else
    # (Set the machine time from the host and) Run the setup script
    echo "Setting the machine time from the host"
    $lMPRr rtc --set
    echo "Machine time set to: $(mpremote resume exec "from utime import localtime; from datetime import datetime; print(datetime(*localtime()[:-2]).isoformat())")"
    read -p "Is the timezone information (check the hour) correct? (y/n): " choice
    if [[ "$choice" == "n" || "$choice" == "N" ]]; then
        read -p "Enter the offset in hours (e.g. if actual time is 17:30, but machine was set to 16:30, TZ_OFFSET=1; if actual time is 17:30, but machine was set to 18:00, TZ_OFFSET=-0.5): " TZ_OFFSET
        $lMPRr rtc --set
        $lMPRr exec "from machine import RTC; from datetime import datetime, timedelta; from utime import localtime; now = datetime(*localtime()[:-2]); tz_offset = timedelta(hours=$TZ_OFFSET); now += tz_offset; rtc = RTC(); rtc.datetime(now.timetuple()[:3] + (localtime()[-2], ) + now.timetuple()[3:6] + (0,))"
        echo "Machine time updated to: $(mpremote resume exec "from utime import localtime; from datetime import datetime; print(datetime(*localtime()[:-2]).isoformat())")"
    fi
fi

# Check if SD card works
echo "Checking if the SD card works"
mpremote resume exec "from usys import path as sys_path
sys_path.insert(0, '/usr/lib')
from picostation_wrapper import sd_mount
if not sd_mount():
    raise RuntimeError('SD Card could not be mounted')" > /dev/null 2>&1 || { 
    echo "Failed to mount SD card. Check if it is inserted/connected properly."
    exit 1
}
echo "SD Card works!"

# Check if RTC works
echo "Checking if the RTC works"
mpremote resume exec "from usys import path as sys_path
sys_path.insert(0, '/usr/lib')
from picostation_wrapper import rtc_setup
clock = rtc_setup()
missing_attr = any(not hasattr(clock, attr) for attr in ('datetime', 'halt'))
if missing_attr:
    raise RuntimeError('Unable to connect to RTC. Check the connection.')"
echo "RTC works!"

# Run the setup script
echo "Running the setup script"
$lMPRr run ./src/setup.py
echo "Machine time updated to: $(mpremote resume exec "from utime import localtime; from datetime import datetime; print(datetime(*localtime()[:-2]).isoformat())")"

# Clean up the station controller
echo "Cleaning up"
$lMPRr mkdir :/.archive
$lMPRr cp :station.txt :/.archive/station.txt
$lMPRr cp :machine_config.py :/.archive/machine_config.py
$lMPRr rm :machine_config.py
if [[ $READ_DATETIME == true ]]; then
    $lMPRr cp :datetime.txt :/.archive/datetime.txt
    $lMPRr rm :datetime.txt
fi
$lMPRr rm :station.txt
rm -rf $RUNTIME_DIR

$lMPRr exec "from machine import Pin; led = Pin('LED', Pin.OUT); led.off()"
echo "Station setup complete!"
