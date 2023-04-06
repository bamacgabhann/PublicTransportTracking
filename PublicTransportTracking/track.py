#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 17:54:13 2023

@author: Breandán Anraoi MacGabhann

Based on MovingPandas by Anita Graser and others,
which is Copyright (c) 2018-2023, MovingPandas developers

"""

import geopandas as gpd
from movingpandas import Trajectory

class Track(Trajectory):
    def __init__(self, gpx, journey_id=None, mode=None, route=None):
        """
        Create a track (a MovingPandas trajectory with additional properties) from a GPX file.

        Parameters
        ----------
        gpx : GPX file
            GPX file with time and point geometry data
        journey_id : any 
            Unique ID for the journey
        mode : str
            The mode of public transport
            (e.g. bus, train, tram)
        route : str
            Route ID for the journey

        Examples
        --------
        Creating a track:

        >>> import publictransporttracking as ptt
        >>> track = ptt.Track(file.gpx, 1, mode='Bus', route='304')
        """
        self.mode = str(mode)
        self.route = str(route)

        self.df = gpd.read_file(gpx, layer='track_points').set_index('time')
        if len(self.df)<2:
            raise ValueError("GPX must contain more than one point")
        cols = self.df.columns.tolist()
        if 'geometry' not in cols:
            raise ValueError("The GPX file must have geometry data")
        cols_to_keep = ['geometry']
        if 'track_fid' in cols: cols_to_keep.append('track_fid')
        if 'track_seg_id' in cols: cols_to_keep.append('track_seg_id')
        if 'track_seg_point_id' in cols: cols_to_keep.append('track_seg_point_id')
        if 'ele' in cols: cols_to_keep.append('ele')
        self.df = self.df[cols_to_keep]
        super().__init__(self.df, journey_id, obj_id=self.mode, crs="epsg:4326")
        #self.add_speed(name="speed (kph)", units=("km", "h"))  # uncomment and delete next 2 lines when mpd adds units support
        self.add_speed(name="speed (kph)")
        self.df["speed (kph)"] = self.df["speed (kph)"] * 3.6  
        self.add_distance(name="distance (m)")        

    def __str__(self):
        return (
            "Track {id} of {mode}, route {route}, ({t0} to {tn})"
            "Size: {n} | Length: {len:.1f}m\n".format(
                id=self.id,
                mode = self.mode if self.mode is not None else "Unknown mode",
                route = self.route if self.route is not None else "Unknown",
                t0=self.get_start_time(),
                tn=self.get_end_time(),
                n=self.size(),
                len=self.get_length(),
            )
        )

    def __repr__(self):
        try:
            line = self.to_linestring()
        except RuntimeError:
            return "Invalid trajectory!"
        wkt=line.wkt[:100]
        return wkt
    
    def __len__(self):
        return self.get_length()

