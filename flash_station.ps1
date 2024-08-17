conda activate pico

param (
    [int]$sid,
    [string]$loc,
    [string]$notes
)

# Get current date and time components
$datetime = Get-Date

$yyyy = $datetime.Year
$mm = $datetime.Month
$dd = $datetime.Day
$hh = $datetime.Hour
$min = $datetime.Minute
$ss = $datetime.Second
$dow = [int]$datetime.DayOfWeek
$doy = $datetime.DayOfYear

# Output the components in the form YYYY, MM, DD, HH, MIN, SS, DoW, DoY to datetime.txt
"$yyyy, $mm, $dd, $hh, $min, $ss, $dow, $doy" | Out-File -FilePath "datetime.txt"