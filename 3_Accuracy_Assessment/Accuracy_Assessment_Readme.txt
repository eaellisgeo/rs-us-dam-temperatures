To begin, RWC raw outputs are combined by dam (not unsnapped to any nodes) 
-- Instead, points are snapped based on the gage location for the accuracy assessment. Output is a CSV file for each dam with all the 
RWC outputs and their distance from the nearest SWORD node. This is a little bit of an intermediate step, but
this makes it a little easier for inspection and might be helpful for future work. 


File:  Export_Combined_RWC_Data_by_Dam.ipynb


To complete accuracy assessment, pull in dam AOIs and get the all the USGS gage data using a  list of 
temperature gages from the USGS website saved as an excel sheet. Each gage's closest SWORD node (from our cleaned
list of nodes) is selected. Then USGS gage data is pulled with NWIS API. This is saved as a CSV (to save time later) and pulled back in as a CSVs.
Filtering is completed to remove empty gages and errors. Associated dams are seletced  with a spatial join in ArcGIS.

Pull in the data for each dam. Find the temperature points (5 closest) for the gages. Create a dataframe with the average temperature and width for each gage.
Then  match up the Landsat information to the gage data (rounded to the nearest hour). Some cleaning needs to be done for gaps, naming conventions, etc. 

To get relative accuracy, a list of gages that fell within the same Landsat footprints (using ArcGIS) is compiled as a spreadsheet of the unique matchups. 
These are pulled into the notebook, joined, and the relative differences are calculated. 

This is used to get the RMSE, MAE, and Bias, as well as to create the graphics. 

File: Accuracy_Assessment.ipynb



