import datetime


def time_to_minutes(time):
    time = time.split(':')
    return int(time[0]) * 60 + int(time[1])


def check_intervals(time1, time2):
    time1 = time1.split('-')
    time1 = time_to_minutes(time1[0]), time_to_minutes(time1[1])
    time2 = time2.split('-')
    time2 = time_to_minutes(time2[0]), time_to_minutes(time2[1])
    if time1[0] < time2[0] < time1[1] or time1[0] < time2[1] < time1[1]:
        return True
    return False


def check_time(time1, time2):
    for i in time1:
        for j in time2:
            if check_intervals(i, j) or check_intervals(j, i):
                return True
    return False


def format_date(date: datetime.datetime):
    return date.isoformat('T')[:-4] + 'Z'


def calculate_time(time1: str, time2: str) -> int:
    time1 = datetime.datetime.fromisoformat(time1[:-4])
    time2 = datetime.datetime.fromisoformat(time2[:-4])
    time = time2 - time1
    return time.seconds


def validate_time_interval(time_interval):
    try:
        start, end = time_interval.split('-')
        start, end = list(map(int, start.split(':'))), list(map(int, end.split(':')))
    except Exception:
        return 'Wrong time interval format. Correct usage: "HH:MM-HH:MM"'
    if not (0 <= start[0] <= 24 and 0 <= end[0] <= 24 and 0 <= start[1] <= 60 and 0 <= end[1] <= 60):
        return 'There are only 24 hours in a day and 60 minutes in an hour.'
    return None


def calculate_capacity(courier_type):
    capacity_table = {'foot': 10, 'bike': 15, 'car': 50}
    return capacity_table[courier_type]
