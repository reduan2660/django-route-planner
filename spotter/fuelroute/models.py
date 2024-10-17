from django.db import models

class FuelStop(models.Model):
    opis_truckstop_id = models.CharField(max_length=100, unique=False)
    truckstop_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=False)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    rack_id = models.CharField(max_length=50, blank=True, null=True)
    retail_price = models.DecimalField(max_digits=5, decimal_places=2)  # Precision for fuel prices
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.truckstop_name} - {self.city}, {self.state} ({self.opis_truckstop_id})"