from typing import List
from dataclasses import dataclass
from datetime import datetime,time

from geofence import point_is_inside_geofence
from web_requests_utils import send_get_request_with_bearer_auth


class CommuteChallenge:
    place_coordinates: tuple
    tolerance_radius: int

    def __init__(self,place_coordinates,tolerance_radius,proxies=None):
        self.place_coordinates = place_coordinates
        self.tolerance_radius = tolerance_radius
        self.proxies=proxies

    @staticmethod
    def is_date_time_between_time_range(date_to_check:str, after_time:str, before_time:str) -> bool:
        """
        Validate if given date is between given hours.

        :param date_to_check: The date and time to check, in ISO 8601 format (e.g., "2023-03-15T14:30:00Z")
        :param after_time: The lower bound time in "HH:MM" format (e.g., "09:00")
        :param before_time: The upper bound time in "HH:MM" format (e.g., "17:00")
        :return: True if the time of date_to_check is between after_time and before_time
        """
        date_time = datetime.strptime(date_to_check, "%Y-%m-%dT%H:%M:%SZ").time()
        after_time = datetime.strptime(after_time, "%H:%M").time()
        before_time = datetime.strptime(before_time, "%H:%M").time()
        print(date_time,after_time,before_time)
        return after_time < date_time < before_time
    
    @staticmethod
    def is_weekday(given_date:str) -> bool:
        """
        Validate if given date is a weekday.
        In datetime.weekday function, days are having their substitute in numbers.
        Monday is 0, Sunday is 6.
        """
        start_date = datetime.strptime(given_date, "%Y-%m-%dT%H:%M:%SZ")
        return start_date.weekday() < 5

    @staticmethod
    def get_activities_url(**kwargs) -> str:
        """
        Compose url based on given parameters
        :param kwargs:  for activities API URL
        :return: Strava API activities link
        """
        activities_url = f"https://www.strava.com/api/v3/athlete/activities"
        if kwargs:
            # Append query sign
            activities_url += '?'
        for key, value in kwargs.items():
            activities_url += f"&{key}={value}"
        return activities_url

    def fetch_strava_activities(self, strava_access_token: str, **kwargs) -> dict:
        """
        Fetch data from strava API /athlete/activities endpoint.
        :param strava_access_token: Generated oAuth access token
        :param kwargs: Parameters for activities API URL
        :return:
        """
        url = self.get_activities_url(per_page=200, **kwargs)
        return send_get_request_with_bearer_auth(url, strava_access_token,self.proxies)

    def get_valid_workplace_commute_activities(self, list_of_activities: dict) -> List[dict]:
        """
        Pick only activities which start or ends at the workplace (with tolerance based on tolerance_radius in meters)
        and check if 'start_date' was before 13:00 if activity started in geofence or after 13:00 if activity finished in geofence.
        :param list_of_activities: List of strava activities based on strava api schema
        :return: List of filtered out activities (matching criteria)
        """
        commute_activities = []
        
        bike_activities_sport_type = ["Ride", "EBikeRide", "EMountainBikeRide", "GravelRide", "MountainBikeRide"]
        for activity in list_of_activities:

            start_point_coordinates = activity['start_latlng']
            end_point_coordinates = activity['end_latlng']
            activity_date =activity['start_date_local']

            is_start_point_in_geofence=point_is_inside_geofence(start_point_coordinates, self.place_coordinates,self.tolerance_radius)
            is_end_point_in_geofence=point_is_inside_geofence(end_point_coordinates, self.place_coordinates,self.tolerance_radius)
            if activity['sport_type'] in bike_activities_sport_type and self.is_weekday(activity_date):
                print("im in first if")
                # Morning ride
                if is_end_point_in_geofence and self.is_date_time_between_time_range(activity_date,"00:01","11:59"):
                    commute_activities.append(activity)
                # Evening ride
                if is_start_point_in_geofence and self.is_date_time_between_time_range(activity_date,"12:01","23:59"):
                    commute_activities.append(activity)

        return commute_activities

@dataclass
class CommuteStatistics:
    activities: List
    target_distance: int = 250
    total_kilometers: float = 0
    kilometers_to_ride: float = 0
    rides_done: int = 0
    time_spent: float = 0
    
    def __post_init__(self):
        if self.activities:
            self.total_kilometers=self.sum_up_activities_distance()
            self.kilometers_to_ride = max(0, self.target_distance - self.total_kilometers)
            self.rides_done = len(self.activities)
            self.time_spent = self.sum_up_activities_time_in_hours()
    
    def sum_up_activities_distance(self) -> float:
        """
        Sum up all 'distance' fields value in list of activities.
        :return: Return sum of distance in kilometers
        """
        total_distance_meters = sum(single_activity['distance'] for single_activity in self.activities)
        return round(total_distance_meters / 1000, 1)
    
    def sum_up_activities_time_in_hours(self) -> float:
        """
        Sum up all 'elapsed_time' fields value in list of activities.
        :return: Return sum of moving in hours
        """
        def convert_seconds_to_hours(seconds:int) -> float:
            return round(seconds / 3600,2)
        
        total_activities_time_in_minutes = sum(single_activity['elapsed_time'] for single_activity in self.activities)
        return convert_seconds_to_hours(total_activities_time_in_minutes)