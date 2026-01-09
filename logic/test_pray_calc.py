from datetime import datetime, timezone
from pray_calc import calc_shacharit, calc_mincha, calc_arvit


sunrise = datetime(2026, 1, 3, 6, 47, tzinfo=timezone.utc)
sunset = datetime(2026, 1, 3, 17, 00, tzinfo=timezone.utc)

print("sunrise:", sunrise.strftime("%H:%M"))
print("sunset :", sunset.strftime("%H:%M"))

print("shacharit:", calc_shacharit(sunrise).strftime("%H:%M"))
print("mincha   :", calc_mincha(sunset).strftime("%H:%M"))
print("arvit    :", calc_arvit(sunrise, sunset).strftime("%H:%M"))
