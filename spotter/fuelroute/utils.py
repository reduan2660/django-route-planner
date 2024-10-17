import logging
from geopy.distance import geodesic
from django.core.cache import cache
from .models import FuelStop  # Import the FuelStop model

# Create logger instance
logger = logging.getLogger('fuelroute')

def round_coordinates(coordinate, precision=3):
    return round(coordinate, precision)

def get_coordinates(request):
    """Extract and convert source and destination to float tuples from request."""
    source = request.query_params.get("source")
    destination = request.query_params.get("destination")

    if not source or not destination:
        logger.error("Missing source or destination in request")
        raise ValueError("Source and destination are required.")

    source = tuple(map(float, source.split(",")))
    destination = tuple(map(float, destination.split(",")))

    logger.info(f"Coordinates parsed successfully: Source {source}, Destination {destination}")
    return source, destination

def cache_key_from_coordinates(source, destination, precision=3):
    """Generate a cache key based on source and destination coordinates rounded to precision."""
    source_rounded = (round_coordinates(source[0], precision), round_coordinates(source[1], precision))
    destination_rounded = (round_coordinates(destination[0], precision), round_coordinates(destination[1], precision))
    return f"route_{source_rounded}_{destination_rounded}"

def get_cached_route(source, destination, precision=3):
    """Retrieve the cached route if available for a rounded coordinate pair."""
    # Generate the cache key using both source and destination
    cache_key = cache_key_from_coordinates(source, destination, precision)
    
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache hit for key: {cache_key}")
    else:
        logger.info(f"Cache miss for key: {cache_key}")
    
    return cached_data


def cache_route(source, destination, data, precision=3):
    """Cache the route data for future use for a rounded coordinate pair."""
    cache_key = cache_key_from_coordinates(source, destination, precision)
    cache.set(cache_key, data, timeout=60*60)  # Cache for 1 hour
    logger.info(f"Data cached under key: {cache_key}")


def find_next_stop(current_location, destination, vehicle_range=500):
    """
    Finds the next optimal fuel stop based on:
    1. Within vehicle range
    2. Closer to destination than current location
    3. Cheapest fuel price
    """
    logger.info(f"Finding next stop from {current_location} to {destination}")

    # Query all fuel stops from the database
    fuel_stops = FuelStop.objects.all()

    valid_stops = []

    for stop in fuel_stops:
        stop_location = (stop.latitude, stop.longitude)
        distance_to_stop = geodesic(current_location, stop_location).miles
        distance_to_destination = geodesic(stop_location, destination).miles
        distance_current_to_destination = geodesic(current_location, destination).miles

        # Check if the stop is within vehicle range and closer to the destination
        if distance_to_stop <= vehicle_range and distance_to_destination < distance_current_to_destination:
            valid_stops.append({
                "location": stop_location,
                "price": stop.retail_price,
                "distance_to_stop": distance_to_stop
            })

    if not valid_stops:
        logger.error(f"No valid fuel stops found within range from {current_location}")
        raise ValueError("No valid fuel stops within range that lead closer to the destination.")
    
    # Find the stop with the lowest fuel price
    next_stop = min(valid_stops, key=lambda x: x["price"])
    logger.info(f"Next stop found at {next_stop['location'][0]}, {next_stop['location'][1]}")

    return next_stop["location"]

def find_route(source, destination, vehicle_range=500, precision=3):
    """Find the optimal route based on vehicle range and fuel stops, with caching."""
    # Try to fetch from cache
    cached_route = get_cached_route(source, destination, precision)
    if cached_route:
        return cached_route

    logger.info(f"Calculating route from {source} to {destination}")

    current_location = source
    route = [current_location]

    while True:
        distance_to_destination = geodesic(current_location, destination).miles
        if distance_to_destination <= vehicle_range:
            route.append(destination)
            logger.info(f"Destination reached: {destination}")
            break
        else:
            try:
                next_stop = find_next_stop(current_location, destination, vehicle_range=vehicle_range)
                route.append(next_stop)
                logger.info(f"Next stop added to route: {next_stop}")
                current_location = next_stop
            except ValueError as e:
                logger.error(f"Error finding next stop: {e}")
                break

    # Cache the route before returning
    cache_route(source, destination, route, precision)
    
    return route


def calculate_fuel_intake_and_cost(route):
    """Calculate fuel intake and cost based on the route."""
    logger.info("Calculating fuel intake and cost for route")
    
    fuel_intake = []
    cost = []
    
    for i in range(len(route) - 1):
        distance = geodesic(route[i], route[i + 1]).miles
        intake = distance / 10  # Assuming 10 miles per unit of fuel
        current_stop = FuelStop.objects.filter(latitude=route[i][0], longitude=route[i][1]).first()  # Fetch the stop from the DB
        
        if current_stop:
            fuel_intake.append(intake)
            cost.append(intake * float(current_stop.retail_price))  # Convert decimal to float

    total_fuel_intake = sum(fuel_intake)
    total_fuel_cost = sum(cost)

    logger.info(f"Fuel intake: {total_fuel_intake}, Fuel cost: {total_fuel_cost}")
    
    return total_fuel_intake, total_fuel_cost