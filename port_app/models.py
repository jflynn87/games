from django.db import models

# Create your models here.


class MarketData(models.Model):
    symbol = models.CharField(max_length=200)
    ccy = models.CharField(max_length = 10)
    date_time = models.DateTimeField()
    type = models.CharField(max_length = 100) #intended for open, close, intra day, etc
    price = models.FloatField()


class Portfolio(models.Model):
    name = models.CharField(max_length=200, unique=True)
    symbol = models.ForeignKey(MarketData, on_delete=models.CASCADE)
    total_pos = models.IntegerField()

class Position(models.Model):
    symbol = models.ForeignKey(MarketData, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.FloatField()
    ccy = models.CharField(max_length=3)
    status = models.CharField(max_length=100)
    open_date = models.DateField()
    close_dat = models.DateField(null=True)
    notes = models.CharField(max_length=300)
