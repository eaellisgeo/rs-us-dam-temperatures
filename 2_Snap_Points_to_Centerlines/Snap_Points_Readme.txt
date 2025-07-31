Once the temperatures have been pulled for all of the dams, we need to be able to aggregate the points back to the SWORD centerline points. 

First, we ensure that the SWORD points we are using for the profiles do not include other dams up/downstream. To check for this, 
filter by the dam, look for nodes downstream classified as a dam then cut off the profile. This is repeated for upstream. 
Then once the nodes for aggregating are selected, the distance between each RWC point and it's nearest SWORD node is calculated. The 5 closest
points to each  SWORD node (within 200m) are selected and their average temperature and width are calculated. 

This in is then exported as a CSV for each individual dam. These values will be used for all future analysis. 