if __name__ == '__main__':

    import ee
    import numpy as np
    import getopt
    import argparse
    import sys
    import os
    from functions_landsat import id2Img
    from rwc_landsat import rwGenSR
    from FC_to_Desktop import ft2df # Used to bypass GEE tasks >> straight to desktop

    parser = argparse.ArgumentParser(prog = 'rwc_landsat_one_image.py',
    description = "Calculate river centerline and width in the provided Landsat scene. \
    (Example: python rwc_landsat_one_image.py LC08_L1TP_022034_20130422_20170310_01_T1 -f shp)")

    parser.add_argument('LANDSAT_ID', help = 'LANDSAT_ID for any Landsat 5, 7, and 8 SR scene', type = str)
    parser.add_argument('-f', '--FORMAT', help = "Output file format ('csv' or 'shp'). Default: 'csv'", type = str, default = 'csv')
    parser.add_argument('-w', '--WATER_METHOD', help = "Water classification method ('Jones2019' or 'Zou2018'). Default: 'Jones2019'", type = str, default = 'Jones2019')
    parser.add_argument('-d', '--MAXDISTANCE', help = 'Default: 4000 meters', type = float, default = 4000)
    parser.add_argument('-i', '--FILL_SIZE', help = 'Default: 333 pixels', type = float, default = 333)
    parser.add_argument('-b', '--MAXDISTANCE_BRANCH_REMOVAL', help = 'Default: 500 pixels', type = float, default = 500)
    parser.add_argument('-o', '--OUTPUT_FOLDER', help = 'Any existing folder name in Google Drive. Default: root of Google Drive', type = str, default = '')
    
    group_validation = parser.add_argument_group(title = 'Run the RivWidthCloud in POINT mode',
    description = 'In POINT mode, width only calculated for the region close to the point \
    location specified by its lon, lat, and an identifier. The radius of the region is specified through the specified buffer. \
    The point must locate within the bounds of the scene. \
    (Example: python rwc_landsat_one_image.py LC08_L1TP_022034_20130422_20170310_01_T1 -f shp -w Zou2018 -p -x -88.263 -y 37.453 -r 2000 -n testPoint)')

    group_validation.add_argument('-p', '--POINT', help = 'Enable the POINT mode', action = 'store_true')
    group_validation.add_argument('-x', '--LONGITUDE', help = 'Longitude of the point location', type = float)
    group_validation.add_argument('-y', '--LATITUDE', help = 'Latitude of the point location', type = float)
    group_validation.add_argument('-r', '--BUFFER', help = 'Radius of the buffered region around the point location', type = float, default = 4000)
    group_validation.add_argument('-n', '--POINT_NAME', help = 'identifier for the point', type = str)
    
    # I added this argument for the Dam Number
    group_validation.add_argument('-dam', '--DAMID', help = 'The Dam ID number', type = int)
    
    args = parser.parse_args()

    IMG_ID = args.LANDSAT_ID
    FORMAT = args.FORMAT
    WATER_METHOD = args.WATER_METHOD
    MAXDISTANCE = args.MAXDISTANCE
    FILL_SIZE = args.FILL_SIZE
    MAXDISTANCE_BRANCH_REMOVAL = args.MAXDISTANCE_BRANCH_REMOVAL
    OUTPUT_FOLDER = args.OUTPUT_FOLDER

    POINTMODE = args.POINT
    LONGITUDE = args.LONGITUDE
    LATITUDE = args.LATITUDE
    RADIUS = args.BUFFER
    ROI_NAME = args.POINT_NAME

    DAMID = args.DAMID

    ee.Initialize()

    # start of program
    img = id2Img(IMG_ID)

    # in validation, clip the original image around the validation site
    if POINTMODE:
        ## Updated to use bounding boxes for each dam
        BoundingBoxes = ee.FeatureCollection('projects/temperature-profiles/assets/RWCT_Data/Dam_AOIs_Final') # this would be updated for the asset location in GEE
        BoundingBoxes_sub = BoundingBoxes.filter(ee.Filter.eq('Assgn_dam', DAMID))
        aoi = BoundingBoxes_sub.geometry()
        rwc = rwGenSR(aoi = aoi, WATER_METHOD = WATER_METHOD, MAXDISTANCE = MAXDISTANCE, FILL_SIZE = FILL_SIZE, MAXDISTANCE_BRANCH_REMOVAL = MAXDISTANCE_BRANCH_REMOVAL)
        exportPrefix = IMG_ID ## Updated to match my naming conventions
    else:
        rwc = rwGenSR(WATER_METHOD = WATER_METHOD, MAXDISTANCE = MAXDISTANCE, FILL_SIZE = FILL_SIZE, MAXDISTANCE_BRANCH_REMOVAL = MAXDISTANCE_BRANCH_REMOVAL)
        exportPrefix = IMG_ID

    widthOut = rwc(img)

###############################################
### Inserting the Temperarure Extraction Process Here:
###############################################
# Add Earth Engine dataset
TempProduct = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')

# Filter the Image by ID
Filtered = TempProduct.filterMetadata('LANDSAT_PRODUCT_ID', 'equals', IMG_ID)

# Create a function to scale opt bands & scale thermal and convert Kelvin to Celsius
def scale(f):
    scale1 = f.select('SR_B3').multiply(0.0000275).add(-0.2).rename('SR_B3_sc')
    scale2 = f.select('SR_B6').multiply(0.0000275).add(-0.2).rename('SR_B6_sc')
    cel = f.select('ST_B10').multiply(0.00341802).add(149).subtract(273.15).rename('celsius')
    newBands = ee.Image([scale1,scale2,cel])
    return(f.addBands(newBands))

# Apply function for Temp conversion
LandsatTempProd_scale = Filtered.map(scale)

# Create and apply MNDWI Masks
# Function to Compute MNDWI
def mndwiFun(f):
    nd = f.normalizedDifference(['SR_B3_sc', 'SR_B6_sc']).rename('MNDWI')
    return(f.addBands(nd))

# Apply the function for MNDWI
LandsatMNDWI = LandsatTempProd_scale.map(mndwiFun)

# Function to create MNDWI Mask 
def maskFun(f):
    mndwiThreshold = f.select('MNDWI').gte(0.0)
    mndwiMask = f.updateMask(mndwiThreshold)
    return(mndwiMask)

# Apply the function for MNDWI Mask
LandsatMNDWImask = LandsatMNDWI.map(maskFun)

# Create a function to buffer all the river nodes and apply the function
def bufferFun(f):
  bufferPoint = f.buffer(30)
  return(bufferPoint)

# Get RWC Centerlines
centerline = ee.FeatureCollection(widthOut)
        
# Extract the Temps
cent_buff = centerline.map(bufferFun)

# function to reduce each image by the feature collection and add temp and date properties to each feature. 
def outputFun(f):
    a = f.select('celsius').reduceRegions(collection=cent_buff, reducer=ee.Reducer.mean())
    temp = a.get('mean')
    time = f.get('system:time_start')

    def addTempFun(ft):
        a = ft.set({'GEE_temp':ft.get('mean'), 'GEE_time':time,'Clst_Dam':DAMID})
        return(a)
    a = a.map(addTempFun)
    return(a)

# Apply function for reducing images. 
output = LandsatMNDWImask.map(outputFun)

# Filter out nulls and negative values
filtered_temp = output.flatten().filter(ee.Filter.notNull(['GEE_temp'])).filter(ee.Filter.gt('GEE_temp', 0))

# Clean up the Columns
Cleaned_Temp = filtered_temp.select(['crs','latitude','longitude','GEE_time','GEE_temp','image_id','width',
                                     'flag_cldShadow', 'flag_cloud', 'flag_water', 'Clst_Dam'])

# Export the Table as a CSV
asset = ee.FeatureCollection(Cleaned_Temp)
filename = str(IMG_ID)+'_'+ str(DAMID)
filepath = os.path.join(r"F:\Insert_File_Path_Here",filename +".csv") # Update File location here # Where the GEE outputs should be stored
print(f"Now processing {filename}")

# Export Function Below:
df = ft2df(
feature_collection=asset,
limit=None,
output_path=filepath,
)
