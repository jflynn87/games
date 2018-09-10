from django.db import models

# Create your models here.
class Shoes(models.Model):
    name = models.CharField(max_length=30, unique=True)
    active = models.BooleanField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("run_app:list")


class Run(models.Model):
    date = models.DateField()
    dist = models.FloatField()
    time = models.DurationField()
    cals = models.PositiveIntegerField()
    shoes = models.ForeignKey(Shoes, on_delete=models.CASCADE,related_name='run')
    location = models.CharField(max_length=30)

    def __str__(self):
        return str(self.date) + ' - ' + str(self.location)

    def get_absolute_url(self):
        return reverse("run_app:list")
    
