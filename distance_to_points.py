# ---- Import libraries ----
import numpy as np
import pandas as pd
import geopandas as gpd
import os
from scipy.spatial import cKDTree
import networkx as nx
import pandana as pdna

def distance_to_points(centroids, points_of_interest, output_filename):
    data_dir = "data"
    output_dir = "output"

    # OS Open Road Nodes and Links
    dfNodes = pd.read_csv(os.path.join(data_dir, "OS Open Road Nodes.csv"))
    dfLinks = pd.read_csv(os.path.join(data_dir, "OS Open Road Links.csv"))
    dfNodes.drop_duplicates(inplace=True)
    dfNodes.set_index('identifier', inplace=True)

    # ---- Compute Distances ----
    # Get largest connected component
    edges = dfLinks.loc[:,['startNode','endNode','length']].values
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    largest_connected_component = sorted(nx.connected_components(G), key = len, reverse=True)[0]

    # Clean up to save memory
    G = None
    edges = None

    # Create pandana network. It's much faster for nearest point-of-interest analysis
    # Filter nodes and edges to just include those in the largest connected componet
    dfLinksLCC = dfLinks.loc[(dfLinks['startNode'].isin(largest_connected_component)) & (dfLinks['endNode'].isin(largest_connected_component))]
    dfNodesLCC = dfNodes.loc[largest_connected_component]
    net=pdna.Network(dfNodesLCC["x"], dfNodesLCC["y"], dfLinksLCC["startNode"], dfLinksLCC["endNode"], dfLinksLCC[["length"]])

    # Get the nearest three points of interest
    search_distance = 200000
    net.set_pois("points", search_distance, 3, points_of_interest.geometry.x, points_of_interest.geometry.y)
    dfNear = net.nearest_pois(search_distance, "points", num_pois=3, include_poi_ids=True)

    # ---- LSOA Computations ----
    # Get just the LSOA centroids and their nearest points
    lsoa_nodes = net.get_node_ids(centroids.X, centroids.Y)
    lsoaComps = dfNear.loc[lsoa_nodes]

    # Include LSOA codes
    centroids['lsoa_nodes'] = lsoa_nodes

    # Merge network distances and LSOA data
    lsoaComps.reset_index(inplace=True)
    lsoaComps = pd.merge(lsoaComps, centroids, left_on = 'identifier', right_on = 'lsoa_nodes', how = 'outer', indicator = True)

    # Wrangle
    lsoaComps['mean_distance_nearest_three_points'] = lsoaComps.loc[:,[1,2,3]].mean(axis = 1)

    # Write
    lsoaComps.to_csv(os.path.join(output_dir, output_filename), index=False)
