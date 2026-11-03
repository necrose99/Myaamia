# helpers/visualization.py
import io
import os
import base64
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib
matplotlib.use('Agg')  # Headless server-safe rendering mode
import matplotlib.pyplot as plt

# Import the language definition mappings from your local file
from languages import ALGIC_LANGUAGE_REGISTRY

CACHE_IMAGE_PATH = "static/cache_algic_dashboard.png"

GROUP_COLORS = {
    "Central": "#1abc9c",    # Teal
    "Eastern": "#2980b9",    # Blue
    "Plains":  "#e67e22",    # Orange
    "Western": "#e74c3c",    # Red (California Outliers)
    "Remnant": "#7f8c8d",    # Gray
    "Ancestral": "#9b59b6"  # Purple
}

# Geographic centers representing pre-contact distribution hubs
BASELINE_COORDS = {
    "alg-x-proto": {"lon": -120.0, "lat": 46.0}, # Columbia Plateau Urheimat Model
    "yur": {"lon": -124.0, "lat": 41.2},
    "wiy": {"lon": -124.2, "lat": 40.6},
    "bft": {"lon": -113.0, "lat": 50.0},
    "arp": {"lon": -105.5, "lat": 40.0},
    "ats": {"lon": -109.5, "lat": 48.0},
    "chy": {"lon": -104.5, "lat": 39.0},
    "cre": {"lon": -105.0, "lat": 55.0},
    "csw": {"lon": -92.0,  "lat": 54.0},
    "crj": {"lon": -74.0,  "lat": 51.0},
    "atj": {"lon": -73.5,  "lat": 48.0},
    "men": {"lon": -88.5,  "lat": 45.0},
    "pot": {"lon": -86.5,  "lat": 42.5},
    "oji": {"lon": -90.0,  "lat": 47.0},
    "otw": {"lon": -82.0,  "lat": 45.0},
    "ciw": {"lon": -93.0,  "lat": 46.5},
    "mia": {"lon": -87.5,  "lat": 40.0},
    "sac": {"lon": -92.5,  "lat": 42.0},
    "kic": {"lon": -88.5,  "lat": 39.5},
    "sjw": {"lon": -84.0,  "lat": 38.0},
    "mic": {"lon": -65.0,  "lat": 47.0},
    "abe": {"lon": -72.5,  "lat": 44.5},
    "aaq": {"lon": -69.0,  "lat": 45.0},
    "mal": {"lon": -67.5,  "lat": 45.5},
    "moo": {"lon": -72.0,  "lat": 41.5},
    "mua": {"lon": -74.5,  "lat": 41.0},
    "unm": {"lon": -75.0,  "lat": 40.0},
    "bue": {"lon": -56.0,  "lat": 49.0},
    "etc": {"lon": -67.0,  "lat": 45.0},
    "xlo": {"lon": -72.0,  "lat": 42.5},
    "xlb": {"lon": -73.0,  "lat": 43.0},
    "crr": {"lon": -79.0,  "lat": 34.5},
    "pim": {"lon": -76.5,  "lat": 37.5},
    "qyp": {"lon": -72.8,  "lat": 41.3}
}

def generate_spatial_registry_dataframe():
    """Merges your catalog definitions with geographical baseline vectors."""
    records = []
    for iso_code, meta in ALGIC_LANGUAGE_REGISTRY.items():
        if iso_code in BASELINE_COORDS:
            coords = BASELINE_COORDS[iso_code]
            records.append({
                "iso": iso_code,
                "name": meta["name"],
                "group": meta["group"],
                "subfamily": meta["subfamily"],
                "lon": coords["lon"],
                "lat": coords["lat"]
            })
    return pd.DataFrame(records)

def render_registry_map_element():
    """Transforms dataframe records into a map element string."""
    df = generate_spatial_registry_dataframe()
    if df.empty:
        return '<div class="alert alert-danger">No aligned coordinate markers found.</div>'
        
    # Build geometry metrics using target coordinate layers
    geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]
    geo_df = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # Safe buffering: project to equal-area projection, buffer by 75km, drop back to 4326
    geo_df = geo_df.to_crs("EPSG:3857")
    geo_df["geometry"] = geo_df.geometry.buffer(75000)
    geo_df = geo_df.to_crs("EPSG:4326")
    
    # Load underlying structural geographic surface map layers
    try:
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    except (AttributeError, ValueError):
        # Clean CDN backup layer parsing strategy
        world = gpd.read_file("https://cloudfront.net")
        
    north_america = world[world['name'].isin(['United States of America', 'Canada'])]
    
    fig, ax = plt.subplots(figsize=(13, 8))
    north_america.to_crs("EPSG:4326").plot(ax=ax, color='#eaeaea', edgecolor='white')
    
    # Render language group polygons based on custom dictionary mappings
    for group_name, group_data in geo_df.groupby("group"):
        color = GROUP_COLORS.get(group_name, "#7f8c8d")
        group_data.plot(
            ax=ax, 
            color=color, 
            alpha=0.65, 
            edgecolor="black", 
            linewidth=1.2, 
            label=group_name
        )
        
    # Annotate spatial points dynamically using centroids
    for idx, row in geo_df.iterrows():
        ax.annotate(
            text=row['name'],
            xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
            xytext=(2, 2),
            textcoords="offset points",
            fontsize=7,
            weight='bold',
            alpha=0.85
        )
        
    plt.title("Algic Language Family Structural Distribution & Sub-Family Matrix", fontsize=12, pad=12)
    plt.grid(True, linestyle="--", alpha=0.25)
    
    # Anchor coordinates to continental view limits
    ax.set_xlim([-130, -50])
    ax.set_ylim([30, 60])
    
    # Save a copy to the filesystem cache folder
    os.makedirs(os.path.dirname(CACHE_IMAGE_PATH), exist_ok=True)
    plt.savefig(CACHE_IMAGE_PATH, format='png', bbox_inches='tight', dpi=150)
    
    # Encode plot straight to image byte stream buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
    img_buffer.seek(0)
    plt.close(fig)
    
    encoded_img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return f'<img src="data:image/png;base64,{encoded_img}" class="img-fluid algic-map-frame" alt="Algic Registry Map">'
