# Code for Selecting rivers/nodes affected by dams and linear referencing them

###################################################
# Document Prep
###################################################
# Load Libraries
library(tidyverse)
library(sf)
library(doParallel)
library(stringr)
library(ggplot2)

###################################################
# Data  Prep
###################################################
# Load in Dams -- Near >100m rivers (selected and manually assessed in ArcGIS)
dams <- st_read("Insert_File_Path_of_Shapefile_with_Dam_Locations.shp") # Update this file path

## Merge SWORD Shapefiles ##
# Centerlines
C_file_list <- list.files("Data/NA_v16/NA_Reaches_v16", pattern = "*shp", full.names = TRUE) ## Download SWORD data v16 and use NA Reach Folder
C_shapefile_list <- lapply(C_file_list, read_sf)
all_centerlines <- do.call(rbind, C_shapefile_list)

# Nodes
N_file_list <- list.files("Data/NA_v16/NA_Nodes_v16", pattern = "*shp", full.names = TRUE) ## Download SWORD data v16 and use NA Nodes Folder
N_shapefile_list <- lapply(N_file_list, read_sf)
all_nodes <- do.call(rbind, N_shapefile_list)

###################################################
# Select Data 
###################################################
dams <- within(dams,rm(sword_reac))
dams <- within(dams,rm(distance_t))

# Set up Parallelization 
cl <- makeCluster(6) # Note the number of cores appropriate for the CPU
registerDoParallel(cl) # only run if new session

# Find River Segments Nearest to the Dams
closest <- foreach(i= 1:nrow(dams),.packages=c('sf'), .combine = 'c') %dopar% {
  reach_id <-  all_centerlines[which.min(
    st_distance(all_centerlines, dams[i,])),]$reach_id
  
  return(reach_id)
}

dams$closest_reach <- closest

# Run when it is done to stop the parallel loop
stopCluster(cl)


##### Select Upstream and Downstream Segments & Assign Dam ##### 

## Function to make list of reaches upstream and downstream from a specific reach
## river = river network sf object
## dam_number = the dam id number
## starting_reach = reach id to start at 
## distance_upstream = distance (m) upstream 
## distance_downstream = distance (m) downstream  
## distance_past_lake = distance (m) past lake flag 

## Notes:
# at each iteration, "is it a lake"?
# once there are two not lakes reaches in a row, start counting distance to 20000m


grab_reaches <- function(river, dam_number, starting_reach, distance_upstream, distance_downstream, distance_past_lake) {
  # List of reaches to keep 
  keep_reaches <- c(starting_reach)
  
  # starting reach id 
  next_reach_id <- starting_reach
  
  # Do upstream 
  # Set starting distance to 0
  d <- 0
  dl <- 0
  # Are we in a lake? 
  lake <- 0
  
  for (i in 1:1000) { 
    print(paste0("i=", i))
    # There could be more than one upstream reach id, so loop through them 
    track_next_reach_id <- c()
    for(j in next_reach_id){
      print(paste0("j=", j))
      # Index the upstream reach id 
      reach_id_up <- river[river$reach_id == j, ]
      print(reach_id_up)
      reach_id_up <- reach_id_up[rowSums(is.na(reach_id_up)) < ncol(reach_id_up)-5, ]
      print(reach_id_up)
      if(nrow(reach_id_up) == 0){ 
        print("skipping")
        next }
      lake_flag <- reach_id_up$lakeflag
      reach_distance <- reach_id_up$reach_len
      reach_id_up <- reach_id_up$rch_id_up
      # Split apart 
      reach_id_up <- str_split(reach_id_up, " ")[[1]]
      # Only keep the actual ids - get rid of 'no data'
      reach_id_up <- reach_id_up[!reach_id_up == "no_data"]
      # Add those reaches to the final list of reaches that you keep 
      keep_reaches <- c(keep_reaches, reach_id_up)
      # Track reaches that are the next level upstream 
      track_next_reach_id <- c(track_next_reach_id, reach_id_up)
      # Set this lake flag as the last lake flag for next iteration 
      last_lake_flag <- lake_flag
    }
    
    # Check if two reaches outside of lake. 
    if(sum(last_lake_flag) + sum(lake_flag)== 0){
      lake =1
    }
    # Add up distance past lake 
    if(lake == 1){
      dl = dl + reach_distance
    }
    #Add the reach you are keeping in this iteration to the total distance
    d <- d + reach_distance
    # Is it minimum dist upstream and minimum dist past lake?
    if((d > distance_upstream) & (dl > distance_past_lake)){break }   

    # next level of reaches upstream 
    next_reach_id <- track_next_reach_id
    
  }
  total_upstream_distance <- d
  upstream_reaches <- keep_reaches

  # Do downstream
  # starting reach id
  next_reach_id <- starting_reach
  # List of reaches to keep
  keep_reaches <- c()
  # Set starting distance to 0
  d <- 0
  for (i in 1:1000) {

    # There could be more than one downstream reach id, so loop through them
    track_next_reach_id <- c()
    for(j in next_reach_id){
      # Index the upstream reach id
      reach_id_down <- river[river$reach_id == j, ]
      reach_id_down <- reach_id_down[rowSums(is.na(reach_id_down)) < ncol(reach_id_down)-5, ]
      if(nrow(reach_id_down) == 0){ next }
      reach_distance <- reach_id_down$reach_len
      reach_id_down <- reach_id_down$rch_id_dn
      # Split apart
      reach_id_down <- str_split(reach_id_down, " ")[[1]]
      # Only keep the actual ids - get rid of 'no data'
      reach_id_down <- reach_id_down[!reach_id_down == "no_data"]
      # Add those reaches to the final list of reaches that you keep
      keep_reaches <- c(keep_reaches, reach_id_down)
      # Track reaches that are the next level upstream
      track_next_reach_id <- c(track_next_reach_id, reach_id_down)
    }
    # next level of reaches upstream
    next_reach_id <- track_next_reach_id
    
    #Add the reach you are keeping in this iteration to the total distance
    d <- d + reach_distance
    # Is it minimum dist upstream and minimum dist past lake?
    if((d > distance_downstream)){break}   
    
  }
  total_downstream_distance <- d
  downstream_reaches <- keep_reaches
  
  dist_df = data.frame(Assgn_dam = c(dam_number), 
                       ds_dist = c(total_downstream_distance),
                       up_dist = c(total_upstream_distance))
  write.csv(dist_df,paste0('Data/Data_Outputs/Total_Dam_Dists/', as.character(dam_number), ".csv" ))

  all_reaches <- c(upstream_reaches, downstream_reaches)
  reach_df <- as.data.frame(all_reaches)
  reach_df$Assgn_dam <- dam_number
  return(reach_df)
}

###############################################################################################################
## Run the Function for Grabbing Reaches 
## For Grabbing Reaches: Function needs -->  
## grab_reaches(river, dam_number, starting_reach,distance_upstream, distance_downstream, distance_past_lake) 
## distances give in meters
###############################################################################################################

# Do this in a for Loop to get each dam's segments 
full_reach_df <- data.frame()
for (i in 1:nrow(dams)){
  print(i)
  grab <- grab_reaches(all_centerlines,dams[i,]$grod_id,dams[i,]$closest_reach , 50000, 50000, 20000)
  grab_df <- grab
  full_reach_df <- rbind(full_reach_df,grab_df)
  }

# Drop the NA values
full_reach_df_nona <- na.omit(full_reach_df)

#Fix column formatting 
full_reach_df_nona$all_reaches <- as.double(full_reach_df_nona$all_reaches)
full_reach_df_nona <- full_reach_df_nona %>%
  rename(reach_id= all_reaches)

##########################################################
# Get the Obstructed Centerlines
Obstructed_Reaches <- left_join(full_reach_df_nona, all_centerlines, by = 'reach_id')

#############################################################
# Export/Save Data ## Obstructed Centerlines to Shapefile ##
############################################################
st_write(Obstructed_Reaches, "Insert_Output_File_Path/Obstructed_Reaches.shp",driver="ESRI Shapefile", append=FALSE) # Update this file path

#############################################################
## Get the Affected Nodes ##
############################################################

# Pull the Nodes from Affected Reaches 
Obstructed_Nodes <- data.frame()
for(i in 1:nrow(full_reach_df_nona)){
  select_nodes <- filter(all_nodes,all_nodes$reach_id == full_reach_df_nona$reach_id[i])
  select_reach <- filter(full_reach_df_nona,full_reach_df_nona$Assgn_dam == full_reach_df_nona$Assgn_dam[i])
  join_select <- left_join(select_nodes,select_reach, by = 'reach_id')
  join_select_df <- join_select
  Obstructed_Nodes <- rbind(Obstructed_Nodes,join_select_df)
}

## Preview Obstructions (without linear referencing) -- view shapefile
#st_write(Obstructed_Nodes, "Insert_File_Path/Obs_Nodes_NoLinRef.shp",driver="ESRI Shapefile", append=FALSE) # Update path here 

#####################################################
####################################################
# Linear Reference Nodes to Dams
###################################################
# Find the nodes nearest to the dam 
# Select nodes that are in the nearest reaches 
Dam_Reach_Nodes <- filter(Obstructed_Nodes, reach_id %in% dams$closest_reach)

# Set up parallelization 
cl <- makeCluster(8) # Note the number of cores used
registerDoParallel(cl) # only run if new session

# Find Segments Nearest to the Dams
closest_node <- foreach(i= 1:nrow(dams),.packages=c('sf'), .combine = 'c') %dopar% {
  assoc_node <-  Dam_Reach_Nodes[which.min(
    st_distance(Dam_Reach_Nodes, dams[i,])),]$node_id
  
  return(assoc_node)
}

dams$closest_node <- closest_node

# Run when it is done to stop the parallel loop
stopCluster(cl)


# Create Dam Column for Dam Flag and Dam Distance in Nodes
Obstructed_Nodes <- Obstructed_Nodes %>%
  add_column(Dam_Flag = NA,
             Dam_Dist = NA)

# Add Flag for Dams
Obstructed_Nodes$Dam_Flag[Obstructed_Nodes$node_id %in%closest_node] <- 'Dam'

## Preview Obstructions (Dams Assigned) -- view shapefile
#st_write(Obstructed_Nodes, "Insert_File_Path_Here/Obs_Nodes_DamAsgn.shp",driver="ESRI Shapefile", append=FALSE) # update file path here

#############################################################
### The Following Process Takes a While to Run -- ###
############################################################

## Work with a copy 
Copy_Obstructed_Nodes <- Obstructed_Nodes

for(i in 1:nrow(dams)){
  Copy_Obstructed_Nodes <- Copy_Obstructed_Nodes %>%
    mutate(Dam_Flag = case_when((Copy_Obstructed_Nodes$Assgn_dam == dams$grod_id[i] 
                                 & Copy_Obstructed_Nodes$node_id == dams$closest_node[i])~ "Main Dam", TRUE ~ Dam_Flag))
}

###############################################
### Linear Reference the nodes to the dams ###
##############################################
# Basically: Work through the list of dams, pull the nodes based on their assigned main dam
# Then within the subsections,use the outlet distance where the dam flag is "main dam" and difference all the outlet values
# These differences will then be appended to the "Dam_Dist" column in Obstructed_Nodes_LinRef
############################################

# Pull the Nodes from Affected Reaches 
Obstructed_Nodes_LinRef <- data.frame()
for(i in 1:nrow(dams)){
  select_nodes <- filter(Copy_Obstructed_Nodes,Copy_Obstructed_Nodes$Assgn_dam == dams$grod_id[i])
  select_dam_node <- filter(select_nodes,select_nodes$node_id == dams$closest_node[i] & select_nodes$Dam_Flag == "Main Dam")
  Obs_N_Dams <- st_drop_geometry(select_dam_node) %>%
    select(c('Assgn_dam','dist_out')) %>%
    rename(dam_to_out = dist_out)
  Obs_Nodes_Join <- left_join(select_nodes, Obs_N_Dams, by = 'Assgn_dam') 
  Obs_Nodes_Join$Dam_Dist <- Obs_Nodes_Join$dam_to_out - Obs_Nodes_Join$dist_out
  join_select_df <- Obs_Nodes_Join
  Obstructed_Nodes_LinRef <- rbind(Obstructed_Nodes_LinRef,join_select_df)
}

###################################################
# Export/Save Data 
###################################################
st_write(Obstructed_Nodes_LinRef, "Insert_File_Path_Here/Obs_Nodes_LinRef.shp",driver="ESRI Shapefile", append=FALSE) # Update File Path Here

# Clean Up File For Export
Obs_Nodes_Clean <- Obstructed_Nodes_LinRef[,c('x','y','node_id','reach_id','lakeflag','width','Assgn_dam',"Dam_Flag", 'Dam_Dist')]

# Save Shapefile of Nodes
st_write(Obs_Nodes_Clean, "Insert_File_Path_Here/Obstructed_Nodes.shp", append=FALSE) # Update File Path Here

## Save Dams to Shapefile
st_write(dams, "Insert_File_Path_Here/Dams_Investigated.shp", append=FALSE) # Update File Path Here 

#######################################################################################
## The exported data are then pulled into ArcGIS for manual cleaning and assessments
## The cleaned outputs are used to extract data from GEE in future python scripts
