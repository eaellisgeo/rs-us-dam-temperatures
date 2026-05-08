These notebooks contain the analysis and figures for the CONUS river temperature profiles 2013-2024. 
This is completed in two main steps: (1) Identify the usable profiles and distinct downstream differences (2) Analyze the profiles and create graphics

First File: Monte_Carlo_Kruskal_Wallis_Simulation.ipynb

This notebook first pulls in all the necessary datasets: dams, snapped temperature profiles, hydropower information (filtered and spatial joined from HILARRI).
Then finds the profiles that have at least 1km of up and downstream (within 20km) river nodes within the same Landsat image. 

To determine which profiles exhibit notable downstream differences, we use a Kruskal-Wallis test to compare points in the Up and Ds river classes. 
Kruskal-Wallis tests can be influenced by spatial autocorrelation, which is present in longitudinal profiles, we want to assess the possibility of type 1 error and account for any autocorrelation. 
So, this notebook does a Monte Carlo simulation to randomize the order of the observations and iteratively repeat the test. Based on the permuations, we get an overall p-value.
The output provides the significance values for each profile. We then classify profiles with Monte Carlo p-values < 0.05 as profiles with DS changes. 

#################
Intermediate information produced: The number of available profiles, number of profiles with notable differences, and the % of profiles that vary between a simple Kruskal-Wallis test and a Monte Carlo Simulation

Final exports: The significance values for unique each profile --- To be used in the next steps

_____________________________________________________________________
Second File: Dammed_River_Temperature_Analysis.ipynb

This notebook first pulls in all the necessary datasets: dams, dam info, snapped temperature profiles, and the profiles identified from the Monte Carlo analysis.

Then temperature nodes are joined to the significance information from the previous analysis. The difference between Up/DS averages is calculated. 
Also, the number of profiles warmer/cooler downstream are noted.

Calculate Descriptive Stats for Profiles: Gets the profile count, direction of change, median, mean, stdv, and range of DS changes. 

Calculate Deviations: Three types of deviations (difference between the temperature measurement and the mean). Gets the mean deviation by waterbody category. Plots them. 
When normalizing by profile average, also tests for significant differences with a traditional Kruskal-Wallis. 

Calculate the Average Difference with Distance: Plot downstream differences (mean and 95% confidence interval envelope) by 1km bins. Calculates difference ranges, slopes, and significance. 

File also has some base info for examples and graphics. Some basic descriptive statistics of the profiles. 
This also includes average difference breakdowns by the dam type.

#################
Intermediate exports: List of unique profiles, Nodes for profiles with changes, Nodes for profiles without changes, Average downstream changes, 
Average seasonal changes, DS differences by nodes, Seasonal profile average temperature by dam type, DS temperature changes by dam type, 
Stats for profiles with moderate differences, Stats for profiles with extreme differences

Final exports  = Graphics for: a study area map, example temperature profiles, box plots of river widths for accuracy assessment, boxen plots of profile temperatures, boxen plots of downstream changes,
downstream changes with distance line plots, and elements for mean deviation plots
