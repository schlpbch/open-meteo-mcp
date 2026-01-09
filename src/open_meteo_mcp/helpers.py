"""Helper functions for weather interpretation and formatting."""

from typing import Dict, Any


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
        48: {"description": "Depositing rime fog", "category": "Fog", "severity": "medium"},
        51: {"description": "Light drizzle", "category": "Drizzle", "severity": "low"},
        53: {"description": "Moderate drizzle", "category": "Drizzle", "severity": "low"},
        55: {"description": "Dense drizzle", "category": "Drizzle", "severity": "medium"},
        61: {"description": "Slight rain", "category": "Rain", "severity": "low"},
        63: {"description": "Moderate rain", "category": "Rain", "severity": "medium"},
        65: {"description": "Heavy rain", "category": "Rain", "severity": "high"},
        71: {"description": "Slight snow", "category": "Snow", "severity": "low"},
        73: {"description": "Moderate snow", "category": "Snow", "severity": "medium"},
        75: {"description": "Heavy snow", "category": "Snow", "severity": "high"},
        77: {"description": "Snow grains", "category": "Snow", "severity": "medium"},
        80: {"description": "Slight rain showers", "category": "Rain", "severity": "low"},
        81: {"description": "Moderate rain showers", "category": "Rain", "severity": "medium"},
        82: {"description": "Violent rain showers", "category": "Rain", "severity": "high"},
        85: {"description": "Slight snow showers", "category": "Snow", "severity": "low"},
        86: {"description": "Heavy snow showers", "category": "Snow", "severity": "high"},
        95: {"description": "Thunderstorm", "category": "Thunderstorm", "severity": "high"},
        96: {"description": "Thunderstorm with slight hail", "category": "Thunderstorm", "severity": "high"},
        99: {"description": "Thunderstorm with heavy hail", "category": "Thunderstorm", "severity": "extreme"},
    }
    
    return weather_codes.get(code, {
        "description": f"Unknown weather code: {code}",
        "category": "Unknown",
        "severity": "unknown"
    })


def get_weather_category(code: int) -> str:
    """
    Get the weather category for a WMO code.
    
    Args:
        code: WMO weather code
    
    Returns:
        Weather category (Clear, Cloudy, Rain, Snow, etc.)
    """
    return interpret_weather_code(code)["category"]


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
        "extreme": "severe"
    }
    
    return impact_map.get(severity, "unknown")


def assess_ski_conditions(snow_data: Dict[str, Any], weather_data: Dict[str, Any]) -> str:
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
    temp_f = temp * 9/5 + 32
    wind_mph = wind * 0.621371
    
    # Wind chill formula (Fahrenheit)
    wind_chill_f = (
        35.74 + 
        0.6215 * temp_f - 
        35.75 * (wind_mph ** 0.16) + 
        0.4275 * temp_f * (wind_mph ** 0.16)
    )
    
    # Convert back to Celsius
    wind_chill_c = (wind_chill_f - 32) * 5/9
    
    return round(wind_chill_c, 1)


def get_seasonal_advice(month: int) -> str:
    """
    Get seasonal advice for outdoor activities.
    
    Args:
        month: Month number (1-12)
    
    Returns:
        Seasonal advice string
    """
    seasons = {
        (12, 1, 2): "Winter: Ideal for skiing and snow sports. Dress warmly and check avalanche warnings.",
        (3, 4, 5): "Spring: Variable conditions. Snow melting at lower elevations. Good for hiking as weather improves.",
        (6, 7, 8): "Summer: Best for hiking, climbing, and outdoor activities. Watch for afternoon thunderstorms in mountains.",
        (9, 10, 11): "Autumn: Beautiful colors, but weather becoming unpredictable. Early snow possible at high elevations."
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
