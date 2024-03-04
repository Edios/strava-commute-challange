from typing import List

from geofence import point_is_inside_geofence
from web_requests_utils import send_get_request_with_bearer_auth


class CommuteChallenge:
    place_coordinates: tuple
    tolerance_radius: int

    def __init__(self,place_coordinates,tolerance_radius):
        self.place_coordinates = place_coordinates
        self.tolerance_radius = tolerance_radius

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
        # TODO: Change for timestamps for activity when it will be launched
        # start_date = datetime(2024, 3, 1).timestamp()
        # finish_date = datetime(2024, 6, 30).timestamp()
        # TODO: Remove debug dates
        # start_date = datetime(2024, 3, 1).timestamp()
        # finish_date = datetime(2024, 6, 1).timestamp()

        url = self.get_activities_url(per_page=200, **kwargs)
        return send_get_request_with_bearer_auth(url, strava_access_token)

    def get_valid_workplace_commute_activities(self, list_of_activities: dict) -> List[dict]:
        """
        Pick only activities which start or ends at the workplace (with tolerance based on tolerance_radius in meters)
        :param list_of_activities: List of strava activities based on strava api schema
        :return: List of filtered out activities (matching criteria)
        """
        commute_activities = []

        for activity in list_of_activities:

            start_point_coordinates = activity['start_latlng']
            end_point_coordinates = activity['end_latlng']

            if any([point_is_inside_geofence(start_point_coordinates, self.place_coordinates,
                                             self.tolerance_radius),
                    point_is_inside_geofence(end_point_coordinates, self.place_coordinates,
                                             self.tolerance_radius)]):
                commute_activities.append(activity)

        return commute_activities

    @staticmethod
    def sum_up_activities_distance(list_of_activities: List[dict]) -> float:
        """
        Sum up all 'distance' fields value in list of activities.
        :param list_of_activities: List of strava activities based on strava api schema
        :return: Return sum of distance in kilometers
        """
        total_distance_meters = sum(single_activity['distance'] for single_activity in list_of_activities)
        return round(total_distance_meters / 1000, 1)