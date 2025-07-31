This notebook contains the analysis and figures for the CONUS river temperature profiles 2013-2024. 

To pull in all the necessary datasets: dams, snapped profiles, hydropower (filtered and spatial joined from HILARRI).
Then find the profiles that have at least 1km of up and downstream (within 20km) river nodes within the same Landsat image. 

Kruskal Wallis test is used to see which profiles (points) are significantly different up and downstream (comparing the Up and Ds river classes only).
Then nodes are rejoined back with the significance info. For significant profiles, the difference between Up/DS averages is calculated. 
Also, identified how many profiles were warm/cold. 

Intermediate exports: List of unique profiles, Significant Nodes, Not Significant nodes, KW Profile results, River Profile averages. 


Calculate Anomalies: Three types and their standard deviations. Plot them by their average by waterbody category. 

Calculate the Average Difference with Distance: Average all by 1km bins. Plot. Calculate the slopes and significance. 


#################
File also has some base info for examples and graphics. Some basic descriptive statistics of the profiles. 
This also includes average difference breakdowns by the dam type and KW significance tests between types.

