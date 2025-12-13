"""
District and Zone Configuration for CleanRoute

Each district is divided into zones for efficient truck allocation.
"""

# =============================================================================
# DISTRICT DEFINITIONS WITH ZONES
# =============================================================================

DISTRICTS = {
    "Colombo": {
        "id": "colombo",
        "name": "Colombo",
        "center": {"lat": 6.9271, "lon": 79.8612},
        "bounds": {"lat_min": 6.83, "lat_max": 6.98, "lon_min": 79.82, "lon_max": 79.92},
        "zones": {
            "zone1": {
                "id": "colombo_zone1",
                "name": "Fort & Pettah",
                "description": "Commercial area",
                "bounds": {"lat_min": 6.925, "lat_max": 6.980, "lon_min": 79.840, "lon_max": 79.865},
                "depot": {"lat": 6.9318, "lon": 79.8478, "name": "Fort Depot"},
                "color": "#FF6B6B"
            },
            "zone2": {
                "id": "colombo_zone2",
                "name": "Kollupitiya & Bambalapitiya",
                "description": "Central residential",
                "bounds": {"lat_min": 6.885, "lat_max": 6.925, "lon_min": 79.845, "lon_max": 79.865},
                "depot": {"lat": 6.9045, "lon": 79.8580, "name": "Galle Face Depot"},
                "color": "#4ECDC4"
            },
            "zone3": {
                "id": "colombo_zone3",
                "name": "Wellawatta & Dehiwala",
                "description": "South residential",
                "bounds": {"lat_min": 6.830, "lat_max": 6.885, "lon_min": 79.850, "lon_max": 79.875},
                "depot": {"lat": 6.8568, "lon": 79.8610, "name": "Dehiwala Depot"},
                "color": "#45B7D1"
            },
            "zone4": {
                "id": "colombo_zone4",
                "name": "Nugegoda & Kotte",
                "description": "Suburban east",
                "bounds": {"lat_min": 6.850, "lat_max": 6.920, "lon_min": 79.875, "lon_max": 79.920},
                "depot": {"lat": 6.8654, "lon": 79.8896, "name": "Nugegoda Depot"},
                "color": "#5F27CD"
            }
        }
    },
    "Kurunegala": {
        "id": "kurunegala",
        "name": "Kurunegala",
        "center": {"lat": 7.4867, "lon": 80.3647},
        "bounds": {"lat_min": 7.40, "lat_max": 7.55, "lon_min": 80.30, "lon_max": 80.45},
        "zones": {
            "zone1": {
                "id": "kurunegala_zone1",
                "name": "Town Center",
                "description": "Commercial & bus stand area",
                "bounds": {"lat_min": 7.480, "lat_max": 7.500, "lon_min": 80.355, "lon_max": 80.375},
                "depot": {"lat": 7.4867, "lon": 80.3647, "name": "Kurunegala Main Depot"},
                "color": "#FF9F43"
            },
            "zone2": {
                "id": "kurunegala_zone2",
                "name": "North Kurunegala",
                "description": "Residential north",
                "bounds": {"lat_min": 7.500, "lat_max": 7.550, "lon_min": 80.340, "lon_max": 80.400},
                "depot": {"lat": 7.5100, "lon": 80.3700, "name": "North Depot"},
                "color": "#EE5A24"
            },
            "zone3": {
                "id": "kurunegala_zone3",
                "name": "South Kurunegala",
                "description": "Residential south",
                "bounds": {"lat_min": 7.400, "lat_max": 7.480, "lon_min": 80.340, "lon_max": 80.400},
                "depot": {"lat": 7.4500, "lon": 80.3600, "name": "South Depot"},
                "color": "#F79F1F"
            }
        }
    },
    "Galle": {
        "id": "galle",
        "name": "Galle",
        "center": {"lat": 6.0328, "lon": 80.2170},
        "bounds": {"lat_min": 5.95, "lat_max": 6.10, "lon_min": 80.15, "lon_max": 80.28},
        "zones": {
            "zone1": {
                "id": "galle_zone1",
                "name": "Galle Fort & Town",
                "description": "Historic fort and commercial",
                "bounds": {"lat_min": 6.020, "lat_max": 6.050, "lon_min": 80.200, "lon_max": 80.230},
                "depot": {"lat": 6.0328, "lon": 80.2170, "name": "Galle Main Depot"},
                "color": "#1ABC9C"
            },
            "zone2": {
                "id": "galle_zone2",
                "name": "Unawatuna & South",
                "description": "Beach and tourist area",
                "bounds": {"lat_min": 5.950, "lat_max": 6.020, "lon_min": 80.200, "lon_max": 80.280},
                "depot": {"lat": 6.0100, "lon": 80.2500, "name": "Unawatuna Depot"},
                "color": "#16A085"
            }
        }
    },
    "Kandy": {
        "id": "kandy",
        "name": "Kandy",
        "center": {"lat": 7.2906, "lon": 80.6337},
        "bounds": {"lat_min": 7.25, "lat_max": 7.35, "lon_min": 80.58, "lon_max": 80.70},
        "zones": {
            "zone1": {
                "id": "kandy_zone1",
                "name": "Kandy City Center",
                "description": "Temple, lake, and commercial",
                "bounds": {"lat_min": 7.280, "lat_max": 7.310, "lon_min": 80.620, "lon_max": 80.650},
                "depot": {"lat": 7.2906, "lon": 80.6337, "name": "Kandy Main Depot"},
                "color": "#9B59B6"
            },
            "zone2": {
                "id": "kandy_zone2",
                "name": "Peradeniya & West",
                "description": "University and residential",
                "bounds": {"lat_min": 7.250, "lat_max": 7.290, "lon_min": 80.580, "lon_max": 80.620},
                "depot": {"lat": 7.2700, "lon": 80.6000, "name": "Peradeniya Depot"},
                "color": "#8E44AD"
            }
        }
    },
    "Matara": {
        "id": "matara",
        "name": "Matara",
        "center": {"lat": 5.9485, "lon": 80.5353},
        "bounds": {"lat_min": 5.90, "lat_max": 6.00, "lon_min": 80.48, "lon_max": 80.60},
        "zones": {
            "zone1": {
                "id": "matara_zone1",
                "name": "Matara Town",
                "description": "Fort and commercial",
                "bounds": {"lat_min": 5.930, "lat_max": 5.970, "lon_min": 80.520, "lon_max": 80.560},
                "depot": {"lat": 5.9485, "lon": 80.5353, "name": "Matara Main Depot"},
                "color": "#E74C3C"
            }
        }
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_districts():
    """Get list of all districts."""
    return list(DISTRICTS.values())


def get_district(district_id: str):
    """Get a specific district by ID."""
    for district in DISTRICTS.values():
        if district['id'] == district_id:
            return district
    return None


def get_district_zones(district_id: str):
    """Get all zones for a district."""
    district = get_district(district_id)
    if district:
        return list(district['zones'].values())
    return []


def assign_to_district_and_zone(lat: float, lon: float):
    """
    Assign a location to a district and zone based on coordinates.
    Returns (district, zone) tuple or (None, None) if not found.
    """
    for district_key, district in DISTRICTS.items():
        bounds = district['bounds']
        if (bounds['lat_min'] <= lat <= bounds['lat_max'] and
            bounds['lon_min'] <= lon <= bounds['lon_max']):
            
            # Found district, now find zone
            for zone_key, zone in district['zones'].items():
                zone_bounds = zone['bounds']
                if (zone_bounds['lat_min'] <= lat <= zone_bounds['lat_max'] and
                    zone_bounds['lon_min'] <= lon <= zone_bounds['lon_max']):
                    return district, zone
            
            # In district but not in a specific zone - assign to first zone
            first_zone = list(district['zones'].values())[0] if district['zones'] else None
            return district, first_zone
    
    return None, None


def get_zone_by_id(zone_id: str):
    """Get a zone by its full ID (e.g., 'colombo_zone1')."""
    for district in DISTRICTS.values():
        for zone in district['zones'].values():
            if zone['id'] == zone_id:
                return zone
    return None
