from math import radians, sin, cos, sqrt, atan2


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the Earth's surface specified by latitude and longitude in degrees.
    """
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)

    # Calculate the differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return distance


def point_is_inside_geofence(point, geofence_center, tolerance_radius) -> bool:
    """
    Check if a given point is inside a geofence defined by a center
    and a tolerance radius in meters.
    """
    # Unpack coordinates
    lat1, lon1 = point
    lat2, lon2 = geofence_center

    # Calculate distance using Haversine formula
    distance = haversine(lat1, lon1, lat2, lon2) * 1000  # Convert to meters

    # Check if the distance is within the tolerance radius
    return distance <= tolerance_radius
