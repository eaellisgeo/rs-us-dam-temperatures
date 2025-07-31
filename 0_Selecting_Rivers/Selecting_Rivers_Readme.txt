To begin this project, dams from the GROD database (1) were selected in ArcGIS. The database was filtered to the Lock and Dam types. Then the dams were selected based on their proximity to SWORD rivers(2) greater than 100m in width. 

Selected GROD dams were then spatially joined with the HILARRI database(3) to include hydropower information. Additionally, the dam selection was visually assessed before proceeding. 


The final shapefile of dams used as a base can be found in the CSVs_SHPs folder as: Study_Dams.shp

This R code also uses SWORD v16 Reaches and Nodes for North America (NA). This download can be found at: https://zenodo.org/records/10013982



Citations: 
1.  X. Yang, T. M. Pavelsky, M. R. V. Ross, S. R. Januchowski-Hartley, W. Dolan, E. H. Altenau, M. Belanger, D. Byron, M. Durand, I. Van Dusen, H. Galit, M. Jorissen, T. Langhorst, E. Lawton, R. Lynch, K. A. Mcquillan, S. Pawar, A. Whittemore, Mapping Flow-Obstructing Structures on Global Rivers. Water Resources Research 58, e2021WR030386 (2022).

2.  E. H. Altenau, T. M. Pavelsky, M. T. Durand, X. Yang, R. P. de M. Frasson, L. Bendezu, The Surface Water and Ocean Topography (SWOT) Mission River Database (SWORD): A Global River Network for Satellite Data Products. Water Resources Research 57, e2021WR030054 (2021).

3.  C. Hansen, P. Matson, Hydropower Infrastructure - LAkes, Reservoirs, and RIvers (HILARRI), V2, Oak Ridge National Laboratory (ORNL), Oak Ridge, TN (United States) (2023); https://doi.org/10.21951/HILARRI/1960141.


-------------------------------

The purpose of this code is to find each of the study dam's nearest river reach and then select the adjacent up and downstream reaches. Once these have been selected, it will calculate the linear referencing (distance upstream (-) or downstream (+) relative to the dam). The output of this code was then manually assessed to remove spurious branches and to create a single continuous path upstream from the dam.

The final cleaned output is used to extract temperatures from GEE in the remaining python notebooks. 