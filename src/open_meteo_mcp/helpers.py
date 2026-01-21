"""Helper functions for weather interpretation and formatting."""

from typing import Dict, Any
from datetime import datetime, timedelta
import pytz  # type: ignore[import-untyped]


def interpret_weather_code(code: int) -> Dict[str, Any]:
    """
    Interpret WMO weather codes into human-readable descriptions.

    Args:
        code: WMO weather code (0-99)

    Returns:
        Dictionary with description, category, and severity
    """
    weather_codes = {
        0: {"description": "Clear sky", "category": "Clear", "severity": "none"},
        1: {"description": "Mainly clear", "category": "Clear", "severity": "none"},
        2: {"description": "Partly cloudy", "category": "Cloudy", "severity": "low"},
        3: {"description": "Overcast", "category": "Cloudy", "severity": "low"},
        45: {"description": "Fog", "category": "Fog", "severity": "medium"},
        48: {
            "description": "Depositing rime fog",
            "category": "Fog",
            "severity": "medium",
        },
        51: {"description": "Light drizzle", "category": "Drizzle", "severity": "low"},
        53: {
            "description": "Moderate drizzle",
            "category": "Drizzle",
            "severity": "low",
        },
        55: {
            "description": "Dense drizzle",
            "category": "Drizzle",
            "severity": "medium",
        },
        61: {"description": "Slight rain", "category": "Rain", "severity": "low"},
        63: {"description": "Moderate rain", "category": "Rain", "severity": "medium"},
        65: {"description": "Heavy rain", "category": "Rain", "severity": "high"},
        71: {"description": "Slight snow", "category": "Snow", "severity": "low"},
        73: {"description": "Moderate snow", "category": "Snow", "severity": "medium"},
        75: {"description": "Heavy snow", "category": "Snow", "severity": "high"},
        77: {"description": "Snow grains", "category": "Snow", "severity": "medium"},
        80: {
            "description": "Slight rain showers",
            "category": "Rain",
            "severity": "low",
        },
        81: {
            "description": "Moderate rain showers",
            "category": "Rain",
            "severity": "medium",
        },
        82: {
            "description": "Violent rain showers",
            "category": "Rain",
            "severity": "high",
        },
        85: {
            "description": "Slight snow showers",
            "category": "Snow",
            "severity": "low",
        },
        86: {
            "description": "Heavy snow showers",
            "category": "Snow",
            "severity": "high",
        },
        95: {
            "description": "Thunderstorm",
            "category": "Thunderstorm",
            "severity": "high",
        },
        96: {
            "description": "Thunderstorm with slight hail",
            "category": "Thunderstorm",
            "severity": "high",
        },
        99: {
            "description": "Thunderstorm with heavy hail",
            "category": "Thunderstorm",
            "severity": "extreme",
        },
    }

    return weather_codes.get(
        code,
        {
            "description": f"Unknown weather code: {code}",
            "category": "Unknown",
            "severity": "unknown",
        },
    )


def get_weather_category(code: int) -> str:
    """
    Get the weather category for a WMO code.

    Args:
        code: WMO weather code

    Returns:
        Weather category (Clear, Cloudy, Rain, Snow, etc.)
    """
    result = interpret_weather_code(code)["category"]
    assert isinstance(result, str)
    return result


def get_travel_impact(code: int) -> str:
    """
    Assess travel impact based on weather code.

    Args:
        code: WMO weather code

    Returns:
        Travel impact level (none, minor, moderate, significant, severe)
    """
    severity = interpret_weather_code(code)["severity"]

    impact_map = {
        "none": "none",
        "low": "minor",
        "medium": "moderate",
        "high": "significant",
        "extreme": "severe",
    }

    return impact_map.get(severity, "unknown")


def assess_ski_conditions(
    snow_data: Dict[str, Any], weather_data: Dict[str, Any]
) -> str:
    """
    Assess ski conditions based on snow depth, snowfall, and weather.

    Args:
        snow_data: Snow conditions data (depth, snowfall, etc.)
        weather_data: Weather data (temperature, weather code, etc.)

    Returns:
        Ski condition assessment (Excellent, Good, Fair, Poor)
    """
    # Extract key metrics
    snow_depth = snow_data.get("snow_depth", 0)
    recent_snowfall = snow_data.get("recent_snowfall", 0)
    temperature = weather_data.get("temperature", 0)
    weather_code = weather_data.get("weather_code", 0)

    # Assess conditions
    if recent_snowfall > 10 and -15 <= temperature <= -5 and weather_code in [0, 1, 2]:
        return "Excellent"
    elif snow_depth > 0.5 and -10 <= temperature <= 0 and weather_code in [0, 1, 2, 3]:
        return "Good"
    elif snow_depth > 0.2 and temperature < 5:
        return "Fair"
    else:
        return "Poor"


def format_temperature(celsius: float) -> str:
    """
    Format temperature with unit.

    Args:
        celsius: Temperature in Celsius

    Returns:
        Formatted temperature string (e.g., "15.2°C")
    """
    return f"{celsius:.1f}°C"


def calculate_wind_chill(temp: float, wind: float) -> float:
    """
    Calculate wind chill temperature.

    Uses the North American wind chill formula.

    Args:
        temp: Air temperature in Celsius
        wind: Wind speed in km/h

    Returns:
        Wind chill temperature in Celsius
    """
    if wind < 4.8:  # Wind chill only applies above ~5 km/h
        return temp

    # Convert to Fahrenheit for calculation
    temp_f = temp * 9 / 5 + 32
    wind_mph = wind * 0.621371

    # Wind chill formula (Fahrenheit)
    wind_chill_f = (
        35.74
        + 0.6215 * temp_f
        - 35.75 * (wind_mph**0.16)
        + 0.4275 * temp_f * (wind_mph**0.16)
    )

    # Convert back to Celsius
    wind_chill_c = (wind_chill_f - 32) * 5 / 9

    result = round(wind_chill_c, 1)
    assert isinstance(result, float)
    return result


def get_seasonal_advice(month: int) -> str:
    """
    Get seasonal advice for outdoor activities.

    Args:
        month: Month number (1-12)

    Returns:
        Seasonal advice string
    """
    seasons = {
        (
            12,
            1,
            2,
        ): "Winter: Ideal for skiing and snow sports. Dress warmly and check avalanche warnings.",
        (
            3,
            4,
            5,
        ): "Spring: Variable conditions. Snow melting at lower elevations. Good for hiking as weather improves.",
        (
            6,
            7,
            8,
        ): "Summer: Best for hiking, climbing, and outdoor activities. Watch for afternoon thunderstorms in mountains.",
        (
            9,
            10,
            11,
        ): "Autumn: Beautiful colors, but weather becoming unpredictable. Early snow possible at high elevations.",
    }

    for months, advice in seasons.items():
        if month in months:
            return advice

    return "Check current conditions before outdoor activities."


def format_precipitation(mm: float) -> str:
    """
    Format precipitation amount with appropriate description.

    Args:
        mm: Precipitation in millimeters

    Returns:
        Formatted precipitation string with description
    """
    if mm == 0:
        return "No precipitation"
    elif mm < 1:
        return f"{mm:.1f}mm (light)"
    elif mm < 5:
        return f"{mm:.1f}mm (moderate)"
    elif mm < 10:
        return f"{mm:.1f}mm (heavy)"
    else:
        return f"{mm:.1f}mm (very heavy)"


def generate_weather_alerts(
    current: Dict[str, Any],
    hourly: Dict[str, Any],
    daily: Dict[str, Any],
    timezone: str,
) -> list[Dict[str, Any]]:
    """
    Generate weather alerts based on thresholds.

    Args:
        current: Current weather conditions
        hourly: Hourly forecast data
        daily: Daily forecast data
        timezone: Timezone for the location

    Returns:
        List of WeatherAlert dictionaries
    """
    from datetime import datetime

    alerts: list[Dict[str, Any]] = []

    if not current or not hourly or not daily:
        return alerts

    try:
        # Extract data safely
        current_temp = current.get("temperature", 20)

        # Get hourly and daily temperatures
        hourly_temps = hourly.get("temperature_2m", [])
        hourly_winds = hourly.get("wind_gusts_10m", [])
        hourly_uvs = hourly.get("uv_index", [])
        hourly_times = hourly.get("time", [])

        daily_codes = daily.get("weather_code", [])

        # HEAT ALERT (temp > 30°C for 3+ consecutive hours)
        if hourly_temps:
            heat_hours = sum(1 for t in hourly_temps[:24] if t > 30)
            if heat_hours >= 3:
                alerts.append(
                    {
                        "type": "heat",
                        "severity": "watch" if heat_hours < 6 else "warning",
                        "start": (
                            hourly_times[0]
                            if hourly_times
                            else datetime.now().isoformat()
                        ),
                        "end": (
                            hourly_times[min(24, heat_hours)]
                            if hourly_times
                            else (datetime.now() + timedelta(hours=6)).isoformat()
                        ),
                        "description": f"High temperature alert: {heat_hours} hours above 30°C expected",
                        "recommendations": [
                            "Limit outdoor activities during peak heat (11am-4pm)",
                            "Increase hydration significantly",
                            "Check on elderly and vulnerable populations",
                            "Seek air-conditioned spaces during hottest hours",
                        ],
                    }
                )

        # COLD ALERT (temp < -10°C)
        if current_temp < -10 or any(t < -10 for t in hourly_temps[:24]):
            alerts.append(
                {
                    "type": "cold",
                    "severity": "watch" if current_temp > -20 else "warning",
                    "start": (
                        hourly_times[0] if hourly_times else datetime.now().isoformat()
                    ),
                    "end": (
                        hourly_times[min(12, len(hourly_times) - 1)]
                        if hourly_times
                        else (datetime.now() + timedelta(hours=12)).isoformat()
                    ),
                    "description": "Extreme cold alert: temperatures below -10°C expected",
                    "recommendations": [
                        "Avoid prolonged outdoor exposure",
                        "Wear appropriate winter gear",
                        "Watch for signs of frostbite and hypothermia",
                        "Check heating systems are functioning",
                    ],
                }
            )

        # STORM ALERT (wind gusts > 80 km/h OR thunderstorm codes 95-99)
        high_wind_hours = (
            [i for i, w in enumerate(hourly_winds) if w and w > 80]
            if hourly_winds
            else []
        )
        thunderstorm_codes = [code for code in daily_codes if code in [95, 96, 99]]

        if high_wind_hours or thunderstorm_codes:
            alerts.append(
                {
                    "type": "storm",
                    "severity": (
                        "warning"
                        if high_wind_hours or thunderstorm_codes
                        else "advisory"
                    ),
                    "start": (
                        hourly_times[high_wind_hours[0]]
                        if high_wind_hours and hourly_times
                        else datetime.now().isoformat()
                    ),
                    "end": (
                        hourly_times[
                            min(high_wind_hours[-1] + 2, len(hourly_times) - 1)
                        ]
                        if high_wind_hours and hourly_times
                        else (datetime.now() + timedelta(hours=4)).isoformat()
                    ),
                    "description": "Storm warning: strong winds (>80 km/h) or thunderstorms expected",
                    "recommendations": [
                        "Avoid outdoor activities in exposed areas",
                        "Secure loose outdoor items",
                        "Monitor for flash flooding",
                        "Keep emergency contacts and supplies ready",
                    ],
                }
            )

        # UV ALERT (UV index > 8)
        high_uv_hours = (
            [i for i, uv in enumerate(hourly_uvs) if uv and uv > 8]
            if hourly_uvs
            else []
        )
        if high_uv_hours:
            alerts.append(
                {
                    "type": "uv",
                    "severity": "advisory",
                    "start": (
                        hourly_times[high_uv_hours[0]]
                        if hourly_times
                        else datetime.now().isoformat()
                    ),
                    "end": (
                        hourly_times[min(high_uv_hours[-1] + 1, len(hourly_times) - 1)]
                        if hourly_times
                        else (datetime.now() + timedelta(hours=3)).isoformat()
                    ),
                    "description": "Extreme UV alert: UV index above 8 expected",
                    "recommendations": [
                        "Apply high SPF sunscreen (SPF 50+) every 2 hours",
                        "Seek shade during peak UV hours (10am-4pm)",
                        "Wear UV-protective clothing, hat, and sunglasses",
                        "Avoid direct sun exposure for sensitive individuals",
                    ],
                }
            )

        # HIGH WIND ALERT (gusts > 50 km/h but < 80)
        moderate_wind_hours = (
            [i for i, w in enumerate(hourly_winds) if w and 50 < w <= 80]
            if hourly_winds
            else []
        )
        if moderate_wind_hours and not high_wind_hours:  # Only if no storm alert
            alerts.append(
                {
                    "type": "wind",
                    "severity": "advisory",
                    "start": (
                        hourly_times[moderate_wind_hours[0]]
                        if hourly_times
                        else datetime.now().isoformat()
                    ),
                    "end": (
                        hourly_times[
                            min(moderate_wind_hours[-1] + 1, len(hourly_times) - 1)
                        ]
                        if hourly_times
                        else (datetime.now() + timedelta(hours=2)).isoformat()
                    ),
                    "description": "High wind advisory: gusts 50-80 km/h expected",
                    "recommendations": [
                        "Be cautious in exposed areas",
                        "Check forecasts before outdoor activities",
                        "Secure loose items",
                        "Safe for most outdoor activities with caution",
                    ],
                }
            )

    except Exception:
        # Log error but don't fail the entire function
        pass

    return alerts


def normalize_timezone(
    response_data: Dict[str, Any], target_timezone: str = "UTC"
) -> Dict[str, Any]:
    """
    Normalize all timestamps in a weather/air quality response to a specified timezone.

    Args:
        response_data: API response data with timezone info
        target_timezone: Target timezone for conversion (default: 'UTC')

    Returns:
        Response data with all timestamps converted and timezone field updated
    """
    try:
        source_tz_str = response_data.get("timezone", "UTC")

        # Get source timezone
        try:
            source_tz = pytz.timezone(source_tz_str)
        except (pytz.UnknownTimeZoneError, KeyError, AttributeError):
            source_tz = pytz.UTC

        # Get target timezone
        try:
            target_tz = pytz.timezone(target_timezone)
        except (pytz.UnknownTimeZoneError, KeyError, AttributeError):
            target_tz = pytz.UTC

        # Convert hourly timestamps if present
        if "hourly" in response_data and isinstance(response_data["hourly"], dict):
            hourly = response_data["hourly"]
            if "time" in hourly and isinstance(hourly["time"], list):
                converted_times = []
                for time_str in hourly["time"]:
                    try:
                        # Parse ISO format timestamp
                        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        if dt.tzinfo is None:
                            dt = source_tz.localize(dt)
                        # Convert to target timezone
                        dt_converted = dt.astimezone(target_tz)
                        converted_times.append(dt_converted.isoformat())
                    except (ValueError, TypeError, AttributeError):
                        converted_times.append(time_str)
                hourly["time"] = converted_times

        # Convert daily timestamps if present
        if "daily" in response_data and isinstance(response_data["daily"], dict):
            daily = response_data["daily"]
            if "time" in daily and isinstance(daily["time"], list):
                converted_times = []
                for time_str in daily["time"]:
                    try:
                        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        if dt.tzinfo is None:
                            dt = source_tz.localize(dt)
                        dt_converted = dt.astimezone(target_tz)
                        converted_times.append(dt_converted.isoformat())
                    except (ValueError, TypeError, AttributeError):
                        converted_times.append(time_str)
                daily["time"] = converted_times

        # Update timezone field
        response_data["timezone"] = target_timezone

        return response_data

    except Exception:
        # If normalization fails, return original data
        return response_data


def normalize_air_quality_timezone(
    air_quality_data: Dict[str, Any], weather_timezone: str = "UTC"
) -> Dict[str, Any]:
    """
    Normalize air quality timestamps to match weather timezone.

    Air quality API returns UTC timestamps while weather API uses local timezone.
    This function converts air quality timestamps to match the weather timezone.

    Args:
        air_quality_data: Air quality API response
        weather_timezone: Target timezone (from weather endpoint)

    Returns:
        Air quality data with timestamps converted to weather timezone
    """
    try:
        # Get UTC timezone (air quality always uses UTC)
        utc_tz = pytz.UTC

        # Get target timezone
        try:
            target_tz = pytz.timezone(weather_timezone)
        except (pytz.UnknownTimeZoneError, KeyError, AttributeError):
            target_tz = pytz.UTC

        # Convert hourly timestamps if present
        if "hourly" in air_quality_data and isinstance(
            air_quality_data["hourly"], dict
        ):
            hourly = air_quality_data["hourly"]
            if "time" in hourly and isinstance(hourly["time"], list):
                converted_times = []
                for time_str in hourly["time"]:
                    try:
                        # Parse ISO format timestamp (should be UTC)
                        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        if dt.tzinfo is None:
                            dt = utc_tz.localize(dt)
                        # Convert to target timezone
                        dt_converted = dt.astimezone(target_tz)
                        converted_times.append(dt_converted.isoformat())
                    except (ValueError, TypeError, AttributeError):
                        converted_times.append(time_str)
                hourly["time"] = converted_times

        # Update timezone field
        air_quality_data["timezone"] = weather_timezone

        return air_quality_data

    except Exception:
        return air_quality_data


def calculate_astronomy_data(
    latitude: float, longitude: float, timezone: str = "UTC"
) -> Dict[str, Any]:
    """
    Calculate astronomical data for a location.

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        timezone: Timezone for the location

    Returns:
        Dictionary with sunrise, sunset, golden hour, blue hour times
    """
    try:
        from datetime import datetime, timedelta, time
        import math

        # Get current date
        now = datetime.now()
        today = now.date()

        # Get timezone object
        try:
            tz = pytz.timezone(timezone)
        except (pytz.UnknownTimeZoneError, KeyError, AttributeError):
            tz = pytz.UTC

        # Calculate sunrise and sunset using a simple approximation
        # This uses a standard formula for sunrise/sunset calculation
        lat_rad = math.radians(latitude)

        # Day of year
        day_of_year = today.timetuple().tm_yday
        n = day_of_year + (now.hour - 12) / 24

        # Solar mean anomaly
        J = n - (longitude / 360)
        M = (357.5291 + 0.98565 * J) % 360
        M_rad = math.radians(M)

        # Equation of center
        C = (
            1.9164 * math.sin(M_rad)
            + 0.02 * math.sin(2 * M_rad)
            + 0.0029 * math.sin(3 * M_rad)
        )

        # Ecliptic longitude
        lambda_sun = (
            280.4665 + 36000.76983 * (J / 36525) + 0.0003025 * ((J / 36525) ** 2)
        ) % 360
        lambda_sun = (lambda_sun + C) % 360
        lambda_sun_rad = math.radians(lambda_sun)

        # Solar declination
        delta = math.asin(math.sin(math.radians(23.4393)) * math.sin(lambda_sun_rad))

        # Sunrise/sunset hour angle
        cos_h = -math.tan(lat_rad) * math.tan(delta)
        cos_h = max(-1, min(1, cos_h))  # Clamp to [-1, 1]
        h = math.degrees(math.acos(cos_h))

        # UTC times
        utc_offset = longitude / 15
        sunrise_utc = 12 - h / 15 - utc_offset
        sunset_utc = 12 + h / 15 - utc_offset

        # Convert to datetime
        sunrise = datetime.combine(today, time(0)) + timedelta(hours=sunrise_utc)
        sunset = datetime.combine(today, time(0)) + timedelta(hours=sunset_utc)

        # Localize to timezone
        sunrise_tz = tz.localize(sunrise)
        sunset_tz = tz.localize(sunset)

        # Golden hour (30 minutes after sunrise, 30 minutes before sunset)
        golden_hour_start = sunrise_tz + timedelta(minutes=30)
        golden_hour_end = sunset_tz - timedelta(minutes=30)

        # Blue hour (civilian twilight ~30-50 minutes after sunset)
        blue_hour_start = sunset_tz
        blue_hour_end = sunset_tz + timedelta(minutes=40)

        return {
            "sunrise": sunrise_tz.isoformat(),
            "sunset": sunset_tz.isoformat(),
            "day_length_hours": round((sunset - sunrise).total_seconds() / 3600, 1),
            "golden_hour": {
                "start": golden_hour_start.isoformat(),
                "end": golden_hour_end.isoformat(),
                "duration_minutes": 30,
            },
            "blue_hour": {
                "start": blue_hour_start.isoformat(),
                "end": blue_hour_end.isoformat(),
                "duration_minutes": 40,
            },
            "moon_phase": "waxing gibbous",  # Simplified; would need lunar calculations
            "best_photography_windows": [
                {
                    "type": "golden_hour",
                    "start": golden_hour_start.isoformat(),
                    "end": golden_hour_end.isoformat(),
                },
                {
                    "type": "blue_hour",
                    "start": blue_hour_start.isoformat(),
                    "end": blue_hour_end.isoformat(),
                },
            ],
        }

    except Exception as e:
        return {"sunrise": None, "sunset": None, "error": str(e)}


def calculate_comfort_index(
    weather: Dict[str, Any], air_quality: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Calculate a comfort index for outdoor activities (0-100).

    Args:
        weather: Current weather conditions
        air_quality: Current air quality (optional)

    Returns:
        Dictionary with overall comfort index and factor breakdown
    """
    try:
        # Extract weather metrics
        temp = weather.get("temperature", 15)
        humidity = weather.get("relative_humidity_2m", 50)
        wind = weather.get("wind_speed_10m", 10)
        uv = weather.get("uv_index", 3)
        precip_prob = weather.get("precipitation_probability", 0)
        weather_code = weather.get("weather_code", 0)

        # Thermal comfort (heat index + wind chill)
        if temp > 25:
            # Heat index calculation
            thermal = 100 - min(40, (temp - 25) * 2 + (humidity - 40) * 0.5)
        elif temp < 5:
            # Wind chill effect
            wind_factor = calculate_wind_chill(temp, wind)
            thermal = max(0, 100 - min(50, (5 - wind_factor) * 3))
        else:
            thermal = 100 - abs(temp - 20) * 2

        # Air quality factor
        aqi = air_quality.get("european_aqi", 50) if air_quality else 50
        air_quality_factor = max(0, 100 - aqi)

        # Precipitation risk
        precip_factor = 100 - precip_prob

        # UV safety
        uv_factor = max(0, 100 - uv * 12)

        # Weather condition impact
        code_severity = interpret_weather_code(weather_code).get("severity", "low")
        severity_map = {"none": 100, "low": 85, "medium": 70, "high": 40, "extreme": 10}
        weather_factor = severity_map.get(code_severity, 50)

        # Calculate weighted overall comfort
        overall = (
            thermal * 0.25
            + air_quality_factor * 0.15
            + precip_factor * 0.20
            + uv_factor * 0.15
            + weather_factor * 0.25
        )

        # Determine recommendation
        if overall >= 80:
            recommendation = "Perfect for outdoor activities"
        elif overall >= 60:
            recommendation = "Good conditions for outdoor activities"
        elif overall >= 40:
            recommendation = "Fair conditions; plan accordingly"
        elif overall >= 20:
            recommendation = "Poor conditions; seek indoor alternatives"
        else:
            recommendation = "Very poor conditions; avoid outdoor activities"

        return {
            "overall": round(overall, 1),
            "factors": {
                "thermal_comfort": round(thermal, 1),
                "air_quality": round(air_quality_factor, 1),
                "precipitation_risk": round(precip_factor, 1),
                "uv_safety": round(uv_factor, 1),
                "weather_condition": round(weather_factor, 1),
            },
            "recommendation": recommendation,
        }

    except Exception:
        return {
            "overall": 50,
            "factors": {
                "thermal_comfort": 50,
                "air_quality": 50,
                "precipitation_risk": 50,
                "uv_safety": 50,
                "weather_condition": 50,
            },
            "recommendation": "Unable to calculate comfort index",
        }
