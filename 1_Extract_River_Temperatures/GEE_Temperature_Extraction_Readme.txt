To extract temperatures from the Landsat 8 collection 2 surface temperature product, we first modified the 
python RivWidthCloud code to handle the updated Landsat Collection 2 data and its new bitmasking scheme. There are 
some artifacts of previous code left/commented out as needed to avoid altering arguments.

This code also clips the image to a region of interest, runs RivWidthCloud, and extracts the surface temperatures 
at the centerline locations. Additionally, we have modified the code to include a function to export the csv 
results directly to a desktop folder -- bypassing GEE and Google Drive. 

To run, the dam locations (points), selected and cleaned SWORD nodes (points), and the dams' areas of interests (polygons) 
are uploaded into GEE as assets to be called as features with GEE Python API. 

To speed up the process and reduce the chance of timing out, multiple instances of the script (saved and labeled accordingly) were run at the same time. 
This was done by using a subset of the list of dams to filter and loop thru. 


#################################################################################################
Original RivWidthCloud Information can be found here: https://github.com/seanyx/RivWidthCloudPaper

Yang, X., T.M. Pavelsky, G.H. Allen, and G. Donchyts (2019), RivWidthCloud: An Automated Google Earth Engine algorithm for river width extraction from remotely sensed imagery, IEEE Geoscience and Remote Sensing Letters. DOI: 10.1109/LGRS.2019.2920225