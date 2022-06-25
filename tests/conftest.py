import os
import warnings

import ee
import geopandas as gpd
import pandas as pd
import pytest

import ecoscope


def pytest_configure(config):
    ecoscope.init()

    try:
        EE_ACCOUNT = os.getenv("EE_ACCOUNT")
        EE_PRIVATE_KEY_DATA = os.getenv("EE_PRIVATE_KEY_DATA")
        if EE_ACCOUNT and EE_PRIVATE_KEY_DATA:
            ee.Initialize(credentials=ee.ServiceAccountCredentials(EE_ACCOUNT, key_data=EE_PRIVATE_KEY_DATA))
        else:
            ee.Initialize()
        pytest.earthengine = True
    except ee.EEException:
        pytest.earthengine = False
        warnings.warn(Warning("Earth Engine can not be initialized. Skipping related tests..."))

    pytest.earthranger = ecoscope.io.EarthRangerIO(
        server=os.getenv("ER_SERVER", "https://sandbox.pamdas.org"),
        username=os.getenv("ER_USERNAME"),
        password=os.getenv("ER_PASSWORD"),
    ).login()
    if not pytest.earthranger:
        warnings.warn(Warning("EarthRanger_IO can not be initialized. Skipping related tests..."))


@pytest.fixture
def earthranger_io():
    ER_SERVER = "https://sandbox.pamdas.org"
    ER_USERNAME = os.getenv("ER_USERNAME")
    ER_PASSWORD = os.getenv("ER_PASSWORD")
    return ecoscope.io.EarthRangerIO(server=ER_SERVER, username=ER_USERNAME, password=ER_PASSWORD)


@pytest.fixture
def movbank_relocations():
    df = pd.read_feather("tests/sample_data/vector/movbank_data.feather")
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.pop("location-long"), df.pop("location-lat")),
        crs=4326,
    )
    gdf["timestamp"] = pd.to_datetime(gdf["timestamp"], utc=True)
    return ecoscope.base.Relocations.from_gdf(
        gdf,
        groupby_col="individual-local-identifier",
        time_col="timestamp",
        uuid_col="event-id",
    )


@pytest.fixture
def aoi_gdf():
    AOI_FILE = "tests/sample_data/vector/maec_4zones_UTM36S.gpkg"
    regions_gdf = gpd.GeoDataFrame.from_file(AOI_FILE).to_crs(4326)
    regions_gdf.set_index("ZONE", drop=True, inplace=True)
    return regions_gdf
