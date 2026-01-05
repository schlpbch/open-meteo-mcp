# WMO Weather Codes Reference

This document provides a reference for interpreting WMO (World Meteorological Organization) weather codes returned by the Open-Meteo API.

## Weather Code Interpretation

| Code | Description | Category | Icon Suggestion |
|------|-------------|----------|-----------------|
| 0 | Clear sky | Clear | ☀️ |
| 1 | Mainly clear | Partly Cloudy | 🌤️ |
| 2 | Partly cloudy | Partly Cloudy | ⛅ |
| 3 | Overcast | Cloudy | ☁️ |
| 45 | Fog | Fog | 🌫️ |
| 48 | Depositing rime fog | Fog | 🌫️ |
| 51 | Drizzle: Light intensity | Drizzle | 🌦️ |
| 53 | Drizzle: Moderate intensity | Drizzle | 🌦️ |
| 55 | Drizzle: Dense intensity | Drizzle | 🌧️ |
| 56 | Freezing drizzle: Light | Freezing Rain | 🌧️❄️ |
| 57 | Freezing drizzle: Dense | Freezing Rain | 🌧️❄️ |
| 61 | Rain: Slight intensity | Rain | 🌧️ |
| 63 | Rain: Moderate intensity | Rain | 🌧️ |
| 65 | Rain: Heavy intensity | Rain | 🌧️ |
| 66 | Freezing rain: Light | Freezing Rain | 🌧️❄️ |
| 67 | Freezing rain: Heavy | Freezing Rain | 🌧️❄️ |
| 71 | Snow fall: Slight intensity | Snow | 🌨️ |
| 73 | Snow fall: Moderate intensity | Snow | 🌨️ |
| 75 | Snow fall: Heavy intensity | Snow | 🌨️ |
| 77 | Snow grains | Snow | 🌨️ |
| 80 | Rain showers: Slight | Showers | 🌦️ |
| 81 | Rain showers: Moderate | Showers | 🌧️ |
| 82 | Rain showers: Violent | Showers | 🌧️ |
| 85 | Snow showers: Slight | Snow Showers | 🌨️ |
| 86 | Snow showers: Heavy | Snow Showers | 🌨️ |
| 95 | Thunderstorm: Slight or moderate | Thunderstorm | ⛈️ |
| 96 | Thunderstorm with slight hail | Thunderstorm | ⛈️ |
| 99 | Thunderstorm with heavy hail | Thunderstorm | ⛈️ |

## Categories

### Clear Conditions
- **Codes**: 0-1
- **Characteristics**: Good visibility, minimal precipitation
- **Travel Impact**: Ideal conditions

### Cloudy Conditions
- **Codes**: 2-3
- **Characteristics**: Reduced sunshine, no precipitation
- **Travel Impact**: Generally good, reduced visibility

### Fog
- **Codes**: 45, 48
- **Characteristics**: Very low visibility
- **Travel Impact**: Delays possible, reduced visibility

### Rain
- **Codes**: 51-67, 80-82
- **Characteristics**: Wet conditions, varying intensity
- **Travel Impact**: Possible delays, wet surfaces

### Snow
- **Codes**: 71-77, 85-86
- **Characteristics**: Cold, reduced visibility
- **Travel Impact**: Significant delays possible, slippery conditions

### Thunderstorms
- **Codes**: 95-99
- **Characteristics**: Severe weather, lightning
- **Travel Impact**: Major delays, safety concerns

## Usage in Journey Planning

When planning journeys, consider:

1. **Clear/Partly Cloudy (0-3)**: Optimal travel conditions
2. **Fog (45-48)**: Allow extra time, check for delays
3. **Rain (51-82)**: Expect minor delays, bring rain gear
4. **Snow (71-86)**: Significant delays likely, check service status
5. **Thunderstorms (95-99)**: Major disruptions possible, consider rescheduling

## Data Source

Weather codes follow the WMO standard as implemented by Open-Meteo API.  
Reference: https://open-meteo.com/en/docs
