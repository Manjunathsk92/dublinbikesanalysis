#from . import weather_getter
from dbanalysis.classes.weather_getter import weather_getter
weather=weather_getter()
df=weather.get_weather()
print(df)
