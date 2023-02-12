# Mathislewald Upload

Use this streamlit application as an upload interface for the Mathislewald app.
The application should be run in a docker container, mounting the target directories
from the container to the host.

The container saves to the following locations:

* `/src/data` for inventory data
* `/src/data/base` for base layer GeoTIFFs
* `/src/img` for inventory images
* `src/www` for checksums

The data folder should be mounted inside a GeoServer `geodata` folder to serve the data via WMS and WFS.
The images can be mounted into an assets folder of a web-application, or a public path of a web proxy server.
The checksums should be mounted inside a public path of a web proxy server