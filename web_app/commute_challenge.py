from typing import List
from dataclasses import dataclass

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
        :param list_of_activities: List of strava activities based on strava api schema
        :return: List of filtered out activities (matching criteria)
        """
        commute_activities = []
        bike_activities_sport_type = ["Ride", "EBikeRide", "EMountainBikeRide", "GravelRide", "MountainBikeRide"]
        for activity in list_of_activities:

            start_point_coordinates = activity['start_latlng']
            end_point_coordinates = activity['end_latlng']

            if any([point_is_inside_geofence(start_point_coordinates, self.place_coordinates,
                                             self.tolerance_radius),
                    point_is_inside_geofence(end_point_coordinates, self.place_coordinates,
                                             self.tolerance_radius)]) and activity['sport_type'] in bike_activities_sport_type:
                commute_activities.append(activity)

        return commute_activities

@dataclass
class CommuteStatistics:
    activities: List
    target_distance: int = 250
    total_kilometers: float = 0
    kilometers_to_ride: float = 0
    rides_done: int = 0
    time_spent: str = '0 hours'
    
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