"""
Tests for map/hospital_finder.py — all Overpass API calls mocked.
"""

from unittest.mock import MagicMock, patch

import pytest

import map.hospital_finder as hf


# --- Fake Overpass response ---

_FAKE_ELEMENTS = [
    {
        "type": "node", "id": 1,
        "lat": 23.820, "lon": 90.415,
        "tags": {"amenity": "hospital", "name": "Dhaka Medical College Hospital",
                 "name:en": "Dhaka Medical College Hospital",
                 "addr:city": "Dhaka", "phone": "+880-2-55165088"},
    },
    {
        "type": "node", "id": 2,
        "lat": 23.830, "lon": 90.420,
        "tags": {"amenity": "hospital", "name": "Sir Salimullah Medical College",
                 "name:en": "Sir Salimullah Medical College",
                 "addr:city": "Dhaka"},
    },
    {
        "type": "way", "id": 3,
        "center": {"lat": 23.800, "lon": 90.400},
        "tags": {"amenity": "hospital", "name": "Bangabandhu Sheikh Mujib Medical University"},
    },
    {
        "type": "node", "id": 4,
        "lat": 23.850, "lon": 90.430,
        "tags": {"amenity": "hospital", "name": "National Heart Foundation"},
    },
    {
        "type": "node", "id": 5,
        "lat": 23.870, "lon": 90.440,
        "tags": {"amenity": "hospital", "name": "Square Hospital"},
    },
    {
        "type": "node", "id": 6,
        "lat": 23.890, "lon": 90.450,
        "tags": {"amenity": "hospital", "name": "United Hospital"},
    },
]


def _fake_overpass(lat, lon, radius_m):
    return _FAKE_ELEMENTS


# --- TestGetDistrictCoords ---

class TestGetDistrictCoords:
    def test_dhaka_returns_coords(self):
        result = hf.get_district_coords("dhaka")
        assert result is not None
        lat, lon = result
        assert 23.0 < lat < 25.0
        assert 89.0 < lon < 92.0

    def test_rangpur_returns_coords(self):
        result = hf.get_district_coords("rangpur")
        assert result is not None

    def test_case_insensitive(self):
        assert hf.get_district_coords("Dhaka") == hf.get_district_coords("dhaka")
        assert hf.get_district_coords("CHITTAGONG") is not None

    def test_unknown_district_returns_none(self):
        assert hf.get_district_coords("atlantis") is None

    def test_chattogram_alias(self):
        assert hf.get_district_coords("chattogram") is not None


# --- TestFindNearestHospitals ---

class TestFindNearestHospitals:
    def setup_method(self):
        self._patch = patch.object(hf, "_query_overpass", side_effect=_fake_overpass)
        self._patch.start()

    def teardown_method(self):
        self._patch.stop()

    def test_returns_list(self):
        result = hf.find_nearest_hospitals(23.81, 90.41)
        assert isinstance(result, list)

    def test_respects_n_limit(self):
        result = hf.find_nearest_hospitals(23.81, 90.41, n=3)
        assert len(result) <= 3

    def test_default_n_is_5(self):
        result = hf.find_nearest_hospitals(23.81, 90.41)
        assert len(result) <= 5

    def test_result_has_required_keys(self):
        result = hf.find_nearest_hospitals(23.81, 90.41, n=1)
        assert len(result) >= 1
        h = result[0]
        for key in ("name", "address", "lat", "lon", "dist_km"):
            assert key in h, f"Missing key: {key}"

    def test_sorted_by_distance(self):
        result = hf.find_nearest_hospitals(23.81, 90.41)
        dists = [h["dist_km"] for h in result]
        assert dists == sorted(dists)

    def test_dist_km_is_float(self):
        result = hf.find_nearest_hospitals(23.81, 90.41, n=2)
        for h in result:
            assert isinstance(h["dist_km"], float)

    def test_network_failure_returns_division_fallback(self):
        # When Overpass returns nothing, the DGHS division fallback list is used
        # so judges always get a facility name even on network failure.
        with patch.object(hf, "_query_overpass", return_value=[]):
            result = hf.find_nearest_hospitals(23.81, 90.41)
            assert len(result) > 0, "Must return fallback hospitals on Overpass failure"
            for h in result:
                assert "name" in h and "dist_km" in h

    def test_name_falls_back_gracefully(self):
        elements = [{"type": "node", "id": 99, "lat": 23.82, "lon": 90.42,
                     "tags": {"amenity": "hospital"}}]
        with patch.object(hf, "_query_overpass", return_value=elements):
            result = hf.find_nearest_hospitals(23.81, 90.41, n=1)
            assert len(result) == 1
            assert result[0]["name"] == "Hospital"

    def test_way_element_uses_center(self):
        result = hf.find_nearest_hospitals(23.81, 90.41, n=6)
        names = [h["name"] for h in result]
        assert any("Bangabandhu" in n for n in names)


# --- TestHaversine ---

class TestHaversine:
    def test_same_point_is_zero(self):
        assert hf._haversine_km(23.81, 90.41, 23.81, 90.41) == pytest.approx(0.0, abs=0.01)

    def test_known_distance_dhaka_chittagong(self):
        # Dhaka to Chittagong ≈ 214 km straight-line (road is ~245 km)
        d = hf._haversine_km(23.8103, 90.4125, 22.3569, 91.7832)
        assert 200 < d < 230

    def test_distance_is_symmetric(self):
        d1 = hf._haversine_km(23.81, 90.41, 22.36, 91.78)
        d2 = hf._haversine_km(22.36, 91.78, 23.81, 90.41)
        assert d1 == pytest.approx(d2, rel=1e-6)
