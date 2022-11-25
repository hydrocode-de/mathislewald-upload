# mathiswald-upload

[![Docker Image CI](https://github.com/hydrocode-de/mathislewald-upload/actions/workflows/docker-image.yml/badge.svg)](https://github.com/hydrocode-de/mathislewald-upload/actions/workflows/docker-image.yml)
[![DOI](https://zenodo.org/badge/569150876.svg)](https://zenodo.org/badge/latestdoi/569150876)


Streamlit application to upload datasources to Mathiswald application

## Prepare the server

Document this 

* Create the folder for geoserver to find inventory and base data
* Create a proxy config to forward to the streamlit app
* secure the application by either restricting to uni-fr IPs or by setting a .htaccess


## Run the container

The container can be run on the host system, which can mount the Geoserver and NGINX image folder locations.
Then run:

```
docker run -d --restart always -p 8501:8501  -v /host/path/to/geoserver:/src/data -v host/path/to/nginx/img:/src/img ghcr.io/hydrocode-de/mathislewald-upload
```

