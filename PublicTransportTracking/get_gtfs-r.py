#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 20:28:58 2023

@author: breandan


There are actually two functions in the code, get_bus_position and match_trip_updates.
For get_bus_position:

The variable interpolated_point in line 70 is undefined.
The threshold variable is undefined, so it should be defined or passed as an argument.
There is a duplicated comment in line 75.
For match_trip_updates:

There is a missing parenthesis in the line that defines the matching_stop_times variable in line 100, which could raise a syntax error.
There is a missing parenthesis in the line that defines the matching_shape_distance variable in line 110, which could raise a syntax error.


Given a trip_id, start_time, route_id, stop_times, and shapes, it will find the stop sequence for the specified trip in stop_times, and filter shapes to get the shape points for the specified route.

It will extract the shape points corresponding to the stops on the trip, construct a LineString from the stop points, and make a GTFS-realtime request for the trip updates from a specified URL.

It will find the update for the specified trip, extract the delay information for each stop on the trip, and calculate the estimated arrival time for each stop based on the delays.

It will interpolate the latitude and longitude of the bus based on the estimated arrival times, calculate the distance along the route for each stop, and interpolate the latitude and longitude of the bus along the route.

It will find the closest point on the route to the interpolated bus position, calculate the distance between the bus and the closest point on the route, and if the distance is greater than a threshold, it will discard the projection.

If the distance is not greater than the threshold, it will return the projected point, which represents the location of the bus along the route at the time of the GTFS-realtime update.



"""

import requests
import gtfs_realtime_pb2
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString

def get_bus_position(trip_id, start_time, route_id, stop_times, shapes):
    # Filter stop_times to get the stop sequence for the specified trip
    stop_sequence = stop_times[(stop_times['trip_id'] == trip_id) &
                               (stop_times['arrival_time'] == start_time) &
                               (stop_times['stop_sequence'] == 1)]['stop_sequence'].values[0]
    
    # Filter shapes to get the shape points for the specified route
    shape_points = shapes[shapes['shape_id'] == route_id][['shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence']]
    
    # Extract the shape points corresponding to the stops on the trip
    stop_points = stop_times[stop_times['trip_id'] == trip_id].merge(shape_points, on='shape_pt_sequence')
    
    # Construct a LineString from the stop points
    line = LineString(list(zip(stop_points['shape_pt_lon'], stop_points['shape_pt_lat'])))
    
    # Make a GTFS-realtime request for the trip updates
    url = 'http://gtfsrt.api.translink.com.au/Feed/SEQ'
    response = requests.get(url)
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    
    # Find the update for the specified trip
    for entity in feed.entity:
        if (entity.trip_update.trip.route_id == route_id and
            entity.trip_update.trip.trip_id == trip_id and
            entity.trip_update.trip.start_time == start_time and
            entity.trip_update.trip.schedule_relationship == 0):
            
            # Extract the delay information for each stop on the trip
            delays = {}
            for update in entity.trip_update.stop_time_update:
                delays[update.stop_sequence] = update.arrival.delay
                
            # Calculate the estimated arrival time for each stop based on the delays
            stop_times['estimated_arrival_time'] = np.nan
            for i, row in stop_times[stop_times['trip_id'] == trip_id].iterrows():
                if row['stop_sequence'] >= stop_sequence:
                    delay = delays.get(row['stop_sequence'], 0)
                    stop_times.loc[i, 'estimated_arrival_time'] = row['arrival_time'] + pd.Timedelta(delay, unit='s')
            
            # Interpolate the latitude and longitude of the bus based on the estimated arrival times
            stop_times = stop_times.interpolate(method='linear', limit_area='inside')
            
            # Calculate the distance along the route for each stop
            stop_points = stop_times[stop_times['trip_id'] == trip_id].merge(shape_points, on='shape_pt_sequence')
            stop_points['distance'] = stop_points['shape_dist_traveled'] - stop_points.iloc[0]['shape_dist_traveled']
            
            # Interpolate the latitude and longitude of the bus along the route
            bus_distance = stop_points[stop_points['estimated_arrival_time'].notna()]['distance'].values
            bus_lat = stop_points[stop_points['estimated_arrival_time'].notna()]['stop_lat'].values
            bus_lon = stop_points[stop_points['estimated_arrival_time'].notna()]['stop_lon'].values
            bus_line = LineString(list(zip(bus_lon, bus_lat)))
            bus_point = Point(bus_line.interpolate(bus_distance[-1], normalized=True))
            
            # Find the closest point on the route to the interpolated bus position
            # Find the closest point on the route to the interpolated bus position
            projected_point = line.interpolate(line.project(interpolated_point))
            
            # Calculate the distance between the bus and the closest point on the route
            distance = interpolated_point.distance(projected_point)
            
            # If the distance is greater than a threshold, discard the projection
            if distance > threshold:
                return None
            
            # Otherwise, return the projected point
            return projected_point         

            # Match the trip ID, start time, and route ID against stop_times dataframe
            trip_id = update["trip_update"]["trip"]["trip_id"]
            start_time = update["trip_update"]["trip"]["start_time"]
            route_id = update["trip_update"]["trip"]["route_id"]
            mask = (stop_times["trip_id"] == trip_id) & (stop_times["route_id"] == route_id) & (stop_times["arrival_time"] == start_time)
            matching_stop_times = stop_times[mask]
        
            # If no matching trip is found, return None
            if matching_stop_times.empty:
                return None
        
            # Get the stop IDs and delays from the update
            stop_ids = [stop_time_update["stop_id"] for stop_time_update in update["trip_update"]["stop_time_update"]]
            delays = [stop_time_update["arrival"]["delay"] if "arrival" in stop_time_update else stop_time_update["departure"]["delay"] for stop_time_update in update["trip_update"]["stop_time_update"]]
        
            # Get the stop sequence and corresponding shape distance traveled from matching_stop_times
            stop_sequence = matching_stop_times["stop_sequence"].values
            shape_dist_traveled = matching_stop_times["shape_dist_traveled"].values
        
            # Find the corresponding shape distance traveled for each stop ID in stop_ids
            matching_shape_distances = []
            for stop_id in stop_ids:
                matching_shape_distance = shapes.loc[shapes["shape_id"] == matching_stop_times["shape_id"].values[0]].loc[shapes["shape_pt_sequence"] == matching_stop_times.loc[matching_stop_times["stop_id"] == stop_id]["shape_pt_sequence"].values[0]]["shape_dist_traveled"].values
                matching_shape_distances.append(matching_shape_distance[0] if len(matching_shape_distance) > 0 else None)
        
            # Interpolate the latitudes and longitudes based on the shape distance traveled and matching_shape_distances
            latitudes = []
            longitudes = []
            for i in range(len(stop_ids)):
                if i == 0:
                    start_dist = 0
                else:
                    start_dist = matching_shape_distances[i-1]
                end_dist = matching_shape_distances[i]
                start_lat = matching_stop_times.loc[matching_stop_times["stop_id"] == stop_ids[i]]["stop_lat"].values[0]
                start_lon = matching_stop_times.loc[matching_stop_times["stop_id"] == stop_ids[i]]["stop_lon"].values[0]
                end_lat, end_lon = find_lat_lon_at_distance_along_shape(start_lat, start_lon, start_dist, end_dist, shapes)
                latitudes.append(end_lat)
                longitudes.append(end_lon)
        
            # Calculate the estimated latitude and longitude of the bus
            estimated_latitude = sum(latitudes) / len(latitudes)
            estimated_longitude = sum(longitudes) / len(longitudes)
        
            # Create a dictionary with the estimated latitude and longitude
            row_dict = {
                "latitude": estimated_latitude,
                "longitude": estimated_longitude
            }
        
            # Convert the dictionary to a geodataframe row and return it
            return gpd.GeoDataFrame([row_dict], geometry=gpd.points_from_xy([estimated_longitude], [estimated_latitude]))                          