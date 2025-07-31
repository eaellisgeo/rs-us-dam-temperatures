## This pulls in a GEE Feature Collection (rather than an asset) and converts to a file on Desktop 

import ee
import geopandas as gpd

ee.Initialize()

output_format_list = ["shp", "geojson", "parquet", "csv"]


def ft2df(feature_collection, limit, output_path):
    try:
        if limit is not None:
            data = feature_collection.limit(limit)
        else:
            data = feature_collection
        # print(
        #     f"Valid feature collection: {feature_collection} with {data.size().getInfo()} features"
        # )
        params = {
            "expression": data,
            "fileFormat": "GEOPANDAS_GEODATAFRAME",
        }
        gdf = ee.data.computeFeatures(params)
        output_format = output_path.split(".")[-1].lower()
        if output_path is not None and output_format in output_format_list:
            if output_format == "shp":
                gdf.to_file(output_path, driver="ESRI Shapefile")
                print(f"Successfully exported to {output_path}")
            elif output_format == "geojson":
                gdf.to_file(output_path, driver="GeoJSON")
                print(f"Successfully exported to {output_path}")
            elif output_format == "parquet":
                gdf.to_parquet(output_path)
                print(f"Successfully exported to {output_path}")
            elif output_format == "csv":
                gdf.to_csv(output_path, index=False)
                print(f"Successfully exported to {output_path}")
            return gdf
        elif output_path is not None and output_format not in output_format_list:
            print("Output format not supported but returning geodataframe")
            return gdf
        elif output_format is None:
            return gdf

    except Exception as error:
        print(error)

    asset = ee.FeatureCollection(Temps_merged)
    filename = 'Temp_L8_Dam_'+ str(dams[i])
    filepath = os.path.join(r"F:\Insert_File_Path_Here",filename+".csv") ## Update File Path Here # Where GEE outputs should be stored
    print(f"Now processing {filename}")

    df = ft2df(
    feature_collection=asset,
    limit=None,
    output_path=filepath,
    )