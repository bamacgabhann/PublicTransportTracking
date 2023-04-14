#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 18:52:43 2023

@author: breandan

Code by ChatGPT - just for ideas

"""

from geopy.distance import distance
from datetime import timedelta

def time_intervals_without_movement(gdf, max_distance, time_col):
    """
    Returns a list of time intervals when the geometry did not change within a specified distance range.

    :param gdf: A GeoDataFrame with point geometry and time columns.
    :type gdf: GeoDataFrame
    :param max_distance: The maximum distance (in meters) within which a change in location is considered movement.
    :type max_distance: float
    :param time_col: The name of the time column in the GeoDataFrame.
    :type time_col: str
    :return: A list of time intervals when the geometry did not change within the specified distance range.
    :rtype: list
    """
    
    # Define a function to calculate the distance between two points
    def calc_distance(row1, row2):
        point1 = (row1.geometry.y, row1.geometry.x)
        point2 = (row2.geometry.y, row2.geometry.x)
        return distance(point1, point2).meters
    
    # Sort the GeoDataFrame by the time column
    gdf = gdf.sort_values(time_col)
    
    # Initialize variables
    intervals = []
    start_time = gdf.iloc[0][time_col]
    prev_row = gdf.iloc[0]
    
    # Loop through the GeoDataFrame
    for i, row in gdf.iterrows():
        # Calculate the distance between the current row and the previous row
        dist = calc_distance(row, prev_row)
        
        # If the distance is greater than the max distance, update the interval
        if dist > max_distance:
            end_time = prev_row[time_col]
            intervals.append((start_time, end_time))
            start_time = row[time_col]
        
        # Update the previous row
        prev_row = row
    
    # Add the final interval
    end_time = gdf.iloc[-1][time_col]
    intervals.append((start_time, end_time))
    
    # Filter out intervals with zero duration
    intervals = [interval for interval in intervals if interval[0] != interval[1]]
    
    # Convert the intervals to timedeltas
    intervals = [(interval[1] - interval[0]).total_seconds() for interval in intervals]
    
    return intervals




from datetime import timedelta
import pandas as pd

def time_intervals_without_movement(gdf, max_distance, time_col):
    """
    Returns a GeoDataFrame with time intervals when the geometry did not change within a specified distance range.

    :param gdf: A GeoDataFrame with point geometry, time, and distance columns.
    :type gdf: GeoDataFrame
    :param max_distance: The maximum distance (in meters) within which a change in location is considered movement.
    :type max_distance: float
    :param time_col: The name of the time column in the GeoDataFrame.
    :type time_col: str
    :return: A GeoDataFrame with time intervals when the geometry did not change within the specified distance range.
    :rtype: GeoDataFrame
    """
    
    # Sort the GeoDataFrame by the time column
    gdf = gdf.sort_values(time_col)
    
    # Initialize variables
    intervals = []
    start_time = gdf.iloc[0][time_col]
    prev_row = gdf.iloc[0]
    prev_dist = 0
    
    # Loop through the GeoDataFrame
    for i, row in gdf.iterrows():
        # If the distance is greater than the max distance, update the interval
        if row['distance'] > max_distance:
            end_time = prev_row[time_col]
            duration = (end_time - start_time).total_seconds()
            intervals.append((prev_row.geometry, start_time, end_time, duration))
            start_time = row[time_col]
            prev_dist = 0
        
        # If the distance is less than or equal to the max distance, update the previous distance
        else:
            prev_dist = row['distance']
        
        # Update the previous row
        prev_row = row
    
    # Add the final interval
    end_time = gdf.iloc[-1][time_col]
    duration = (end_time - start_time).total_seconds()
    intervals.append((prev_row.geometry, start_time, end_time, duration))
    
    # Create a DataFrame from the intervals
    df = pd.DataFrame(intervals, columns=['geometry', 'start_time', 'end_time', 'duration'])
    
    # Create a GeoDataFrame from the DataFrame
    gdf_intervals = gpd.GeoDataFrame(df, geometry='geometry', crs=gdf.crs)
    
    return gdf_intervals

# TODO: Use gpd.GeoSeries.buffer() on a geoseries of the bus stop locations
# and spatial join to the output GDF to only output the stopped intervals at stops


import geopandas as gpd

def points_within_radius(gdf1, gdf2, radius):
    """
    Returns a GeoDataFrame with only rows from gdf1 where the geometry is within radius meters of a point in gdf2.

    :param gdf1: A GeoDataFrame with point geometry.
    :type gdf1: GeoDataFrame
    :param gdf2: A GeoDataFrame with point geometry.
    :type gdf2: GeoDataFrame
    :param radius: The radius (in meters) within which points are considered to be within range.
    :type radius: float
    :return: A GeoDataFrame with only rows from gdf1 where the geometry is within radius meters of a point in gdf2.
    :rtype: GeoDataFrame
    """
    
    # Create a buffer around the points in gdf2
    buffer = gdf2.buffer(radius)
    
    # Use a spatial join to find points in gdf1 that intersect the buffer
    join = gpd.sjoin(gdf1, buffer, op='within')
    
    return join[gdf1.columns]






import geopandas as gpd
from shapely.geometry import LineString, Point

def snap_points_to_route(gdf, route):
    """
    Returns a revised version of the GeoDataFrame with the points corrected to lie precisely on the route, adjusting
    them so that no errors are introduced in the distance and speed between adjacent points.

    :param gdf: A GeoDataFrame with time index and point geometry column.
    :type gdf: GeoDataFrame
    :param route: A GeoSeries representing a route.
    :type route: GeoSeries
    :return: A revised version of the GeoDataFrame with the points corrected to lie precisely on the route.
    :rtype: GeoDataFrame
    """
    
    # Create a LineString from the route GeoSeries
    route_line = LineString(route.geometry.values)
    
    # Create an empty list to hold the corrected points
    corrected_points = []
    
    # Loop over the points in the GeoDataFrame
    prev_point = None
    for _, row in gdf.iterrows():
        # Get the point geometry
        point = row.geometry
        
        # Find the nearest point on the route to the point
        nearest_point = route_line.interpolate(route_line.project(point))
        
        # Adjust the corrected point so that no errors are introduced in distance and speed
        if prev_point is not None:
            distance = nearest_point.distance(prev_point)
            time_delta = row.name - prev_time
            speed = distance / time_delta.total_seconds()
            if speed > 30:  # maximum speed of 30 m/s
                distance = 30 * time_delta.total_seconds()
                nearest_point = route_line.interpolate(route_line.project(prev_point, normalized=True) + distance / route_line.length)
        
        # Add the corrected point to the list
        corrected_points.append(nearest_point)
        
        prev_point = nearest_point
        prev_time = row.name
    
    # Create a new GeoDataFrame with the corrected points
    corrected_gdf = gpd.GeoDataFrame(gdf.drop('geometry', axis=1),
                                     geometry=corrected_points,
                                     crs=gdf.crs)
    
    return corrected_gdf






import geopandas as gpd
from shapely.geometry import LineString

def speed_range_along_route(*gdfs):
    # Merge input GeoDataFrames into a single GeoDataFrame
    merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    # Group merged GeoDataFrame by line along the route
    lines_gdf = merged_gdf.groupby('line')['geometry'].apply(lambda x: LineString(x.tolist())).reset_index(name='geometry')
    
    # Calculate speed range along each line
    speeds_gdf = merged_gdf.groupby('line').agg({'speed': ['min', 'max']}).reset_index()
    speeds_gdf.columns = ['line', 'min_speed', 'max_speed']
    
    # Merge speed range into lines GeoDataFrame
    result_gdf = lines_gdf.merge(speeds_gdf, on='line', how='left')
    
    return result_gdf