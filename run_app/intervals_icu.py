import os
from datetime import datetime
from requests import get
from requests.auth import HTTPBasicAuth
from run_app.models import Run
from django.db.models import Min
from statistics import mean

class Intervals_icu(object):
    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date if start_date else Run.objects.aggregate(Min('date'))['date__min'].strftime('%Y-%m-%d')
        self.end_date = end_date if end_date else datetime.today().strftime('%Y-%m-%d')
        self.api_key = os.getenv("INTERNAL_ICU_API_KEY")
        self.url = "https://intervals.icu/api/v1/athlete/0/activities"
        try:
            self.activities = self.get_activities()
        except Exception as e:
            print("Error fetching activities from Intervals.icu:", e)
            raise f"Error fetching activities from Intervals.icu: {e}"
        
    def get_activities(self):
        response = get(
            self.url,
            auth=HTTPBasicAuth("API_KEY", self.api_key),
            params={
                "oldest": self.start_date,
                "newest": self.end_date,
            },
        )

        response.raise_for_status()
        return response.json()

    def run_dates(self):
        return set(item.get('start_date_local', '').split('T')[0] for item in self.activities if item.get('type') == "Run")

    def daily_activity(self, activity_date):
        data = [x for x in self.activities if x.get("start_date_local", "").split("T")[0] == activity_date]

        if not data:
            raise ValueError(f"Activity for date {activity_date} not found.")
        activity_dict = {'distance_km': 0, 'calories': 0, 'run_date': None, 'avg_heart_rate': 0, 'max_heart_rate': 0, 'time': 0}
        average_heartrate = mean([d.get("average_heartrate") for d in data if d.get("average_heartrate") is not None])

        for d in data:
            activity_dict['run_date'] = d.get("start_date_local", "").split("T")[0]
            activity_dict['distance_km'] += round(d.get("distance", 0) / 1000, 2)
            activity_dict['calories'] += d.get("calories", 0)
            activity_dict['avg_heart_rate'] = average_heartrate 
            if activity_dict['max_heart_rate'] < d.get("max_heartrate"):
                activity_dict['max_heart_rate'] = d.get("max_heartrate")
            activity_dict['time'] += d.get("moving_time", 0)

        return activity_dict
