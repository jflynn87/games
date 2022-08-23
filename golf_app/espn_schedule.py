from datetime import datetime, timedelta

from requests import get
import json

from golf_app import utils
from golf_app.models import Tournament, ScoreDict, Group, Field


class ESPNSchedule(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data,
        all_data is a list of dicts
        event_data is the data for the event but most is in competition
        competition_data varoius datat about  the tournament
        field_data is the actual golfers in the tournament'''

    def __init__(self):
        start = datetime.now()

        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        url = 'https://www.espn.com/golf/schedule/_/season/2022/tour/pga?_xhr=pageContent'
        self.schedule = get(url, headers=headers).json()

        self.events_to_exclude = ['The Match', 'Corales Puntacana Championship', 'Puerto Rico Open', 'Barracuda Championship', 'Barbasol Championship']

    def get_event_list(self):
        d = {}
        for event in self.schedule.get('events'):
            if event.get('name') not in self.events_to_exclude: 
                d[event.get('name')] = {
                                'start_date': datetime.strptime(event.get('startDate')[:-1], '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d'),
                                'status': event.get('status'),
                                'link': event.get('link')
                                }

        return d

    def current_event(self):
        if [v for v in self.schedule.get('events') if v.get('status')  == 'in']:
            return [v for v in self.schedule.get('events') if v.get('status') == 'in']

        end_date = datetime.now() + timedelta(days=5)
        start_date = datetime.utcnow()
        
        event = [v for v in self.schedule.get('events') if datetime.strptime(v.get('startDate')[:-1], '%Y-%m-%dT%H:%M') >= start_date \
                    and  datetime.strptime(v.get('startDate')[:-1], '%Y-%m-%dT%H:%M') < end_date]
        return event

    def complete_events(self):
        print ({k for k,v in self.get_event_list().items() if v.get('status') == 'post'})
        return len([v for k,v in self.get_event_list().items() if v.get('status') == 'post'])

    def remaining_events(self):
        print ({k for k,v in self.get_event_list().items() if v.get('status') == 'pre'})
        return len([v for k,v in self.get_event_list().items() if v.get('status') == 'pre']) # removed plus 1 on 8/10/22 +1  #+1 for in progress current tornament