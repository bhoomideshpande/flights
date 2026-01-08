import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capstone.settings")
django.setup()

from flight.utils import (
    createWeekDays,
    addPlaces,
    cleanDuplicatePlaces,
    addDomesticFlights,
    addInternationalFlights
)

createWeekDays()
addPlaces()
cleanDuplicatePlaces()
addDomesticFlights()
addInternationalFlights()
