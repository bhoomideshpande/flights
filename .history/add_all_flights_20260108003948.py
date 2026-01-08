import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capstone.settings")
django.setup()

from flight.models import Week
Week.objects.all().delete()

from flight.utils import (
    createWeekDays,
    addPlaces,
    cleanDuplicatePlaces,
    cleanDuplicateWeeks,
    addDomesticFlights,
    addInternationalFlights
)

cleanDuplicateWeeks()
createWeekDays()
addPlaces()
cleanDuplicatePlaces()
addDomesticFlights()
addInternationalFlights()