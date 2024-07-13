def get_next_record_time_localtime(current_time, interval):
    year, month, day, hour, minute, second = current_time
    # Calculate how many intervals have passed since the last full hour
    intervals_passed = minute // interval
    # Calculate the minute of the next interval
    next_interval_minute = (intervals_passed + 1) * interval

    if next_interval_minute >= 60:
        # Move to the next hour
        next_interval_minute -= 60
        hour += 1
        if hour >= 24:
            # Move to the next day (simplified, not accounting for month changes)
            hour = 0
            day += 1

    return (year, month, day, hour, next_interval_minute, 0)

def get_next_record_time_epoch(current_epoch, interval):
    # Calculate the total seconds of the interval
    interval_seconds = interval * 60

    # Find the next interval time by rounding up to the nearest interval
    next_epoch = ((current_epoch + interval_seconds - 1) // interval_seconds) * interval_seconds
    
    return next_epoch

# Example usage
interval = 30

current_time = (2024, 5, 21, 20, 49, 50)
next_time = get_next_record_time_localtime(current_time, interval)
print(next_time)

current_epoch = 1738472990
next_epoch = get_next_record_time_epoch(current_epoch, interval)
print(next_epoch)
