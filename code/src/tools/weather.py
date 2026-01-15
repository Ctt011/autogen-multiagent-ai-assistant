"""Weather tools for the Multi-Agent AI Assistant."""

import httpx
import pytz
from datetime import datetime
from typing import Dict, Any, Tuple
from autogen_core.tools import FunctionTool

from ..config import config
from ..logger import logger


class WeatherTools:
    """Weather information tools using Open-Meteo API."""

    WEATHER_CODE_DESC: Dict[int, str] = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Light rain showers", 81: "Moderate rain showers", 82: "Heavy rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail",
    }

    def __init__(self):
        self.open_meteo_url = config.OPEN_METEO_URL
        self.nominatim_url = config.NOMINATIM_URL
        self.default_timezone = config.DEFAULT_TIMEZONE

    async def _geocode(self, city: str) -> Tuple[float, float]:
        """Get coordinates for a city using Nominatim."""
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "ai-assistant/1.0"},
                timeout=10,
            ) as client:
                response = await client.get(
                    self.nominatim_url,
                    params={"q": city, "format": "json", "limit": 1},
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    raise ValueError(f"Could not find location: {city}")

                lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
                logger.debug(f"Geocoded {city} to ({lat}, {lon})")
                return lat, lon

        except Exception as e:
            logger.error(f"Geocoding error for {city}: {e}")
            raise

    async def _get_weather_data(self, location: str) -> Dict[str, Any]:
        """Fetch weather data from Open-Meteo API."""
        try:
            # Parse coordinates or geocode city
            if "," in location:
                lat, lon = map(float, location.split(",", maxsplit=1))
                location_name = f"{lat:.2f},{lon:.2f}"
            else:
                lat, lon = await self._geocode(location)
                location_name = location

            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "hourly": "temperature_2m,weathercode,precipitation_probability",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                "forecast_days": 3,
                "timezone": "auto",
            }

            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(self.open_meteo_url, params=params)
                response.raise_for_status()
                data = response.json()

            logger.info(f"Retrieved weather data for {location_name}")
            return {
                "location": location_name,
                "current": data.get("current_weather", {}),
                "hourly": data.get("hourly", {}),
                "daily": data.get("daily", {}),
            }

        except Exception as e:
            logger.error(f"Weather API error: {e}")
            raise RuntimeError(f"Weather API error: {e}")

    async def get_current_weather(self, location: str) -> str:
        """
        Get current weather for a location.

        Args:
            location: City name or "lat,lon" coordinates

        Returns:
            Formatted current weather information
        """
        try:
            data = await self._get_weather_data(location)
            current = data["current"]

            temp = current.get("temperature", "N/A")
            code = current.get("weathercode", 0)
            desc = self.WEATHER_CODE_DESC.get(code, "Unknown")
            wind = current.get("windspeed", "N/A")

            result = f"Current weather in {data['location']}:\n"
            result += f"• Temperature: {temp}°C\n"
            result += f"• Conditions: {desc}\n"
            result += f"• Wind: {wind} km/h"

            logger.info(f"Formatted current weather for {location}")
            return result

        except Exception as e:
            error_msg = f"Error getting current weather: {e}"
            logger.error(error_msg)
            return error_msg

    async def get_forecast(self, location: str, days: int = 3) -> str:
        """
        Get weather forecast for a location.

        Args:
            location: City name or coordinates
            days: Number of days (1-3)

        Returns:
            Formatted weather forecast
        """
        try:
            data = await self._get_weather_data(location)
            daily = data["daily"]

            result = f"{days}-day forecast for {data['location']}:\n"

            for i in range(min(days, len(daily["time"]))):
                date = daily["time"][i]
                temp_max = daily["temperature_2m_max"][i]
                temp_min = daily["temperature_2m_min"][i]
                precip = daily["precipitation_sum"][i]
                code = daily["weathercode"][i]
                desc = self.WEATHER_CODE_DESC.get(code, "Unknown")

                result += f"\n{date}:\n"
                result += f"  • Temp: {temp_min:.0f}°C to {temp_max:.0f}°C\n"
                result += f"  • Conditions: {desc}\n"
                result += f"  • Precipitation: {precip:.1f}mm"

            logger.info(f"Formatted forecast for {location}")
            return result

        except Exception as e:
            error_msg = f"Error getting forecast: {e}"
            logger.error(error_msg)
            return error_msg

    async def as_function_tools(self):
        """Convert weather methods to AutoGen function tools."""
        return [
            FunctionTool(self.get_current_weather, description="Get current weather for a city"),
            FunctionTool(self.get_forecast, description="Get weather forecast for a city"),
        ]
