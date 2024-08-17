#!/bin/bash
source ~/.bashrc
set +x

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

# Flag to control datetime.txt generation for datetime updation via external RTC (default: disabled); Automatically, the machine RTC is set from the host and then transferred to the external RTC
WRITE_DATETIME=false

# Parse arguments, including optional flag
while getopts ":dt:" opt; do
    case $opt in
    d) WRITE_DATETIME=true ;;
    t) echo "Warning: -t flag is deprecated, use -d instead." ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    esac
done

shift $((OPTIND - 1)) # Shift remaining arguments after options

# Parse the station ID, Location, and Notes from the command line argument
if [ $# -lt 3 ]; then
    echo "Error: Missing arguments." | tee -a "$LOGFILE"
    echo "Usage: $0 [-d] <station_id (int)> <location (str)> <notes (str)>" | tee -a "$LOGFILE"
    exit 1
fi

if ! [[ $1 =~ ^[0-9]+$ ]]; then
    echo "Error: station_id must be an integer." | tee -a "$LOGFILE"
    exit 1
fi

sid=$1
loc=$2
notes=$3
echo "sid=$sid" >./.tmp/station.txt
echo "loc=$loc" >>./.tmp/station.txt
echo "notes=$notes" >>./.tmp/station.txt

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

    echo "[$yyyy, $mm, $dd, $hh, $min, $ss, $dow, $doy]" >./.tmp/datetime.txt
fi

# Check if the station controller has any files on it and prompt the user to remove them
root_files=$(mpremote resume exec "import os; print(os.listdir())" | tr -d '[:space:]')
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
$lMPRr cp ./.tmp/station.txt :station.txt
$lMPRr cp ./machine_config.py :machine_config.py
if [[ $WRITE_DATETIME == true ]]; then
    echo "Copying over datetime"
    $lMPRr cp ./.tmp/datetime.txt :datetime.txt
fi

# (Set the machine time from the host and) Run the setup script
echo "Setting the machine time from the host"
$lMPRr rtc --set
echo "Running the setup script"
$lMPRr run ./src/setup.py

# Clean up the station controller
echo "Cleaning up"
$lMPRr mkdir :/.archive
$lMPRr cp :station.txt :/.archive/station.txt
$lMPRr cp :machine_config.py :/.archive/machine_config.py
if [[ $WRITE_DATETIME == true ]]; then
    $lMPRr cp :datetime.txt :/.archive/datetime.txt
    $lMPRr rm :datetime.txt
fi
$lMPRr rm :station.txt

$lMPRr exec "from machine import Pin; led = Pin('LED', Pin.OUT); led.off()"
echo "Station setup complete!"
