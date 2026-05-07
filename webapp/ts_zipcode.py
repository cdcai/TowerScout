#
# TowerScout
# A tool for identifying cooling towers from satellite and aerial imagery
#
# TowerScout Team:
# Karen Wong, Gunnar Mein, Thaddeus Segura, Jia Lu
#
# Licensed under CC-BY-NC-SA-4.0
# (see LICENSE.TXT in the root of the repository for details)
#

# zipcode outline provider

import geopandas as gpd

from ts_paths import get_base_dir

class Zipcode_Provider:
    def __init__(self):
        zipcode_path = get_base_dir() / 'data' / 'tl_2025_us_zcta520' / 'tl_2025_us_zcta520.shp'
        self.gdf = gpd.read_file(zipcode_path)

    def zipcode_polygon(self, zipcode):
        zp = self.gdf[self.gdf['ZCTA5CE20']==zipcode]
        return zp['geometry'].to_json()
