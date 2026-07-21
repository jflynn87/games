import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
import django
django.setup()

from golf_app.models import Tournament
from golf_app import field_csv

t = Tournament.objects.get(current=True)
f = field_csv.FieldCSV(t)
f_csv = f.create_file()
print (f_csv)
exit()
