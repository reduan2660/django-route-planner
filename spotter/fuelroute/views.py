from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dotenv import load_dotenv
import requests, logging, os


load_dotenv()

# Create a logger for this module
logger = logging.getLogger('fuelroute')

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Proxy view to fetch the Google Maps API
def proxy_google_maps(request):
    endpoint = "https://maps.googleapis.com/maps/api/js"
    params = {
        "key": GOOGLE_MAPS_API_KEY,
        "libraries": "places",
        "callback": request.GET.get("callback")
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise exception for any bad status codes
        return HttpResponse(response.content, content_type="application/javascript")
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

from .utils import (
    get_coordinates,
    get_cached_route,
    cache_route,
    calculate_fuel_intake_and_cost,
    find_route
)


def index(request):
    logger.info("Index page requested")
    return render(request, "index.html")


@api_view(["GET"])
def get_optimal_route(request):
    """
    GET request with query parameters source and destination
    Returns the optimal route and total fuel intake cost
    """
    try:
        # Log request parameters
        logger.info("Optimal route request received")

        # Extract and validate coordinates
        source, destination = get_coordinates(request)
        logger.info(f"Source: {source}, Destination: {destination}")

        # Check cache first
        # cache_key = f"route_{source}_{destination}"
        cached_response = get_cached_route(source, destination)
        if cached_response:
            logger.info("Returning cached route data")
            return Response(cached_response)

        # Find the optimal route
        route = find_route(source, destination)
        logger.info(f"Calculated route: {route}")

        # Calculate fuel intake and cost
        total_fuel_intake, total_fuel_cost = calculate_fuel_intake_and_cost(route)
        logger.info(f"Total fuel intake: {total_fuel_intake}, Total fuel cost: {total_fuel_cost}")

        # Prepare response
        response_data = {
            "route": route,
            "total_fuel_cost": round(total_fuel_cost, 2),
            "total_fuel_intake": round(total_fuel_intake, 2),
        }

        # Store in cache
        cache_route(source, destination, response_data)
        logger.info("Route data cached successfully")

        return Response(response_data)
        
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        return JsonResponse(
            {"error": "Invalid coordinates provided."},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Exception: {str(e)}", exc_info=True)
        return JsonResponse(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )