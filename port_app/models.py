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

    def __str__(self):
        return self.name


class CCY(models.Model):
    code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.code

class Position(models.Model):
    CHOICES = ((1, 'Public'), (2, 'Private'))
    CCY_CHOICES = ((1, 'USD'), (2, 'JPY'))
    #symbol = models.ForeignKey(MarketData, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=CHOICES)
    qty = models.IntegerField()
    price = models.FloatField()
    ccy = models.CharField(max_length=3, choices=CCY_CHOICES)
    #status = models.CharField(max_length=100)
    open_date = models.DateField()
    close_date = models.DateField(null=True)
    notes = models.CharField(max_length=300)

    def __str__(self):
        return self.symbol
