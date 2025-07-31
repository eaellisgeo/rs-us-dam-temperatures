This code was developed for "Satellite observations reveal widespread alteration of river thermal regimes by U.S. dams" (Ellis et al.)


This repository is divided into the following folders: 

0_Selecting_Rivers -- This R code is used to identify river reaches up- and downstreams of obstructions and calculate thier distances from the dams.

1_Extract_River_Temperatures -- This python code is used to dynamically extract river temperatures from Landsat 8 surface temperature product using a modified version of RivWidthCloud. 

2_Snap_Points_to_Centerlines -- This python code is used to join the temperature outputs to river centerlines. 

3_Accuracy_Assessment -- This python code is used to assess the intra-image accuracy of Landsat river surface temperature estimates.

4_River_Temperature_Analysis -- This python code is used to perform the analysis of temperature data and create base images for the graphics. 

CSVs_SHPs -- This folder contains some data inputs for the scripts. 
