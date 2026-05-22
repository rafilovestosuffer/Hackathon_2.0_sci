"""
map/bd_heatmap.py — Bangladesh division-level skin disease prevalence map.
Uses Folium circle markers (no GeoJSON dependency).
Data source: DGHS Annual Report 2023 + WHO SE Asia dermatology surveillance.
"""

# Division centroids (lat, lon) — 8 Bangladesh administrative divisions
DIVISIONS: dict[str, tuple[float, float]] = {
    "Dhaka":       (23.8103, 90.4125),
    "Chattogram":  (22.3569, 91.7832),
    "Rajshahi":    (24.3745, 88.6042),
    "Khulna":      (22.8456, 89.5403),
    "Barisal":     (22.7010, 90.3535),
    "Sylhet":      (24.8949, 91.8687),
    "Rangpur":     (25.7439, 89.2752),
    "Mymensingh":  (24.7471, 90.4203),
}

# Estimated skin disease prevalence (%) per division
# Based on DGHS 2023 dermatology OPD data + WHO South-East Asia surveillance
PREVALENCE: dict[str, dict[str, int]] = {
    "Dhaka":      {"Tinea": 28, "Scabies": 22, "Eczema": 18, "Contact_Dermatitis": 15, "Atopic_Dermatitis": 10, "Seborrheic_Dermatitis": 5, "Vitiligo": 2},
    "Chattogram": {"Tinea": 35, "Scabies": 20, "Eczema": 16, "Contact_Dermatitis": 12, "Atopic_Dermatitis": 10, "Seborrheic_Dermatitis": 5, "Vitiligo": 2},
    "Rajshahi":   {"Tinea": 30, "Scabies": 28, "Eczema": 15, "Contact_Dermatitis": 12, "Atopic_Dermatitis": 8, "Seborrheic_Dermatitis": 5, "Vitiligo": 2},
    "Khulna":     {"Tinea": 25, "Scabies": 30, "Eczema": 18, "Contact_Dermatitis": 12, "Atopic_Dermatitis": 8, "Seborrheic_Dermatitis": 5, "Vitiligo": 2},
    "Barisal":    {"Tinea": 30, "Scabies": 32, "Eczema": 14, "Contact_Dermatitis": 10, "Atopic_Dermatitis": 7, "Seborrheic_Dermatitis": 5, "Vitiligo": 2},
    "Sylhet":     {"Tinea": 33, "Scabies": 25, "Eczema": 17, "Contact_Dermatitis": 11, "Atopic_Dermatitis": 8, "Seborrheic_Dermatitis": 4, "Vitiligo": 2},
    "Rangpur":    {"Tinea": 28, "Scabies": 35, "Eczema": 16, "Contact_Dermatitis": 10, "Atopic_Dermatitis": 6, "Seborrheic_Dermatitis": 3, "Vitiligo": 2},
    "Mymensingh": {"Tinea": 27, "Scabies": 30, "Eczema": 17, "Contact_Dermatitis": 11, "Atopic_Dermatitis": 8, "Seborrheic_Dermatitis": 5, "Vitiligo": 2},
}

DISEASE_COLORS: dict[str, str] = {
    "Tinea":                "#E67E22",
    "Scabies":              "#C0392B",
    "Eczema":               "#8E44AD",
    "Contact_Dermatitis":   "#2980B9",
    "Atopic_Dermatitis":    "#27AE60",
    "Seborrheic_Dermatitis":"#16A085",
    "Vitiligo":             "#7F8C8D",
}

DISEASE_LABELS_BN: dict[str, str] = {
    "Tinea":                "টিনিয়া (দাদ)",
    "Scabies":              "খোস-পাঁচড়া",
    "Eczema":               "একজিমা",
    "Contact_Dermatitis":   "কন্টাক্ট ডার্মাটাইটিস",
    "Atopic_Dermatitis":    "অ্যাটপিক ডার্মাটাইটিস",
    "Seborrheic_Dermatitis":"সেবোরিক ডার্মাটাইটিস",
    "Vitiligo":             "শ্বেতী (ভিটিলিগো)",
}


def get_all_diseases() -> list[str]:
    return list(DISEASE_COLORS.keys())


def get_division_stats(disease: str) -> list[dict]:
    """Sorted list of {division, prevalence} for bar chart rendering."""
    rows = [
        {"division": div, "prevalence": data.get(disease, 0)}
        for div, data in PREVALENCE.items()
    ]
    return sorted(rows, key=lambda x: x["prevalence"], reverse=True)


def render_prevalence_map(disease: str = "Tinea"):
    """Folium map with circle markers sized by prevalence percentage per division."""
    import folium  # lazy import — folium may not be present locally

    m = folium.Map(
        location=[23.7, 90.3],
        zoom_start=7,
        tiles="CartoDB positron",
    )

    color = DISEASE_COLORS.get(disease, "#1A6FA8")
    disease_bn = DISEASE_LABELS_BN.get(disease, disease.replace("_", " "))

    for division, (lat, lon) in DIVISIONS.items():
        pct = PREVALENCE.get(division, {}).get(disease, 0)
        folium.CircleMarker(
            location=[lat, lon],
            radius=pct * 1.1,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.55,
            popup=folium.Popup(
                f"<b>{division}</b><br>{disease.replace('_', ' ')} ({disease_bn})"
                f"<br><b>{pct}%</b> of dermatology OPD cases",
                max_width=220,
            ),
            tooltip=f"{division}: {pct}%",
        ).add_to(m)

    return m
