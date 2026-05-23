"""
map/hospital_finder.py — Emergency hospital finder via Overpass API (OpenStreetMap).
No API key required. Used only when triage tier == 3.

Provides:
  find_nearest_hospitals(lat, lon, n=5, radius_km=50) -> list[dict]
  render_hospital_map(hospitals, user_lat, user_lon) -> folium.Map
  get_district_coords(district_name) -> (lat, lon) | None
"""

import logging
import math
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
REQUEST_TIMEOUT = 30  # seconds — HF Spaces has variable latency; 10s caused frequent cold misses

# Default coordinates if user location unknown — Dhaka centre
_DEFAULT_LAT = 23.8103
_DEFAULT_LON = 90.4125

# Major Bangladesh district headquarters (lat, lon)
DISTRICT_COORDS: dict[str, tuple[float, float]] = {
    "dhaka":        (23.8103, 90.4125),
    "chittagong":   (22.3569, 91.7832),
    "chattogram":   (22.3569, 91.7832),
    "rajshahi":     (24.3745, 88.6042),
    "khulna":       (22.8456, 89.5403),
    "sylhet":       (24.8949, 91.8687),
    "barisal":      (22.7010, 90.3535),
    "barishal":     (22.7010, 90.3535),
    "rangpur":      (25.7439, 89.2752),
    "mymensingh":   (24.7471, 90.4203),
    "comilla":      (23.4607, 91.1809),
    "cumilla":      (23.4607, 91.1809),
    "narayanganj":  (23.6238, 90.4997),
    "gazipur":      (23.9999, 90.4203),
    "faridpur":     (23.6070, 89.8429),
    "tangail":      (24.2513, 89.9167),
    "bogura":       (24.8465, 89.3773),
    "bogra":        (24.8465, 89.3773),
    "jessore":      (23.1667, 89.2167),
    "jashore":      (23.1667, 89.2167),
    "cox's bazar":  (21.4272, 92.0058),
    "coxsbazar":    (21.4272, 92.0058),
    "noakhali":     (22.8696, 91.0988),
    "pabna":        (24.0064, 89.2372),
    "dinajpur":     (25.6279, 88.6338),
    "kushtia":      (23.9014, 89.1203),
    "brahmanbaria": (23.9571, 91.1115),
    "manikganj":    (23.8634, 90.0048),
    "narsingdi":    (23.9324, 90.7152),
    "habiganj":     (24.3745, 91.4156),
    "moulvibazar":  (24.4826, 91.7774),
    "sunamganj":    (25.0657, 91.3950),
    "netrokona":    (24.8705, 90.7270),
    "kishoreganj":  (24.4449, 90.7760),
    "sherpur":      (25.0204, 90.0159),
    "jamalpur":     (24.9372, 89.9378),
    "sirajganj":    (24.4536, 89.7058),
    "natore":       (24.4204, 88.9876),
    "chapainawabganj": (24.5959, 88.2765),
    "naogaon":      (24.8024, 88.9357),
    "joypurhat":    (25.0970, 89.0201),
    "gaibandha":    (25.3289, 89.5290),
    "nilphamari":   (25.9317, 88.8560),
    "lalmonirhat":  (25.9923, 89.2847),
    "kurigram":     (25.8066, 89.6360),
    "thakurgaon":   (26.0318, 88.4584),
    "panchagarh":   (26.3408, 88.5507),
    "pirojpur":     (22.5791, 89.9765),
    "jhalokathi":   (22.6397, 90.1993),
    "bhola":        (22.1785, 90.7169),
    "patuakhali":   (22.3596, 90.3296),
    "barguna":      (22.1521, 89.9978),
    "satkhira":     (22.7183, 89.0683),
    "bagerhat":     (22.6602, 89.7854),
    "narail":       (23.1724, 89.5124),
    "magura":       (23.4878, 89.4198),
    "jhenaidah":    (23.5448, 89.1526),
    "meherpur":     (23.7624, 88.6318),
    "chuadanga":    (23.6401, 88.8418),
    "khagrachhari": (23.1193, 91.9847),
    "rangamati":    (22.6523, 92.1803),
    "bandarban":    (22.1953, 92.2183),
    "feni":         (23.0183, 91.3976),
    "lakshmipur":   (22.9449, 90.8282),
    "chandpur":     (23.2513, 90.6718),
    "munshiganj":   (23.5422, 90.5320),
    "shariatpur":   (23.2427, 90.4349),
    "madaripur":    (23.1641, 90.2002),
    "gopalganj":    (23.0059, 89.8271),
    "rajbari":      (23.7579, 89.6442),
}


# ── DGHS division-level fallback (one hospital per division) ─────────────────
# Used when Overpass API fails — ensures PDF Section 4 always has a facility name.
_DIVISION_FALLBACK: list[dict] = [
    {"name": "Dhaka Medical College Hospital",          "address": "Bakshi Bazar, Dhaka",      "lat": 23.7248, "lon": 90.3976, "dist_km": 0.0, "phone": "02-55165088"},
    {"name": "Chittagong Medical College Hospital",     "address": "K B Fazlul Kader Rd, Chattogram", "lat": 22.3574, "lon": 91.8225, "dist_km": 0.0, "phone": "031-636368"},
    {"name": "Rajshahi Medical College Hospital",       "address": "Rajshahi",                 "lat": 24.3673, "lon": 88.5890, "dist_km": 0.0, "phone": "0721-772150"},
    {"name": "Khulna Medical College Hospital",         "address": "Khulna",                   "lat": 22.8328, "lon": 89.5396, "dist_km": 0.0, "phone": "041-731012"},
    {"name": "Sylhet MAG Osmani Medical College Hospital", "address": "Sylhet",               "lat": 24.8906, "lon": 91.8833, "dist_km": 0.0, "phone": "0821-713375"},
    {"name": "Barisal Sher-E-Bangla Medical College Hospital", "address": "Barisal",          "lat": 22.7108, "lon": 90.3616, "dist_km": 0.0, "phone": "0431-64213"},
    {"name": "Rangpur Medical College Hospital",        "address": "Rangpur",                  "lat": 25.7483, "lon": 89.2527, "dist_km": 0.0, "phone": "0521-63970"},
    {"name": "Mymensingh Medical College Hospital",     "address": "Mymensingh",               "lat": 24.7476, "lon": 90.4054, "dist_km": 0.0, "phone": "091-65001"},
]


def _nearest_division_fallback(lat: float, lon: float, n: int = 5) -> list[dict]:
    """Return the n nearest division hospitals from the static DGHS list."""
    scored = []
    for h in _DIVISION_FALLBACK:
        dist = _haversine_km(lat, lon, h["lat"], h["lon"])
        scored.append({**h, "dist_km": round(dist, 1)})
    scored.sort(key=lambda x: x["dist_km"])
    return scored[:n]


# ── Haversine distance ────────────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Overpass query ────────────────────────────────────────────────────────────

def _query_overpass(lat: float, lon: float, radius_m: int) -> list[dict]:
    """Return raw hospital elements from Overpass API. Retries once on timeout."""
    query = f"""
    [out:json][timeout:{REQUEST_TIMEOUT}];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      way["amenity"="hospital"](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """
    for attempt in range(2):
        try:
            resp = requests.post(
                OVERPASS_URL,
                data={"data": query},
                headers={"User-Agent": "SkinAI-BD/1.0 (https://huggingface.co/spaces/rafilovestosuffer/skinai-bangladesh)"},
                timeout=REQUEST_TIMEOUT + 10,
            )
            resp.raise_for_status()
            return resp.json().get("elements", [])
        except requests.exceptions.Timeout:
            if attempt == 0:
                logger.warning("Overpass timeout on attempt 1, retrying in 2 s…")
                time.sleep(2)
                continue
            logger.error("Overpass timed out after 2 attempts")
            return []
        except Exception as exc:
            logger.warning("Overpass query failed: %s", exc)
            return []
    return []


def _parse_element(el: dict, user_lat: float, user_lon: float) -> Optional[dict]:
    """Extract coordinates + tags from a node or way element."""
    tags = el.get("tags", {})
    if el["type"] == "node":
        lat, lon = el.get("lat"), el.get("lon")
    else:
        centre = el.get("center", {})
        lat, lon = centre.get("lat"), centre.get("lon")

    if lat is None or lon is None:
        return None

    name = (
        tags.get("name:en")
        or tags.get("name")
        or tags.get("name:bn")
        or "Hospital"
    )
    address_parts = [
        tags.get("addr:street", ""),
        tags.get("addr:city", ""),
        tags.get("addr:district", ""),
    ]
    address = ", ".join(p for p in address_parts if p) or "Bangladesh"

    return {
        "name":     name,
        "address":  address,
        "lat":      lat,
        "lon":      lon,
        "dist_km":  round(_haversine_km(user_lat, user_lon, lat, lon), 1),
        "phone":    tags.get("phone", ""),
        "osm_type": el["type"],
        "osm_id":   el["id"],
    }


# ── Public API ────────────────────────────────────────────────────────────────

def get_district_coords(district: str) -> Optional[tuple[float, float]]:
    """Return (lat, lon) for a Bangladesh district name, or None."""
    return DISTRICT_COORDS.get(district.lower().strip())


def find_nearest_hospitals(
    lat: float,
    lon: float,
    n: int = 5,
    radius_km: int = 50,
) -> list[dict]:
    """
    Return up to n nearest hospitals within radius_km of (lat, lon).
    Uses Overpass API. Returns [] on network failure — caller must handle.
    Each dict: {name, address, lat, lon, dist_km, phone}
    """
    elements = _query_overpass(lat, lon, radius_m=radius_km * 1000)
    hospitals = []
    for el in elements:
        parsed = _parse_element(el, lat, lon)
        if parsed:
            hospitals.append(parsed)

    hospitals.sort(key=lambda h: h["dist_km"])
    result = hospitals[:n]

    # If Overpass returned nothing, fall back to the static DGHS division list
    if not result:
        logger.warning("Overpass returned no hospitals — using DGHS division fallback.")
        result = _nearest_division_fallback(lat, lon, n=n)

    return result


def render_hospital_map(
    hospitals: list[dict],
    user_lat: float,
    user_lon: float,
):
    """
    Build and return a folium.Map with hospital pins + user location marker.
    Returns None if folium is unavailable or hospitals list is empty.
    """
    if not hospitals:
        return None
    try:
        import folium

        m = folium.Map(
            location=[user_lat, user_lon],
            zoom_start=11,
            tiles="OpenStreetMap",
        )

        # User location
        folium.Marker(
            location=[user_lat, user_lon],
            popup="📍 Your Location",
            icon=folium.Icon(color="blue", icon="user", prefix="fa"),
        ).add_to(m)

        tier3_red = "#dc2626"
        for i, h in enumerate(hospitals):
            rank = i + 1
            popup_html = (
                f"<b>#{rank} {h['name']}</b><br>"
                f"📍 {h['address']}<br>"
                f"🚗 {h['dist_km']} km away"
                + (f"<br>📞 {h['phone']}" if h.get("phone") else "")
            )
            folium.Marker(
                location=[h["lat"], h["lon"]],
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=f"#{rank} {h['name']} ({h['dist_km']} km)",
                icon=folium.Icon(
                    color="red" if rank == 1 else "orange",
                    icon="plus-sign",
                    prefix="glyphicon",
                ),
            ).add_to(m)

        # Fit bounds to show all markers
        all_lats = [user_lat] + [h["lat"] for h in hospitals]
        all_lons = [user_lon] + [h["lon"] for h in hospitals]
        m.fit_bounds(
            [[min(all_lats), min(all_lons)], [max(all_lats), max(all_lons)]],
            padding=(30, 30),
        )
        return m
    except Exception as exc:
        logger.error("render_hospital_map failed: %s", exc)
        return None
