#!/bin/bash

python3 src/Processing/pre_process.py --input_file entradas/DatosNewYork/US_NewYorkTempTrain.txt --coords_file entradas/DatosNewYork/POIS_Coords_Foursquare.txt --output_file US_NewYork_POIS_Coords_shortCompleto.txt

python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename entradas/Datasets/US_NewYork_POIS_Coords_short.txt --output convoy_neighbors_classified.txt --minpoints 3 --lifetime 2 --distance_max 0.1 --partials True
python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename entradas/Datasets/US_NewYork_POIS_Coords_short_1k.txt --neighbors_classified st_dbscan.txt --spatial_thresold 5000 --temporal_threshold 6000 --min_neighbors 1
python3 src/Patterns/Flock/fpFlockOnline.py --filename entradas/Datasets/US_NewYork_POIS_Coords_short_10k.txt --output flock_output.txt --epsilon 0.2 --mu 2 --delta 0.2

python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified convoy_neighbors_classified.txt
python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified convoy_neighbors_classified.txt --uid 15 --iid 6589

python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified st_dbscan.txt
python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified st_dbscan.txt --uid 15 --iid 6589

python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified flock_output.txt
python3 src/Recommender/knn.py --train_file entradas/Datasets/US_NewYork_POIS_Coords_short.txt --test_file entradas/Datasets/US_NewYork_POIS_Coords_short_test.txt --k 1 --neighbors_classified flock_output.txt --uid 15 --iid 6589


python3 src/Patterns/Greedy/greedy_approach.py --filename entradas/entrada_corta.txt --output greedy.txt  --delta 15552000


