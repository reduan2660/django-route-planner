# management/commands/load_fuel_stops.py

import csv
from django.core.management.base import BaseCommand
from fuelroute.models import FuelStop  # Import your updated model

class Command(BaseCommand):
    help = 'Load fuel stops data from a CSV file into the database'

    def handle(self, *args, **kwargs):
        with open('fuel_stops.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                FuelStop.objects.create(
                    opis_truckstop_id=row['OPIS Truckstop ID'],
                    truckstop_name=row['Truckstop Name'],
                    address=row['Address'],
                    city=row['City'],
                    state=row['State'],
                    rack_id=row['Rack ID'],
                    retail_price=row['Retail Price'],
                    latitude=row['Latitude'],
                    longitude=row['Longitude']
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded fuel stops'))