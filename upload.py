import streamlit as st
import os
import zipfile

import pandas as pd
import geopandas as gpd


# the code will be running in a container and thus, the output locations are passed as env variables
def get_env() -> dict:
    return dict(
        DATADIR=os.environ.get('DATADIR', 'out/data'),
        IMGDIR=os.environ.get('IMGDIR', 'out/img')
    )

def drop_session_data():
    if 'inventory' in st.session_state:
        del st.session_state.inventory
    if 'png_zip' in st.session_state:
        del st.session_state.png_zip
    
    st.experimental_rerun()

def base_data_page():
    """Component to control the base data upload page"""
    st.title('Upload base data')
    st.info('Base data is any kind of raster data, that the user may switch on/off while using the Map')
    
    upload_base_data()


def inventory_data_page():
    """Component to control the inventory data upload page"""
    st.title('Upload inventory data')
    st.info('Inventory data is the main data, which represents a Tree entity')

    # first get the inventory dataframe
    inv = get_inventory_df()

    # if at least the inv is there, add the drop button
    drop = st.sidebar.button('DROP CACHE')
    if drop:
        drop_session_data()

    # make a preview
    with st.expander('INVENTORY', expanded=True):
        st.dataframe(inv)

    # next step is to uplaod the png files
    zip = upload_inventory_img(inv)
    
    # process the inventory
    with st.spinner('START PROCESSING...'):
        # get the paths
        datapath = get_env().get('DATADIR')
        imgpath = get_env().get('IMGDIR')

        # convert the inventory
        gdf = gpd.GeoDataFrame(inv.copy(), geometry=gpd.points_from_xy(inv.x, inv.y, crs=32632))
        # TODO: THIS overwrites, we want merging?
        gdf.to_file(os.path.join(datapath, 'inventory.shp'))

        # go for the archive
        fnames = [f.filename for f in zip.filelist if not f.filename.startswith('__') and not f.filename.startswith('.')]
        for fname in fnames:
            zip.extract(fname, path=os.path.join(imgpath, fname))

    st.success('done.')

def upload_base_data():
    """
    Upload new base data to the data directory of geoserver.
    Terminates the Streamlit process if no file is uploaded
    """
    filenames = st.file_uploader('Raster base data', accept_multiple_files=True, type=['tif'])
    
    # number of files to process
    num = len(filenames)
    
    # check if something was uploaded
    if num > 0:
        # get environment variables
        path = get_env().get('DATADIR')

        bar = st.progress(0.0)
        for i, fname in enumerate(filenames):
            # get the file as bytes array
            barray = fname.getvalue()
            
            # get the fpath
            fpath = os.path.join(path, fname.name)
            # save to the datadir
            with open(fpath, 'wb') as f:
                f.write(barray)
            st.write(f'Wrote {fname.name} to target location: {fpath}')
            # update progressbar
            bar.progress((i + 1) / num)
        
        st.success('done')
        
    else:
        st.stop()


def upload_inventory_img(df: pd.DataFrame) -> zipfile.ZipFile:
    if 'png_zip' in st.session_state:
        return st.session_state.png_zip
    
    st.write('Upload image files for each Tree entity as specified in the inventory data.')
    st.write(f"Sample from the inventory: {', '.join(df.image.values[:3])}")

    # upload
    archive = st.file_uploader('Tree Image files', accept_multiple_files=False, type=['zip'])

    # if nothing was uploaded, stop
    if archive is None:
        st.stop()
    
    # get the zipfile
    zip = zipfile.ZipFile(archive)
    fnames = [f.filename for f in zip.filelist if not f.filename.startswith('__') and not f.filename.startswith('.')]
    st.info(f'Found {len(fnames)} files in the archive')

    # check for errors
    not_in_archive = []
    not_in_inventory = []
    with st.spinner('Checking files...'):
        for n in df.image.values:
            if n not in fnames:
                not_in_archive.append(n)
        for n in fnames:
            if n not in df.image.values:
                not_in_inventory.append(n)
    
    # check if there was a warning:
    if len(not_in_archive) > 0:
        st.warning(f"{len(not_in_archive)} files from the inventory were not found in the archive")
    if len(not_in_inventory) > 0:
        st.warning(f"{len(not_in_inventory)} files from the archive are not linked in the inventory")
    
    if len(not_in_archive) > 0 or len(not_in_inventory) > 0:
        with st.expander('WARNINGS'):
            st.json({'Not in archive': not_in_archive, 'Not in inventory': not_in_inventory})
        
        # user can stop here
        con = st.button('CONTINUE ANYWAY')
        if not con:
            st.stop()
    
    st.session_state.png_zip = zip
    st.experimental_rerun()


def get_inventory_df() -> pd.DataFrame:
    # first step is to load the inventory data
    if 'inventory' in st.session_state:
        return st.session_state.inventory
    
    # upload
    st.markdown("""The inventory data csv has to be a comma separated CSV using the header "TreeID","Radius","X","Y","Height","Image".
    The image data paths should only contain the image names.
    X and Y coordinates need to be transformed to EPSG 32632 first, as transformations are not (yet) implemented.""")
    
    fname = st.file_uploader('Inventory CSV', type=['csv'], accept_multiple_files=False)
    
    # if no file uploaded, terminate the app
    if fname is None:
        st.stop()
    
    df = pd.read_csv(fname)

    # convert the dataframe columns
    df.columns = [col.lower() for col in df.columns]

    # set the dataframe to the session and restart
    st.session_state.inventory = df
    st.experimental_rerun()
    


def main():
    # general config
    st.set_page_config(page_title='Mathislewald Uploader', layout='wide')

    #st.sidebar.markdown('### ')
    ACT = dict(inventory="Upload inventory data", base="Upload base raster")
    st.sidebar.radio('Select an action', options=list(ACT.keys()), format_func=lambda k: ACT.get(k), key="action")
    
    # switch the action
    if st.session_state.action=='inventory':
        inventory_data_page()
    elif st.session_state.action=='base':
        base_data_page()


if __name__ == '__main__':
    import fire
    fire.Fire(main)
