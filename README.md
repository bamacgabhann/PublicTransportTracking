# PublicTransportTracking

Using GPX tracks of public transport journeys to analyse a public transport network

Currently, a short Jupyter Notebook contains code to take a GPX file, and a geopackage with bus stop locations as points; and returns an interactive holoviews plot showing the journey colour-coded by speed in kilometres per hour, with stationary periods of more than 15 seconds within a 30m diameter circle shown as pink circles, and bus stop locations shown as blue + symbols. A list of all stationary periods mapped can also be produced.

The folder 'GPX' contains GPX tracks for some bus journeys in Limerick, Belfast, and Basel.

A second folder 'PNG' contains some PNG outputs of holoviews plots for these GPX tracks.

A much more complete package for analysis is in development.