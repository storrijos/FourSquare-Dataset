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
do_neighbors=TRUE
do_knn=FALSE
do_eval=FALSE
do_posteval=FALSE

traintest_folder="entradas/Rome"
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
  echo "Processing $filename"
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
patternneigh_folder="pattern_neigh_circle"
for (( index=0; index < ${#filenames_train[*]}; index=index+1))
do
  filename=${filenames_train[$index]}
  echo "Processing $filename"
  training_pre=$traintest_folder"/"${filename}
  training=$traintest_folder"/"${filename}__post
  training_sim=${training}_sim
  ## These take too much time
  #python3 src/Patterns/Convoy/ConvoyTrajectory.py --filename $training --output $patternneigh_folder"/"$filename"__"convoy_3_2_0.1_T.txt --minpoints 3 --lifetime 2 --distance_max 0.1 --partials False &
  ## These take too much time (in Tokyo, not so much in Rome)
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_5000_6000_1.txt --spatial_thresold 5000 --temporal_threshold 6000 --min_neighbors 1 &
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_1000_2000_1.txt --spatial_thresold 1000 --temporal_threshold 2000 --min_neighbors 1 &
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_2000_4000_1.txt --spatial_thresold 2000 --temporal_threshold 4000 --min_neighbors 1 &
  #python3 src/Patterns/ST_DBSCAN/main_stdbscan.py --filename $training --neighbors_classified $patternneigh_folder"/"$filename"__"stdbscan_4000_2000_1.txt --spatial_thresold 4000 --temporal_threshold 2000 --min_neighbors 1 &
  ## Next one takes too much memory
  #python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.2_2_0.2.txt --epsilon 0.2 --mu 2 --delta 0.2 &
  #python3 src/Patterns/Flock/fpFlockOnline.py --filename $training --output $patternneigh_folder"/"$filename"__"flock_0.05_4_3600.txt --epsilon 0.05 --mu 4 --delta 3600 &
  ## Ad hoc
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_3600.txt --delta 3600
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_7200.txt --delta 7200
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_10800.txt --delta 10800
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_14400.txt --delta 14400
  #python3 src/Patterns/Greedy/greedy_approach.py --filename $training_pre --output $patternneigh_folder"/"$filename"__"adhoc_28800.txt --delta 28800
  ## New ones based on similarity
  #python3 src/Patterns/TrajectorySimilarity/trajectory_similarity.py --dataset $training_sim --output_file $patternneigh_folder"/"$filename"__"trajsim_haus.txt --function "hausdorff" --k 1000000 --threads 1
  #python3 src/Patterns/TrajectorySimilarity/trajectory_similarity.py --dataset $training_sim --output_file $patternneigh_folder"/"$filename"__"trajsim_dtw.txt --function "dtw" --k 1000000 --threads 1
  ##Convoy Partials
  #python3 src/Patterns/Convoy/convoy_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"adhoc_3600.txt --output $patternneigh_folder"/"$filename"__"convoy_partials_3_2_0.1_T.txt --k 100 --minpoints 3 --lifetime 2 --distance_max 0.1 --partials False &
  ## Flock Partials
  python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"adhoc_3600.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.2_2_0.2.txt --k 100 --epsilon 0.2 --mu 2 --delta 0.2 &
  #python3 src/Patterns/Flock/flock_partial.py --dataset $training --similarity_file $patternneigh_folder"/"$filename"__"adhoc_3600.txt --output $patternneigh_folder"/"$filename"__"flock_partials_0.05_4_3600.txt --k 100 --epsilon 0.05 --mu 4 --delta 3600 &
  # wait
done
wait
fi

if [ "$do_knn" = TRUE ] ; then
use_tfg=FALSE
use_ranksys=TRUE

if [ "$use_tfg" = TRUE ] ; then
# obtain neighbors
patternneigh_folder="pattern_neigh_circle"
rec_folder="rec_circle"
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
    python3 src_rec/Recommender/knn.py --train_file $training_pre --test_file $test_pre --k 50 --neighbors_classified $neigh_file --output_file $rec_folder"/"$filename"__"knn_50__$neigh_name
  done
done
wait
fi

if [ "$use_ranksys" = TRUE ] ; then
java_command=java
jvm_memory=-Xmx30G
JAR=seqrecs/SequentialRecs.jar
all_neighbours="10 20 40 60 80 100 120 150 200 250 300"
items_recommended=100
rec_strat="T_I" # T_I is train items

# obtain neighbors
patternneigh_folder="pattern_neigh_circle"
# process files for Java project
patterns=$(ls $patternneigh_folder/*.txt)
for pattern_file in $patterns
do
    if [ -f ${pattern_file}"__tab" ] ; then
	echo "File ${pattern_file} already processed. Ignoring"
    else
	# needed (only once)
    	awk 'BEGIN{FS=" "}{print $1"\t"$2"\t"$3}' $pattern_file > ${pattern_file}"__tab"
    fi
done
#
rec_folder="rec_circle"
for (( index=0; index < ${#filenames_train[*]}; index=index+1))
do
  # training file
  filename=${filenames_train[$index]}
  echo "Processing $filename"
  training_pre=$traintest_folder"/"${filename}
  neigh_files=$(ls $patternneigh_folder"/"$filename"__"*"__tab")
  # test file
  filename=${filenames_test[$index]}
  echo "with $filename"
  test_pre=$traintest_folder"/"${filename}
  for neigh_file in $neigh_files
  do
    neigh_name=$(basename -- "$neigh_file")

    for neighbours in $all_neighbours
    do
        output_rec_file=$rec_folder"/"$filename"__"ubknn_"$neighbours"__$neigh_name
        train_file=$training_pre
        test_file=$test_pre
        $java_command $jvm_memory -jar $JAR -o ranksysTolc4recsysLoadingUBSimFile -trf $train_file -tsf $test_file -cIndex false -nI $items_recommended -n $neighbours -orf $output_rec_file -sf $neigh_file -recStrat $rec_strat
    done
    # end neighbours
  done
  # end neigh_files
done
# end training files
fi

fi

if [ "$do_eval" = TRUE ] ; then
use_basic_eval=FALSE

if [ "$use_basic_eval" = FALSE ] ; then
java_command=java
jvm_memory=-Xmx30G
JAR=seqrecs/SequentialRecommendersPopEvAUC.jar

rec_folder="rec_circle"
eval_folder="eval_circle"

cutoffs="5,10,20"
evthreshold=1

number_bins=19
user_features="L T B"

for (( index=0; index < ${#filenames_train[*]}; index=index+1))
do
  # training file
  filename=${filenames_train[$index]}
  echo "Processing $filename"
  training_pre=$traintest_folder"/"${filename}
  # test file
  filename=${filenames_test[$index]}
  echo "with $filename"
  rec_files=$(ls $rec_folder"/"$filename"__"*)
  test_pre=$traintest_folder"/"${filename}
  filename=${filenames_features[$index]}
  feature_file=$traintest_folder"/"${filename}
  filename=${filenames_coord[$index]}
  coord_file=$traintest_folder"/"${filename}
  filename=${filenames_userfeature[$index]}
  userfeature_file=$traintest_folder"/"${filename}
  for rec_file in $rec_files
  do
      rec_filename=$(basename -- "$rec_file")
      ## normal
      output_eval_file=$eval_folder"/eval_std_"$rec_filename
      train_file=$training_pre
      test_file=$test_pre
      $java_command $jvmMemory -jar $JAR -o ranksysNonAccuracyMetricsEvaluation -trf $train_file -tsf $test_file -rf $rec_file -ff $feature_file -thr $evthreshold -rc $cutoffs -orf $output_eval_file -onlyAcc false -lcsEv true -compDistances true -coordFile $coord_file -popEv true -numberBins $number_bins
      ## per user feature
      for user_feature in $user_features
      do
        output_eval_file=$eval_folder"/eval_"$user_feature"_"$rec_filename
        train_file=$training_pre
        test_file=$test_pre
        $java_command $jvmMemory -jar $JAR -o ranksysNonAccuracyMetricsEvaluation -trf $train_file -tsf $test_file -rf $rec_file -ff $feature_file -thr $evthreshold -rc $cutoffs -orf $output_eval_file -onlyAcc false -lcsEv true -compDistances true -coordFile $coord_file -popEv true -numberBins $number_bins -compUF true -uff $userfeature_file -ufs $user_feature
      done
  done
  # end rec_files
done
# end training files
else # end use_basic_eval=FALSE
  java_command=java
  jvm_memory=-Xmx30G
  JAR=seqrecs/SequentialRecs.jar

  rec_folder="rec_circle"
  eval_folder="eval_circle"

  cutoffs="5,10,20"
  evthreshold=1

  for (( index=0; index < ${#filenames_train[*]}; index=index+1))
  do
    # training file
    filename=${filenames_train[$index]}
    echo "Processing $filename"
    training_pre=$traintest_folder"/"${filename}
    # test file
    filename=${filenames_test[$index]}
    echo "with $filename"
    rec_files=$(ls $rec_folder"/"$filename"__"*)
    test_pre=$traintest_folder"/"${filename}
    filename=${filenames_features[$index]}
    feature_file=$traintest_folder"/"${filename}
    for rec_file in $rec_files
    do
        rec_filename=$(basename -- "$rec_file")
        output_eval_file=$eval_folder"/eval_"$rec_filename
        train_file=$training_pre
        test_file=$test_pre
        $java_command $jvm_memory -jar $JAR -o ranksysNonAccuracyMetricsEvaluation -trf $train_file -tsf $test_file -rf $rec_file -ff $feature_file -thr $evthreshold -rc $cutoffs -orf $output_eval_file -onlyAcc false
    done
    # end rec_files
  done
  # end training files
fi # end use_basic_eval=TRUE
fi

if [ "$do_posteval" = TRUE ] ; then
eval_folder="eval_circle"
evthreshold=1
summary_file="summary_circle"
rm -f $summary_file

for (( index=0; index < ${#filenames_train[*]}; index=index+1))
do
  # training file
  filename=${filenames_train[$index]}
  echo "Processing $filename"
  training_pre=$traintest_folder"/"${filename}
  # test file
  filename=${filenames_test[$index]}
  echo "with $filename"
  eval_files=$(echo $eval_folder"/eval_*_"$filename"__*")
  for eval_file in $eval_files
  do
      eval_filename=$(basename -- "$eval_file")
      awk -v FILE=$summary_file -v TH=$evthreshold -v RNAME=$eval_filename -v DATASET=$filename 'BEGIN { RS = "\n" } ; { print FILENAME"\t"RNAME"\t"DATASET"\t"TH"\t"$0 >> FILE }' $eval_file
  done
  # end rec_files
done
# end training files
fi
