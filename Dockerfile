FROM python:3.9

# make the structure
RUN mkdir -p /src/app
RUN mkdir -p /src/data
RUN mkdir -p /src/www
RUN mkdir -p /src/img

# copy the app
COPY ./requirements.txt /src/requirements.txt
COPY ./upload.py /src/app/upload.py
RUN echo "DATADIR=/src/data\nWWWDIR=/src/www\nIMGDIR=/src/img" >> /src/.env

# install requirements
RUN apt-get update && apt-get install -y libgdal-dev
#RUN pip install GDAL
RUN pip install -r /src/requirements.txt

# run
WORKDIR /src/app 
CMD ["streamlit", "run", "upload.py", "--server.maxUploadSize=2000"]