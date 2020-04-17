import heapq

from surprise import PredictionImpossible
from surprise import Prediction
from surprise.prediction_algorithms.optimize_baselines import baseline_sgd, baseline_als
from surprise import similarities
import numpy as np
import os, sys
curent_file_abs_path = os.path.abspath(__file__)
current_dir = os.path.dirname(curent_file_abs_path) + "/../Processing"
carpeta2_abs_path = os.path.abspath(current_dir)
sys.path.insert(0,carpeta2_abs_path)
from pre_process import ProcessData

class AlgoBase(object):
    """Abstract class where is defined the basic behavior of a prediction
    algorithm.
    Keyword Args:
        baseline_options(dict, optional): If the algorithm needs to compute a
            baseline estimate, the ``baseline_options`` parameter is used to
            configure how they are computed. See
            :ref:`baseline_estimates_configuration` for usage.
    """

    def __init__(self, **kwargs):

        self.bsl_options = kwargs.get('bsl_options', {})
        self.sim_options = kwargs.get('sim_options', {})
        if 'user_based' not in self.sim_options:
            self.sim_options['user_based'] = True

    def fit_custom(self, trainset, neighbours_dataset):
        self.fit(trainset)
        self.neighbours_dataset = neighbours_dataset


    def fit(self, trainset):
        """Train an algorithm on a given training set.
        This method is called by every derived class as the first basic step
        for training an algorithm. It basically just initializes some internal
        structures and set the self.trainset attribute.
        Args:
            trainset(:obj:`Trainset <surprise.Trainset>`) : A training
                set, as returned by the :meth:`folds
                <surprise.dataset.Dataset.folds>` method.
        Returns:
            self
        """

        self.trainset = trainset

        # (re) Initialise baselines
        self.bu = self.bi = None

        return self

    def predict(self, uid, iid, r_ui=None, clip=True, verbose=False):
        """Compute the rating prediction for given user and item.
        The ``predict`` method converts raw ids to inner ids and then calls the
        ``estimate`` method which is defined in every derived class. If the
        prediction is impossible (e.g. because the user and/or the item is
        unkown), the prediction is set according to :meth:`default_prediction()
        <surprise.prediction_algorithms.algo_base.AlgoBase.default_prediction>`.
        Args:
            uid: (Raw) id of the user. See :ref:`this note<raw_inner_note>`.
            iid: (Raw) id of the item. See :ref:`this note<raw_inner_note>`.
            r_ui(float): The true rating :math:`r_{ui}`. Optional, default is
                ``None``.
            clip(bool): Whether to clip the estimation into the rating scale.
                For example, if :math:`\\hat{r}_{ui}` is :math:`5.5` while the
                rating scale is :math:`[1, 5]`, then :math:`\\hat{r}_{ui}` is
                set to :math:`5`. Same goes if :math:`\\hat{r}_{ui} < 1`.
                Default is ``True``.
            verbose(bool): Whether to print details of the prediction.  Default
                is False.
        Returns:
            A :obj:`Prediction\
            <surprise.prediction_algorithms.predictions.Prediction>` object
            containing:
            - The (raw) user id ``uid``.
            - The (raw) item id ``iid``.
            - The true rating ``r_ui`` (:math:`\\hat{r}_{ui}`).
            - The estimated rating (:math:`\\hat{r}_{ui}`).
            - Some additional details about the prediction that might be useful
              for later analysis.
        """
        # Convert raw ids to inner ids
        try:
            iuid = self.trainset.to_inner_uid(uid)
        except ValueError:
            iuid = 'UKN__' + str(uid)
        try:
            #print(iid)
            iiid = self.trainset.to_inner_iid(iid)
        except ValueError:
            iiid = 'UKN__' + str(iid)

        details = {}
        try:

            #print('TRAINSET')
            #print('####')

            #print('ID:' + str(iuid) + 'ITEM_ID ' + str(iiid))
            #print('ID:' + str(iuid) + 'ITEM_ID ' + str(iiid))

            #print('llamo')
            est = self.estimate(iuid, iiid)

            #print('ESTIMACION' + str(est))

            # If the details dict was also returned
            if isinstance(est, tuple):
                est, details = est

            details['was_impossible'] = False

        except PredictionImpossible as e:
            est = self.default_prediction()
            details['was_impossible'] = True
            details['reason'] = str(e)

        # clip estimate into [lower_bound, higher_bound]
        if clip:
            lower_bound, higher_bound = self.trainset.rating_scale
            est = min(higher_bound, est)
            est = max(lower_bound, est)

        pred = Prediction(uid, iid, r_ui, est, details)

        if verbose:
            print(pred)

        return pred

    def default_prediction(self):
        '''Used when the ``PredictionImpossible`` exception is raised during a
        call to :meth:`predict()
        <surprise.prediction_algorithms.algo_base.AlgoBase.predict>`. By
        default, return the global mean of all ratings (can be overridden in
        child classes).
        Returns:
            (float): The mean of all ratings in the trainset.
        '''

        return self.trainset.global_mean

    def test(self, not_seen, testset, verbose=False):
        """Test the algorithm on given testset, i.e. estimate all the ratings
        in the given testset.
        Args:
            testset: A test set, as returned by a :ref:`cross-validation
                itertor<use_cross_validation_iterators>` or by the
                :meth:`build_testset() <surprise.Trainset.build_testset>`
                method.
            verbose(bool): Whether to print details for each predictions.
                Default is False.
        Returns:
            A list of :class:`Prediction\
            <surprise.prediction_algorithms.predictions.Prediction>` objects
            that contains all the estimated ratings.
        """

        # The ratings are translated back to their original scale.

        predictions = [self.predict(uid,
                                    iid,
                                    r_ui_trans,
                                    verbose=verbose)
                       for (uid, iid, r_ui_trans) in testset]

        predictions2 = [self.predict(uid, iid, 0.0, verbose=verbose) for (uid, iid) in not_seen]

        return predictions + predictions2

    def compute_baselines(self):
        """Compute users and items baselines.
        The way baselines are computed depends on the ``bsl_options`` parameter
        passed at the creation of the algorithm (see
        :ref:`baseline_estimates_configuration`).
        This method is only relevant for algorithms using :func:`Pearson
        baseline similarty<surprise.similarities.pearson_baseline>` or the
        :class:`BaselineOnly
        <surprise.prediction_algorithms.baseline_only.BaselineOnly>` algorithm.
        Returns:
            A tuple ``(bu, bi)``, which are users and items baselines."""

        # Firt of, if this method has already been called before on the same
        # trainset, then just return. Indeed, compute_baselines may be called
        # more than one time, for example when a similarity metric (e.g.
        # pearson_baseline) uses baseline estimates.
        if self.bu is not None:
            return self.bu, self.bi

        method = dict(als=baseline_als,
                      sgd=baseline_sgd)

        method_name = self.bsl_options.get('method', 'als')

        try:
            self.bu, self.bi = method[method_name](self)
            return self.bu, self.bi
        except KeyError:
            raise ValueError('Invalid method ' + method_name +
                             ' for baseline computation.' +
                             ' Available methods are als and sgd.')

    def compute_similarities(self):
        """Build the similarity matrix.
        The way the similarity matrix is computed depends on the
        ``sim_options`` parameter passed at the creation of the algorithm (see
        :ref:`similarity_measures_configuration`).
        This method is only relevant for algorithms using a similarity measure,
        such as the :ref:`k-NN algorithms <pred_package_knn_inpired>`.
        Returns:
            The similarity matrix."""

        construction_func = {'cosine': similarities.cosine,
                             'msd': similarities.msd,
                             'pearson': similarities.pearson,
                             'pearson_baseline': similarities.pearson_baseline}

        if self.sim_options['user_based']:
            n_x, yr = self.trainset.n_users, self.trainset.ir
        else:
            n_x, yr = self.trainset.n_items, self.trainset.ur

        min_support = self.sim_options.get('min_support', 1)

        args = [n_x, yr, min_support]

        name = self.sim_options.get('name', 'msd').lower()
        if name == 'pearson_baseline':
            shrinkage = self.sim_options.get('shrinkage', 100)
            bu, bi = self.compute_baselines()
            if self.sim_options['user_based']:
                bx, by = bu, bi
            else:
                bx, by = bi, bu

            args += [self.trainset.global_mean, bx, by, shrinkage]

        try:
            sim = construction_func[name](*args)
            return sim
        except KeyError:
            raise NameError('Wrong sim name ' + name + '. Allowed values ' +
                            'are ' + ', '.join(construction_func.keys()) + '.')

    def get_neighbors_flock(self, item, k):

        if self.neighbours_dataset is None:
            return []
        else:
            neighbors = self.neighbours_dataset[self.neighbours_dataset['user_id'] == item]
            neighbors_dict = dict(zip(neighbors.neighbour_id.values, neighbors.weight.values))
            neighbors_id_result_clean = []
            neighbors_weight_result_clean = []

            for elem, weight in neighbors_dict.items():
                try:
                    self.trainset.to_inner_uid(elem)
                    neighbors_id_result_clean.append(elem)
                    neighbors_weight_result_clean.append(weight)
                except ValueError:
                    return
                    #print(elem)

            result_dict = dict(zip(neighbors_id_result_clean[:k], neighbors_weight_result_clean[:k]))
            return result_dict

    def get_neighbors(self, iid, k):
        """Return the ``k`` nearest neighbors of ``iid``, which is the inner id
        of a user or an item, depending on the ``user_based`` field of
        ``sim_options`` (see :ref:`similarity_measures_configuration`).
        As the similarities are computed on the basis of a similarity measure,
        this method is only relevant for algorithms using a similarity measure,
        such as the :ref:`k-NN algorithms <pred_package_knn_inpired>`.
        For a usage example, see the :ref:`FAQ <get_k_nearest_neighbors>`.
        Args:
            iid(int): The (inner) id of the user (or item) for which we want
                the nearest neighbors. See :ref:`this note<raw_inner_note>`.
            k(int): The number of neighbors to retrieve.
        Returns:
            The list of the ``k`` (inner) ids of the closest users (or items)
            to ``iid``.
        """

        if self.sim_options['user_based']:
            all_instances = self.trainset.all_users
        else:
            all_instances = self.trainset.all_items

        others = [(x, self.sim[iid, x]) for x in all_instances() if x != iid]
        others.sort(key=lambda tple: tple[1], reverse=True)
        k_nearest_neighbors = [j for (j, _) in others[:k]]

        return self.get_neighbors_flock(iid, k)
        #return k_nearest_neighbors

class SymmetricAlgo(AlgoBase):
    """This is an abstract class aimed to ease the use of symmetric algorithms.
    A symmetric algorithm is an algorithm that can can be based on users or on
    items indifferently, e.g. all the algorithms in this module.
    When the algo is user-based x denotes a user and y an item. Else, it's
    reversed.
    """

    def __init__(self, sim_options={}, verbose=False, **kwargs):

        AlgoBase.__init__(self, sim_options=sim_options, **kwargs)
        self.verbose = verbose

    def fit(self, trainset):

        AlgoBase.fit(self, trainset)

        ub = self.sim_options['user_based']
        self.n_x = self.trainset.n_users if ub else self.trainset.n_items
        self.n_y = self.trainset.n_items if ub else self.trainset.n_users
        self.xr = self.trainset.ur if ub else self.trainset.ir
        self.yr = self.trainset.ir if ub else self.trainset.ur

        return self

    def switch(self, u_stuff, i_stuff):
        """Return x_stuff and y_stuff depending on the user_based field."""

        if self.sim_options['user_based']:
            return u_stuff, i_stuff
        else:
            return i_stuff, u_stuff

class KNNCustom(SymmetricAlgo):
    def __init__(self, k=40, min_k=1, sim_options={}, verbose=True, **kwargs):

        SymmetricAlgo.__init__(self, sim_options=sim_options, verbose=verbose,
                               **kwargs)
        self.k = k
        self.min_k = min_k

    def fit(self, trainset):

        SymmetricAlgo.fit(self, trainset)
        self.sim = self.compute_similarities()

        return self

    def estimate(self, u, i):

        if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
            raise PredictionImpossible('User and/or item is unkown.')

        x, y = self.switch(u, i)

        #self.yr = self.trainset.ir if ub else self.trainset.ur

        #neighbors = [(self.sim[x, x2], r) for (x2, r) in self.yr[y]]
        k_neighbors = self.get_neighbors_flock(self.trainset.to_raw_uid(u), self.k)
        #print('USER: ' + str(self.trainset.to_raw_uid(u)) + 'item' + str(y))
        #print(k_neighbors)
        #print('##')

        # compute weighted average
        sum_sim = sum_ratings = actual_k = 0

        if k_neighbors:
            for (neighbor, sim) in k_neighbors.items():
                #print(self.trainset.ur[self.trainset.to_inner_uid(neighbor)])
                for (item, r) in self.trainset.ur[self.trainset.to_inner_uid(neighbor)]:
                    #print(self.trainset.to_raw_iid(item))
                    #print(self.trainset.to_raw_iid(y))
                    #print('item' + str(item) + 'el_mio' + str(y))
                    if item == y:
                        #print('entra')
                        sum_ratings += r * sim
                        actual_k += 1
                        #print(r)
                        #print(sum_ratings, actual_k)


        if actual_k < self.min_k:
            raise PredictionImpossible('Not enough neighbors.')

        est = sum_ratings

        details = {'actual_k': actual_k}

        return est, details
