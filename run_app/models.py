from django.db import models

# Create your models here.
class Shoes(models.Model):
    name = models.CharField(max_length=30, unique=True)
    active = models.BooleanField()
    main_shoe = models.BooleanField(default=False)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("run_app:list")


    def save(self, *args, **kwargs):
        if self.main_shoe:
            try:
                temp = Shoes.objects.get(main_shoe=True)
                if self != temp:
                    temp.main_shoe = False
                    temp.save()
            except Shoes.DoesNotExist:
                pass
        super(Shoes, self).save(*args, **kwargs)


class Run(models.Model):
    LOCATION_CHOICES = (
    ('1','town'),
    ('2','palace'),
    ('3','tamagawa'),
    ('4','tm')
    )

    date = models.DateField()
    dist = models.FloatField()
    time = models.DurationField()
    cals = models.PositiveIntegerField()
    shoes = models.ForeignKey(Shoes, on_delete=models.CASCADE,related_name='run')
    location = models.CharField(choices=LOCATION_CHOICES, max_length=30)

    def __str__(self):
        return str(self.date) + ' - ' + str(self.location)

    def get_absolute_url(self):
        return reverse("run_app:list")

    def shoe_dist(self):
        dist = Run.objects.values('shoes').annotate(total_dist=Sum('dist'))
        print ('dist', dist)
        return dist
