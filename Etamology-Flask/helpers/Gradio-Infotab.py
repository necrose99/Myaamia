"""
gradio_infotab.py
Include module for Algonquian Dialectology Historical Mapping and GIS Infotabs.
"""

import os
import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Define the absolute, map-ready GeoJSON feature payload data with standardized coordinates
ALGIC_GEOJSON_DATA = {
  "type": "FeatureCollection",
  "properties": {
    "layer": "Algonquian Dialectology Timeline Asset",
    "temporal_scope": "Proto-Algonquian to 2026"
  },
  "features": [
    {
      "type": "Feature",
      "id": "bla",
      "properties": { "name": "Blackfoot", "group": "Plains", "iso_639_3": "bla" },
      "geometry": { "type": "Point", "coordinates": [-112.666666667, 50.0] }
    },
    {
      "type": "Feature",
      "id": "arp",
      "properties": { "name": "Arapaho", "group": "Plains", "iso_639_3": "arp" },
      "geometry": { "type": "Point", "coordinates": [-103.0, 40.0] }
    },
    {
      "type": "Feature",
      "id": "chy",
      "properties": { "name": "Cheyenne", "group": "Plains", "iso_639_3": "chy" },
      "geometry": { "type": "Point", "coordinates": [-95.0, 47.0] }
    },
    {
      "type": "Feature",
      "id": "mez",
      "properties": { "name": "Menominee", "group": "Central / Great Lakes", "iso_639_3": "mez" },
      "geometry": { "type": "Point", "coordinates": [-88.3333333333, 45.5] }
    },
    {
      "type": "Feature",
      "id": "cre",
      "properties": { "name": "Cree (Plains)", "group": "Central / Great Lakes", "iso_639_3": "crk" },
      "geometry": { "type": "Point", "coordinates": [-110.0, 54.0] }
    },
    {
      "type": "Feature",
      "id": "csw",
      "properties": { "name": "Swampy Cree", "group": "Central / Great Lakes", "iso_639_3": "csw" },
      "geometry": { "type": "Point", "coordinates": [-90.0, 56.0] }
    },
    {
      "type": "Feature",
      "id": "atj",
      "properties": { "name": "Atikamekw", "group": "Central / Great Lakes", "iso_639_3": "atj" },
      "geometry": { "type": "Point", "coordinates": [-74.0, 48.0] }
    },
    {
      "type": "Feature",
      "id": "pot",
      "properties": { "name": "Potawatomi", "group": "Central / Great Lakes", "iso_639_3": "pot" },
      "geometry": { "type": "Point", "coordinates": [-85.0, 44.5] }
    },
    {
      "type": "Feature",
      "id": "oji",
      "properties": { "name": "Ojibwe (Eastern)", "group": "Central / Great Lakes", "iso_639_3": "ojg" },
      "geometry": { "type": "Point", "coordinates": [-80.0, 46.0] }
    },
    {
      "type": "Feature",
      "id": "ciw",
      "properties": { "name": "Chippewa", "group": "Central / Great Lakes", "iso_639_3": "ciw" },
      "geometry": { "type": "Point", "coordinates": [-95.0, 48.0] }
    },
    {
      "type": "Feature",
      "id": "mia",
      "properties": { "name": "Miami-Illinois", "group": "Central / Great Lakes", "iso_639_3": "mia" },
      "geometry": { "type": "Point", "coordinates": [-90.0, 40.0] }
    },
    {
      "type": "Feature",
      "id": "sac",
      "properties": { "name": "Meskwaki (Fox)", "group": "Central / Great Lakes", "iso_639_3": "sac" },
      "geometry": { "type": "Point", "coordinates": [-83.0, 43.0] }
    },
    {
      "type": "Feature",
      "id": "kic",
      "properties": { "name": "Kickapoo", "group": "Central / Great Lakes", "iso_639_3": "kic" },
      "geometry": { "type": "Point", "coordinates": [-84.0, 42.25] }
    },
    {
      "type": "Feature",
      "id": "sjw",
      "properties": { "name": "Shawnee", "group": "Central / Great Lakes", "iso_639_3": "sjw" },
      "geometry": { "type": "Point", "coordinates": [-83.0, 40.0] }
    },
    {
      "type": "Feature",
      "id": "pim",
      "properties": { "name": "Powhatan", "group": "Eastern", "iso_639_3": "pim" },
      "geometry": { "type": "Point", "coordinates": [-76.5, 37.3333333333] }
    },
    {
      "type": "Feature",
      "id": "mic",
      "properties": { "name": "Mi'kmaq", "group": "Eastern", "iso_639_3": "mic" },
      "geometry": { "type": "Point", "coordinates": [-63.0, 45.0] }
    },
    {
      "type": "Feature",
      "id": "abe",
      "properties": { "name": "Western Abenaki", "group": "Eastern", "iso_639_3": "abe" },
      "geometry": { "type": "Point", "coordinates": [-72.25, 44.0] }
    },
    {
      "type": "Feature",
      "id": "pqm",
      "properties": { "name": "Maliseet-Passamaquoddy", "group": "Eastern", "iso_639_3": "pqm" },
      "geometry": { "type": "Point", "coordinates": [-67.0, 45.0] }
    },
    {
      "type": "Feature",
      "id": "xpq",
      "properties": { "name": "Mohegan-Pequot", "group": "Eastern", "iso_639_3": "xpq" },
      "geometry": { "type": "Point", "coordinates": [-72.0, 41.5] }
    },
    {
      "type": "Feature",
      "id": "umu",
      "properties": { "name": "Munsee", "group": "Eastern", "iso_639_3": "umu" },
      "geometry": { "type": "Point", "coordinates": [-74.6666666667, 41.5] }
    },
    {
      "type": "Feature",
      "id": "unm",
      "properties": { "name": "Unami", "group": "Eastern", "iso_639_3": "unm" },
      "geometry": { "type": "Point", "coordinates": [-75.1666666667, 40.0] }
    },
    {
      "type": "Feature",
      "id": "wiy",
      "properties": { "name": "Wiyot", "group": "Western Algic Isolate", "iso_639_3": "wiy" },
      "geometry": { "type": "Point", "coordinates": [-124.166666667, 40.8333333333] }
    },
    {
      "type": "Feature",
      "id": "yur",
      "properties": { "name": "Yurok", "group": "Western Algic Isolate", "iso_639_3": "yur" },
      "geometry": { "type": "Point", "coordinates": [-124.0, 41.3333333333] }
    },
    {
      "type": "Feature",
      "id": "bue",
      "properties": { 
        "name": "Beothuk", 
        "group": "Lost / Unattested Remnant Isolate", 
        "iso_639_3": "bue",
        "wals_code": "beo",
        "extinction_marker": "1829-06-06"
      },
      "geometry": { "type": "Point", "coordinates": [-57.0, 48.0] }
    }
  ]
}

def load_geopandas_dataframe():
    """Converts internal GeoJSON data directly to a GeoPandas GeoDataFrame."""
    features = ALGIC_GEOJSON_DATA["features"]
    rows = []
    for f in features:
        row = f["properties"].copy()
        row["id"] = f["id"]
        row["geometry"] = Point(f["geometry"]["coordinates"][0], f["geometry"]["coordinates"][1])
        rows.append(row)
    return gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")

def render_timeline_plot(selected_epoch):
    """Generates the localized GeoPandas matplotlib visualization based on temporal filters."""
    fig, ax = plt.subplots(figsize=(11, 6.5))
    
    # Safely load the Natural Earth base low-res continent outline map configuration
    try:
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        na_background = world[world.continent == 'North America']
        na_background.plot(ax=ax, color='#f4f4f7', edgecolor='#b0b0b0', linewidth=0.7)
    except Exception:
        # Fallback grid configuration if background dataset is offline or deprecated
        ax.set_facecolor('#fdfdfd')
        ax.grid(True, color='#ebebeb', linestyle='--')
        
    gdf = load_geopandas_dataframe()
    
    # 1. Proto-Algonquian Core Urheimat Phase (c. 1000 BCE)
    if selected_epoch == "Proto-Algonquian Urheimat Core (c. 1000 BCE)":
        proto_homeland = Point(-81.5, 46.5)
        homeland_gdf = gpd.GeoDataFrame([{"layer": "Urheimat Range"}], geometry=[proto_homeland], crs="EPSG:4326")
        homeland_gdf.buffer(7.0).plot(ax=ax, color='#e67e22', alpha=0.45, edgecolor='#d35400', linewidth=2)
        ax.text(-81.5, 46.5, "Proto-Algonquian Urheimat\n(Great Lakes Core Area)", fontsize=11, weight='bold', ha='center', color='#2c3e50')
        ax.set_title("Theoretical Ancestral Homeland Core Range", fontsize=13, weight='bold')

    # 2. Maximum Pre-Contact Colonial Footprint Expansion Zone (c. 1500 CE)
    elif selected_epoch == "Pre-Contact Expansion Footprint (c. 1500 CE)":
        # Group and display macro geographic clusters
        gdf[gdf["group"] == "Plains"].plot(ax=ax, color='#3498db', markersize=65, label='Plains Branch Expansion', edgecolor='black', zorder=3)
        gdf[gdf["group"] == "Central / Great Lakes"].plot(ax=ax, color='#2ecc71', markersize=65, label='Central/Woodlands Branch', edgecolor='black', zorder=3)
        gdf[gdf["group"] == "Eastern"].plot(ax=ax, color='#9b59b6', markersize=65, label='Eastern Seaboard Branch', edgecolor='black', zorder=3)
        
        # Overlay historical California western relatives (Yurok/Wiyot)
        gdf[gdf["group"] == "Western Algic Isolate"].plot(ax=ax, color='#f1c40f', markersize=80, marker='*', label='Western Algic Relatives', edgecolor='black', zorder=4)
        
        ax.set_title("Pre-Contact Geographic Spread (Maximum Footprint Overview)", fontsize=13, weight='bold')
        ax.legend(loc='lower left', framealpha=0.9)

    # 3. Modern Structural Reference Coordinates / 2026 Epoch
    else:
        # Plot modern language tracker index data
        gdf[gdf["id"] != "bue"].plot(ax=ax, color='#16a085', markersize=55, marker='o', label='Modern/Documented WALS Reference Point', edgecolor='black', zorder=3)
        
        # Specifically highlight the exact isolated locus of the extinct Beothuk language in Newfoundland
        gdf[gdf["id"] == "bue"].plot(ax=ax, color='#c0392b', markersize=90, marker='X', label='Beothuk (Extinct 1829)', edgecolor='black', zorder=5)
        
        ax.text(-57.0, 49.0, "Newfoundland\n(Beothuk)", fontsize=9, color='#c0392b', weight='bold', ha='center')
        ax.set_title("Linguistic Survey Map Index (WALS/Glottolog Data - 2026 Localized)", fontsize=13, weight='bold')
        ax.legend(loc='lower left', framealpha=0.9)

    ax.set_xlim([-130, -45])
    ax.set_ylim([35, 60])
    ax.set_xlabel("Longitude (WGS84)")
    ax.set_ylabel("Latitude (WGS84)")
    plt.tight_layout()
    return fig

def create_infotab_interface():
