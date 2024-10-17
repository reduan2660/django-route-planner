from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase

class RouteTestCase(TestCase):
    def setUp(self):
        # Set up the test client
        self.client = APIClient()
        # Example source and destination coordinates
        self.source = "32.715736,-117.161087"
        self.destination = "34.052235,-95.08503"

    def test_optimal_route(self):
        # Perform a GET request to the API
        response = self.client.get(
            reverse('get_optimal_route'), 
            {'source': self.source, 'destination': self.destination}
        )

        # Assert that the status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response contains the correct data
        self.assertIn("route", response.data)
        self.assertIn("total_fuel_cost", response.data)
        self.assertIn("total_fuel_intake", response.data)

        # Convert route elements to lists for comparison
        response_route = [list(point) for point in response.data["route"]]

        expected_route = [
            [32.715736, -117.161087],
            [33.4615878, -112.1474423],
            [31.7429919, -106.2676594],
            [32.4330582, -100.5422351],
            [34.052235, -95.08503]
        ]

        # Assert that the routes match
        self.assertEqual(response_route, expected_route)

        # Assert fuel cost and intake
        self.assertAlmostEqual(response.data["total_fuel_cost"], 470.95, places=2)
        self.assertAlmostEqual(response.data["total_fuel_intake"], 133.23, places=2)