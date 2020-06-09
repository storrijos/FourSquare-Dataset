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

: <<'PRE'
# BEFORE:
python3 -m venv venv
source ./venv/bin/activate
pip3 install -e .
PRE

do_process=FALSE
do_neighbors=FALSE
do_knn=FALSE
do_eval=FALSE
do_posteval=FALSE
sim_avg=TRUE

traintest_folder="entradas/Rome10K"
filenames_train=(romeTempTrain.txt)
filenames_coord=(POIS_rome__Coords.txt)
filenames_test=(romeTest.txt)
filenames_features=(rome_Features_Tripbuilder.txt)
filenames_userfeature=(xxx)



if [ "$do_process" = TRUE ] ; then
# preprocess files
for (( index=0; index < ${#filenames_train[*]}; index=index+1))
do
  filename=${filenames_train[$index]}
  echo "Processing $filename"4
  training=$traintest_folder"/"$filename
  coord_filename=${filenames_coord[$index]}
  coord_file=$traintest_folder"/"$coord_filename
  ## maybe next method should have '--method coords' added if run again
  if [ -f ${training}__post ] ; then
    echo "File ${training}__post already exists!"
  else
    python3 src/Processing/pre_process.py --input_file $training --coords_file $coord_file --output_file ${training}__post
  fi
  if [ -f ${training}__post_sim ] ; then
    echo "File ${training}__post_sim already exists!"
  else
    python3 src/Processing/pre_process.py  --method dataset_similarity --input_file ${training}__post --coords_file $coord_file --output_file ${training}__post_sim
  fi
  # now let's process the test set
  filename=${filenames_test[$index]}
  echo "Processing $filename"
  test=$traintest_folder"/"$filename
  coord_filename=${filenames_coord[$index]}
  coord_file=$traintest_folder"/"$coord_filename
  ## maybe next method should have '--method coords' added if run again
  if [ -f ${test}__post ] ; then
    echo "File ${test}__post already exists!"
  else
    python3 src/Processing/pre_process.py --input_file $test --coords_file $coord_file --output_file ${test}__post
  fi
done
fi

if [ "$do_neighbors" = TRUE ] ; then
# obtain neighbors
patternneigh_folder="patterns_neigh_10K_combinaciones"
for (( index=0; index < ${#filenames_train[*]}; index=index+1))
do
  filename=${filenames_train[$index]}
  echo "Processing $filename"
  training_pre=$traintest_folder"/"${filename}
  training=$traintest_folder"/"${filename}__post
  training_sim=${training}_sim
  ## These take too much time

  echo "Convoy Partials"
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_1_2_0.1_T.txt --minpoints 2 --lifetime 2 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_3_2_0.1_T.txt --minpoints 3 --lifetime 2 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_5_2_0.1_T.txt --minpoints 5 --lifetime 2 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_3_5_0.1_T.txt --minpoints 3 --lifetime 5 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_3_10_0.1_T.txt --minpoints 3 --lifetime 10 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_3_5_1_T.txt --minpoints 3 --lifetime 5 --distance_max 1 --partials True

  echo "Convoy"
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_30_5_0.1_no_partials.txt --minpoints 20 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_2_0.01_no_partials.txt --minpoints 2 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_5_2_0.01_no_partials.txt --minpoints 5 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_10_2_0.01_no_partials.txt --minpoints 10 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_20_2_0.01_no_partials.txt --minpoints 20 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_5_0.01_no_partials.txt --minpoints 2 --lifetime 5 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_10_0.01_no_partials.txt --minpoints 2 --lifetime 10 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_20_0.01_no_partials.txt --minpoints 2 --lifetime 20 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_2_100_no_partials.txt --minpoints 2 --lifetime 2 --distance_max 100 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_2_1_no_partials.txt --minpoints 2 --lifetime 2 --distance_max 1 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_2_0.1_no_partials.txt --minpoints 2 --lifetime 2 --distance_max 0.1 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_2_0.01_no_partials.txt --minpoints 2 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_2_0.001_no_partials.txt --minpoints 2 --lifetime 2 --distance_max 0.001 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_2_0.00000001_no_partials.txt --minpoints 2 --lifetime 2 --distance_max 0.00000001 --partials False

  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_5_2_0.01_last_no_partials.txt --minpoints 5 --lifetime 2 --distance_max 0.01 --partials False
  python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_5_2_0.000000000000001_last_no_partials.txt --minpoints 5 --lifetime 2 --distance_max 0.000000000000001 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_2_0.0001_last_no_partials.txt --minpoints 2 --lifetime 2 --distance_max 0.0001 --partials False
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_2_2_0.000001_no_partials.txt --minpoints 2 --lifetime 2 --distance_max 0.000001 --partials False


  ## These take too much time (in Tokyo, not so much in Rome)
  echo "ST-DBSCAN"
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_1000_2000_1_extra.txt --spatial_thresold 1000 --temporal_threshold 2000 --min_neighbors 1 &
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --spatial_thresold 2000 --temporal_threshold 4000 --min_neighbors 1 &
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_4000_2000_1.txt --spatial_thresold 4000 --temporal_threshold 2000 --min_neighbors 1 &
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_5000_6000_1.txt --spatial_thresold 5000 --temporal_threshold 6000 --min_neighbors 1 &
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_5000_6000_5.txt --spatial_thresold 5000 --temporal_threshold 6000 --min_neighbors 5 &
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_5000_6000_10.txt --spatial_thresold 5000 --temporal_threshold 6000 --min_neighbors 10 &
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_5000_6000_20.txt --spatial_thresold 5000 --temporal_threshold 6000 --min_neighbors 20 &


  ## Next one takes too much memory
  echo "Flock"
  #python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.1_2_2.txt --epsilon 0.1 --mu 2 --delta 3 &
  #python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.001_2_2.txt --epsilon 0.001 --mu 2 --delta 3
  #python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_10_2_2.txt --epsilon 10 --mu 2 --delta 2 &
  #REV python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.1_5_2.txt --epsilon 0.1 --mu 5 --delta 2
  #Nada python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.1_10_2.txt --epsilon 0.1 --mu 10 --delta 2
  #python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.1_2_1.txt --epsilon 0.1 --mu 2 --delta 1
  #python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.1_2_10.txt --epsilon 0.1 --mu 2 --delta 10
  # Nada python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.1_2_100.txt --epsilon 0.1 --mu 2 --delta 100

  ## Ad hoc
  echo "Ad-Hoc"
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_3600.txt --delta 3600
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_7200.txt --delta 7200 &
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_10800.txt --delta 10800
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_14400.txt --delta 14400 &
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_28800.txt --delta 28800 &

  echo "Similarity"
  ## New ones based on similarity
  #python3 src/Patterns/TrajectorySimilarity/trajectory_similarity.py --dataset $training_sim --output_file $patternneigh_folder"/"$filename"__"trajsim_haus.txt --function "hausdorff" --k 1000000 --threads 1
  #python3 src/Patterns/TrajectorySimilarity/trajectory_similarity.py --dataset $training_sim --output_file $patternneigh_folder"/"$filename"__"trajsim_dtw.txt --function "dtw" --k 1000000 --threads 1

  echo "Partials"
  ##Convoy Partials
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_1_2_0.1_T.txt --k 100 --minpoints 2 --lifetime 2 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_3_2_0.1_T.txt --k 100 --minpoints 3 --lifetime 2 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_5_2_0.1_T.txt --k 100 --minpoints 5 --lifetime 2 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_10_2_0.1_T.txt --k 100 --minpoints 10 --lifetime 2 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_3_5_0.1_T.txt --k 100 --minpoints 3 --lifetime 5 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_3_10_0.1_T.txt --k 100 --minpoints 3 --lifetime 10 --distance_max 0.1 --partials True
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_3_5_1_T.txt --k 100 --minpoints 3 --lifetime 5 --distance_max 1 --partials True

  ##Convoy Partials no_partials
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_2_0.01_T_no_partial.txt --k 100 --minpoints 2 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_5_2_0.01_T_no_partial.txt --k 100 --minpoints 5 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_10_2_0.01_T_no_partial.txt --k 100 --minpoints 10 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_20_2_0.01_T_no_partial.txt --k 100 --minpoints 20 --lifetime 2 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_5_0.01_T_no_partial.txt --k 100 --minpoints 2 --lifetime 5 --distance_max 0.01 --partials False
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_10_0.01_T_no_partial.txt --k 100 --minpoints 2 --lifetime 10 --distance_max 0.01 --partials False
 # python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_20_0.01_T_no_partial.txt --k 100 --minpoints 2 --lifetime 20 --distance_max 0.01 --partials False
 # python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_2_100_T_no_partial.txt --k 100 --minpoints 2 --lifetime 2 --distance_max 100 --partials False
 # python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_2_1_T_no_partial.txt --k 100 --minpoints 2 --lifetime 2 --distance_max 1 --partials False
 # python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_2_0.1_T_no_partial.txt --k 100 --minpoints 2 --lifetime 2 --distance_max 0.1 --partials False
 # python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_2_0.01_T_no_partial.txt --k 100 --minpoints 2 --lifetime 2 --distance_max 0.01 --partials False
 # python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_2_0.001_T_no_partial.txt --k 100 --minpoints 2 --lifetime 2 --distance_max 0.001 --partials False
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_2_2_0.00000001_T_no_partial.txt --k 100 --minpoints 2 --lifetime 2 --distance_max 0.00000001 --partials False

  ## Flock Partials
  #python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.1_2_2_cleaned.txt --k 100 --epsilon 0.01 --mu 2 --delta 0.2
  #python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.1_2_2_cleaned.txt --k 100 --epsilon 0.1 --mu 2 --delta 2
  #python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"flock_partials_10_2_2_cleaned.txt --k 100 --epsilon 10 --mu 2 --delta 2
  #python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.1_2_2_cleaned.txt --k 100 --epsilon 0.01 --mu 2 --delta 0.2
  #python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.1_5_2.txt --k 100 --epsilon 0.1 --mu 5 --delta 2
  #Nada python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.1_10_2.txt --k 100 --epsilon 0.1 --mu 10 --delta 2
  #python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.1_2_1.txt --k 100 --epsilon 0.1 --mu 2 --delta 1
  #python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.1_2_10_cleaned.txt --k 100 --epsilon 0.1 --mu 2 --delta 10
  #Nada python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.1_2_100.txt --k 100 --epsilon 0.1 --mu 2 --delta 100

done
wait
fi

if [ "$sim_avg" = TRUE ] ; then
  # obtain neighbors
  patternneigh_folder="patterns_neigh_10K_combinaciones"
  echo "Similarity average"
  python3 src/Processing/stats.py --path $patternneigh_folder
fi

if [ "$do_knn" = TRUE ] ; then
use_tfg=TRUE

if [ "$use_tfg" = TRUE ] ; then
all_neighbours="10 20 40 80 160 300"
# obtain neighbors
patternneigh_folder="patterns_neigh_10K_combinaciones"
rec_folder="recs"

echo "Filename,Precision,Recall,RMSE,MAE" >> $rec_folder/$patternneigh_folder"_output_knn.csv"

for (( index=0; index < ${#filenames_train[*]}; index=index+1))
do
  # training file
  filename=${filenames_train[$index]}
  echo "Processing $filename"
  training_pre=$traintest_folder"/"${filename}
  training=$traintest_folder"/"${filename}__post
  neigh_files=$(ls $patternneigh_folder"/"$filename"__"*)
  # test file
  filename=${filenames_test[$index]}
  echo "with $filename"
  test_pre=$traintest_folder"/"${filename}
  test=$traintest_folder"/"${filename}__post
  for neigh_file in $neigh_files
  do
    neigh_name=$(basename -- "$neigh_file")
    for neighbours in $all_neighbours
    do
      val=$(python3 src/Recommender/knn.py --train_file $training_pre --test_file $test_pre --k $neighbours --neighbors_classified $neigh_file --output_file $rec_folder"/"$filename"__"$neighbours"__"$neigh_name)
      echo "KNN_"$neighbours"_"$neigh_file","$val
      echo "KNN_"$neighbours"_"$neigh_file","$val >> $rec_folder/$patternneigh_folder"_output_knn.csv"
    done
  done
done
wait
fi





fi