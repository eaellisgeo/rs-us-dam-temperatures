import ee

def merge_collections_std_bandnames_collection1tier1_sr():
    """merge landsat 5, 7, 8 collection 1 tier 1 SR imageCollections and standardize band names
    """
    ## standardize band names #### Updated for Collection 2 bands naming conventions
    bn8 = ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B6', 'QA_PIXEL', 'SR_B5', 'SR_B7']
    bn7 = ['SR_B1', 'SR_B1', 'SR_B2', 'SR_B3', 'SR_B5', 'QA_PIXEL', 'SR_B4', 'SR_B7']
    bn5 = ['SR_B1', 'SR_B1', 'SR_B2', 'SR_B3', 'SR_B5', 'QA_PIXEL', 'SR_B4', 'SR_B7']
    bns = ['uBlue', 'Blue', 'Green', 'Red', 'Swir1', 'BQA', 'Nir', 'Swir2']

    # create a merged collection from landsat 5, 7, and 8 #### Updated for new GEE Collection names
    ls5 = ee.ImageCollection("LANDSAT/LT05/C02/T1_L2").select(bn5, bns)

    ls7 = (ee.ImageCollection("LANDSAT/LE07/C02/T1_L2")
           .filterDate('1999-04-15', '2003-05-30')
           .select(bn7, bns))

    ls8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").select(bn8, bns)

    ls9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2").select(bn8,bns) ##### Updated to include Landsat 9

    merged = ls5.merge(ls7).merge(ls8).merge(ls9) ##### Updated to include Landsat 9

    return(merged)


def id2Img(id):
    return(ee.Image(merge_collections_std_bandnames_collection1tier1_sr()
    .filterMetadata('LANDSAT_PRODUCT_ID', 'equals', id) ###### Updated: C2 name is now "LANDSAT_PRODUCT_ID"
    .first()))

def Unpack(bitBand, startingBit, bitWidth):
    # unpacking bit bands
    # see: https://groups.google.com/forum/#!starred/google-earth-engine-developers/iSV4LwzIW7A
     ###### Updated: Match the Collection 2 the bit values
    return (ee.Image(bitBand)
            .rightShift(startingBit)
            .bitwiseAnd(ee.Number(2).pow(ee.Number(bitWidth)).subtract(ee.Number(1)).int()))
def UnpackAllSR(bitBand):
    # apply Unpack function for multiple pixel qualities
    bitInfoSR = {
    'Cloud': [3, 1],
    'CloudShadow': [4, 1],
    'SnowIce': [5, 1],
    'Water': [7, 1]
    }
    unpackedImage = ee.Image.cat([Unpack(bitBand, bitInfoSR[key][0], bitInfoSR[key][1]).rename([key]) for key in bitInfoSR])
    return unpackedImage
def AddFmaskSR(image):
    # // add fmask as a separate band to the input image
    temp = UnpackAllSR(image.select(['BQA']))

    fmask = (temp.select(['Water']).rename(['fmask'])
    .where(temp.select(['SnowIce']), ee.Image(3))
    .where(temp.select(['CloudShadow']), ee.Image(2))
    .where(temp.select(['Cloud']), ee.Image(4))
    .mask(temp.select(['Cloud']).gte(0)))

    return image.addBands(fmask)

def CalcHillShadowSR(image):
    dem = ee.Image("MERIT/DEM/v1_0_3").clip(image.geometry().buffer(9000).bounds()) ## Updated: correct Merit DEM location 
    SOLAR_AZIMUTH_ANGLE = ee.Number(image.get('SUN_AZIMUTH')) ####### Updated: changed name for SOLAR_AZIMUTH_ANGLE
    SOLAR_ZENITH_ANGLE = ee.Number(image.get('SUN_ELEVATION')) ####### Updated: changed name for SOLAR_ZENITH_ANGLE

    return(ee.Terrain.hillShadow(dem, SOLAR_AZIMUTH_ANGLE, SOLAR_ZENITH_ANGLE, 100, True)
    .reproject("EPSG:4326", None, 90).rename(['hillshadow']))

# /* functions to classify water (default) */
def ClassifyWater(imgIn, method = 'Jones2019'):
######## Not using these anymore with Collection 2, but need it to run
    if method == 'Jones2019':
        from functions_waterClassification_Jones2019 import ClassifyWaterJones2019
        return(ClassifyWaterJones2019(imgIn))
    elif method == 'Zou2018':
        from functions_waterClassification_Zou2018 import ClassifyWaterZou2018
        return(ClassifyWaterZou2018(imgIn))

# /* water function */
def CalculateWaterAddFlagsSR(imgIn, waterMethod = 'Jones2019'):
    #waterMethod = typeof waterMethod !== 'undefined' ? waterMethod : 'Jones2019'; ######## Commented put for collection 2
   
    fmask = AddFmaskSR(imgIn).select(['fmask'])

    fmaskUnpacked = (fmask.eq(4).rename('flag_cloud')
    .addBands(fmask.eq(2).rename('flag_cldShadow'))
    .addBands(fmask.eq(3).rename('flag_snowIce'))
    .addBands(fmask.eq(1).rename('flag_water')))

    water = fmask.eq(1).rename(['waterMask']).where(fmask.gte(2),ee.Image.constant(0)) ######## Updated: for Collection 2 and Fmask
    
    hillshadow = CalcHillShadowSR(imgIn).Not().rename(['flag_hillshadow'])

    imgOut = (ee.Image(water.addBands(fmask).addBands(hillshadow).addBands(fmaskUnpacked)
    .setMulti({
        'image_id': imgIn.get('LANDSAT_PRODUCT_ID'), ####### Updated: changed name for Collection 2
        'timestamp': imgIn.get('system:time_start'),
        'scale': imgIn.projection().nominalScale(),
        'crs': imgIn.projection().crs()
    })))

    return(imgOut)
