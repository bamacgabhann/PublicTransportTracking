#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 20:01:10 2023

@author: breandan
"""

import movingpandas as mpd
from movingpandas.trajectory_utils import convert_time_ranges_to_segments
from geopandas import GeoDataFrame
from shapely import Point

class TrajectoryStopDetectorPlus(mpd.TrajectoryStopDetector):
    
    def __init__(self, traj):
        #self.traj = traj
        super().__init__(traj)
    
    def get_stop_points_as_int(self, max_diameter, min_duration):
        """
        Returns detected stop location points

        Parameters
        ----------
        max_diameter : float
            Maximum diameter for stop detection
        min_duration : datetime.timedelta
            Minimum stop duration

        Returns
        -------
        geopandas.GeoDataFrame
            Stop locations as points with start and end time and stop duration
            in seconds

        Examples
        --------

        >>> detector = mpd.TrajectoryStopDetector(traj)
        >>> stops = detector.get_stop_points(min_duration=timedelta(seconds=60),
                                             max_diameter=100)
        """
        stop_time_ranges = self.get_stop_time_ranges(max_diameter, min_duration)
        stops = mpd.TrajectoryCollection(
            convert_time_ranges_to_segments(self.traj, stop_time_ranges)
        )

        stop_pts = GeoDataFrame(columns=["geometry"]).set_geometry("geometry")
        stop_pts["stop_id"] = [track.id for track in stops.trajectories]
        stop_pts = stop_pts.set_index("stop_id")

        for stop in stops:
            stop_pts.at[stop.id, "start_time"] = stop.get_start_time()
            stop_pts.at[stop.id, "end_time"] = stop.get_end_time()
            pt = Point(stop.df.geometry.x.median(), stop.df.geometry.y.median())
            stop_pts.at[stop.id, "geometry"] = pt
            stop_pts.at[stop.id, "traj_id"] = stop.parent.id

        if len(stops) > 0:
            stop_pts["duration_s"] = (
                stop_pts["end_time"] - stop_pts["start_time"]
            )
            stop_pts["duration_s"] = stop_pts["duration_s"].apply(lambda x: x.seconds)
            stop_pts["traj_id"] = stop_pts["traj_id"].astype(type(stop.parent.id))

        return stop_pts
