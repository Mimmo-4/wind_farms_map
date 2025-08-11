import utm


def get_coordinates_from_utm(utm_easting, utm_northing, utm_zone_number=32, utm_zone_letter="N"):

    # Convert UTM to latitude and longitude
    lat, lon = utm.to_latlon(utm_easting, utm_northing, utm_zone_number, utm_zone_letter)

    return lat, lon


def get_utm_from_coordinates(lat, lon):
    """
    Convert latitude and longitude to UTM northing and easting.

    Parameters:
    - lat: Latitude in decimal degrees.
    - lon: Longitude in decimal degrees.

    Returns:
    - utm_easting: Easting coordinate in UTM.
    - utm_northing: Northing coordinate in UTM.
    """
    # Convert latitude and longitude to UTM
    utm_easting, utm_northing, utm_zone_number, utm_zone_letter = utm.from_latlon(lat, lon)

    return utm_easting, utm_northing