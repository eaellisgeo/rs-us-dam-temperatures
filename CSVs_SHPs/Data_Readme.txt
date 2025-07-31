This folder contains some reference data files used in the R and Python codes. All of these files can also be created, updated, or replaced in the notebooks as needed.


Files Included:

1. Study_Dams -- Shapefile of all dams used as a starting point of analysis 

2. Obstructed_Nodes_Base_Clean -- Shapefile of the SWORD nodes identified in R and manually cleaned --- Will also need to be uploaded as a GEE asset

3. Dam_AOIs -- Shapefile of a footprint of the obstructed nodes for each dam --- Will also need to be uploaded as a GEE asset

4. All_Possible_Gages_Site_Nos -- Excel file created from querying the USGS website for gages collecting temperature data

5. Site_Image_Match -- CSV file created manually determining the unique combination of USGS gages that fall within the same Landsat footprints. Note: Site numbers have leading zeros, handle with caution

6. USGS_Gages_AA_n87 -- Shapefile of the 87 gages used for Accuracy Assessment that have temperature data, along large rivers, and fall within the same Landsat image as another gage, during our study period

7. NA_SWORD_reach_v16_gt100 -- Shapefile created from SWORD NA files. Filtered by width and to CONUS. Only used for visualization purposes

8. Dam_Reservoir_Check -- Excel file of the dams with significant downstream differences that needed to be manually assessed for the presence of a reservoir. Completed in ArcGIS using imagery, NID, and SWORD nodes 

