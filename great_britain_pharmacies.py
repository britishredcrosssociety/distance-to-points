import pandas as pd
import geopandas as gpd
import os
from distance_to_points import distance_to_points

# ----  Globals & Functions ----
# Set datat dir
data_dir = "data"

# Set CRS
GBcrs = {"init":"epsg:27700"}

# ---- Load Data ----
# LSOA 2011 Pop Weighted Centroids: https://geoportal.statistics.gov.uk/datasets/lower-layer-super-output-areas-december-2011-population-weighted-centroids
dfLSOACent = pd.read_csv(os.path.join(data_dir, Lower_Layer_Super_Output_Areas_December_2011_Population_Weighted_Centroids.csv))
dfLSOACent = dfLSOACent.loc[:, ['DataZone', 'Easting', 'Northing']]
dfLSOACent.columns = ['lsoa11cd', 'X', 'Y']

# Scottish Data Zone centroids
dfDZCent = gpd.read_file(os.path.join(data_dir, "SG_DataZone_Cent_2011.shp"))

# Combine England/Wales LSOAs and Scotland Data Zones into one
dfLSOACent2 = dfLSOACent.loc[:, ['lsoa11cd', 'X', 'Y']]
dfDZCent2 = dfDZCent.loc[:, ['DataZone', 'Easting', 'Northing']]
dfDZCent2.columns = ['lsoa11cd', 'X', 'Y']
dfLSOACent = pd.concat([dfLSOACent2, dfDZCent2])

# Load points of interest + change crs
scotlandGeoJSON = gpd.read_file(os.path.join(scotland_dir, "points.geojson"))
scotlandGeoJSON = scotlandGeoJSON.to_crs(GBcrs)
