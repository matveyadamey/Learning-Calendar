import datetime

class IntervalChecker:
    def interval_repetition(self,notes_dict):
        today = datetime.datetime.now()
        repetitions = []
        for note, creation_date in notes_dict.items():
            time_difference = today - datetime.datetime.fromtimestamp(creation_date)
            
            if time_difference == datetime.timedelta(minutes=20):
                repetitions.append((note, creation_date))
            elif time_difference == datetime.timedelta(hours=1):
                repetitions.append((note, creation_date))
            elif time_difference == datetime.timedelta(hours=8):
                repetitions.append((note, creation_date))
            elif time_difference == datetime.timedelta(days=1):
                repetitions.append((note, creation_date))
            elif time_difference == datetime.timedelta(weeks=1):
                repetitions.append((note, creation_date))
            elif time_difference == datetime.timedelta(weeks=2):
                repetitions.append((note, creation_date))
            elif time_difference <= datetime.timedelta(weeks=4):
                repetitions.append((note, creation_date))

        return repetitions
