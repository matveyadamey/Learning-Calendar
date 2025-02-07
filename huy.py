import schedule
import time
from sys import exit


def print_huy():
    print("huy")

# Choose the selection - For the purpose of the blog I will use just this
schedule.every(1).minute.do(print_huy)

while True:
    schedule.run_pending()
    time.sleep(1)

