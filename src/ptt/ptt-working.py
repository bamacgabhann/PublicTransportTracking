import geopandas as gpd
import movingpandas as mpd
import hvplot.pandas
from datetime import datetime, timedelta

from shapely.geometry import Point, LineString, Polygon
from holoviews import opts

import warnings

warnings.filterwarnings("ignore")

plot_defaults = {"linewidth": 5, "capstyle": "round", "figsize": (10, 6), "legend": True}
opts.defaults(
    opts.Overlay(active_tools=["wheel_zoom"], frame_width=800, frame_height=600)
)

gpx = "GPX/2023/304 to UL 2023-03-09 0811.gpx"
bus_stops = gpd.read_file("GPKG/stops_304_to_UL.gpkg")
journey_plot_title = "304 to UL 2023-03-09 08:11"

gdf = gpd.read_file(gpx, layer="track_points").set_index("time")
gdf.drop(
    columns=[
        "magvar",
        "geoidheight",
        "name",
        "cmt",
        "desc",
        "src",
        "link1_href",
        "link1_text",
        "link1_type",
        "link2_href",
        "link2_text",
        "link2_type",
        "sym",
        "type",
        "fix",
        "sat",
        "hdop",
        "vdop",
        "pdop",
        "ageofdgpsdata",
        "dgpsid",
    ],
    inplace=True,
)
track = mpd.Trajectory(gdf, 1)
track.add_speed(name="speed (km/h)", units=("km", "h"))
track.add_distance(units="m")

track.df

stopped_time = 15

detector = mpd.TrajectoryStopDetector(track)
stationary_points = detector.get_stop_points(
    min_duration=timedelta(seconds=stopped_time), max_diameter=30
)

journey_plot = track.hvplot(
    c="speed (km/h)",
    clim=(0, 60),
    line_width=7.0,
    x="Longitude",
    y="Latitude",
    xlabel="Longitude",
    ylabel="Latitude",
    title=journey_plot_title,
    clabel="Speed (km/h)",
    tiles="CartoLight",
    cmap="RdYlGn",
    colorbar=True,
)

stationary_plot = stationary_points.hvplot(
    geo=True, size="duration_s", color="deeppink"
)

bus_stops_plot = bus_stops.hvplot(
    geo=True, size=40, marker="+", color="blue"
)  

track_plot = (
    journey_plot * stationary_plot * bus_stops_plot
)

track_plot

stop_time_ranges = detector.get_stop_time_ranges(
    min_duration=timedelta(seconds=15), max_diameter=30
)
for x in stop_time_ranges:
    print(x)