from Monitor import Monitor
from IntervalChecker import IntervalChecker

monitor = Monitor()
result = monitor.scan_directory()

int_check = IntervalChecker()
repetitions = int_check.interval_repetition(result)

print(repetitions)
