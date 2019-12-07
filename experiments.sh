#!/bin/bash

: <<'END'
python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename entradas/Datasets/US_NewYork_POIS_Coords_short.txt --output convoy_neighbors_classified.txt --minpoints 3 --lifetime 2 --distance_max 0.1 --partials True
python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename entradas/Datasets/US_NewYork_POIS_Coords_short.txt --neighbors_classified st_dbscan.txt --spatial_thresold 5000 --temporal_threshold 6000 --min_neighbors 1
python3 src/Patterns/Flock/fpFlockOnline.py --filename entradas/Datasets/US_NewYork_POIS_Coords_short.txt --output flock_output.txt --epsilon 0.2 --mu 2 --delta 0.2

python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified convoy_neighbors_classified.txt
python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified convoy_neighbors_classified.txt --uid 15 --iid 6589

python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified st_dbscan.txt
python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified st_dbscan.txt --uid 15 --iid 6589

python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified flock_output.txt
python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified flock_output.txt --uid 15 --iid 6589
END

traintest_folder="traintest"
patternneigh_folder="pattern_neigh"

for filename in JP_TokyoTempTrain6months.txt JP_TokyoTempTrainCC80-20.txt JP_TokyoTempTrainFix4-4.txt JP_TokyoTempTrainSessions.txt
do
  # is this format correct? otherwise, we will need to first process each file according to the requirements needed by each pattern method
  training=$traintest_folder"/"$filename
  python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_3_2_0.1_T.txt --minpoints 3 --lifetime 2 --distance_max 0.1 --partials True
  python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_5000_6000_1.txt --spatial_thresold 5000 --temporal_threshold 6000 --min_neighbors 1
  python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.2_2_0.2.txt --epsilon 0.2 --mu 2 --delta 0.2
done
