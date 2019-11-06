""" This module provides a learner exploiting different reliabilities of challenges
    evaluated several times on an XOR Arbiter PUF. It is based on the work from G. T.
    Becker in "The Gap Between Promise and Reality: On the Insecurity of XOR Arbiter
    PUFs". The learning algorithm applies Covariance Matrix Adaptation Evolution
    Strategies from N. Hansen in "The CMA Evolution Strategy: A Comparing Review".
"""
#import cma
from cma import CMA
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp

from scipy.stats import pearsonr, mode

from pypuf.tools import approx_dist, transform_challenge_11_to_01,transform_challenge_01_to_11
from pypuf.bipoly import BiPoly
from pypuf.learner.base import Learner
from pypuf.simulation.arbiter_based.ltfarray import LTFArray




# ==================== Reliability for PUF and MODEL ==================== #

def reliabilities_PUF(response_bits):
    """
        Computes 'Reliabilities' according to [Becker].
        :param response_bits: Array with shape [num_challenges, num_measurements]
    """
    # Convert to 0/1 from 1/-1
    response_bits = np.array(response_bits, dtype=np.int8)
    if (-1 in response_bits):
        response_bits = transform_challenge_11_to_01(response_bits)
    return np.abs(response_bits.shape[1]/2 - np.sum(response_bits, axis=1))

def reliabilities_MODEL(delay_diffs, EPSILON=3):
    """
        Computes 'Hypothical Reliabilities' according to [Becker].
        :param delay_diffs: Array with shape [num_challenges]
    """
    res = tf.math.greater(tf.transpose(tf.abs(delay_diffs)), EPSILON)
    return res

def tf_pearsonr(x, y):
    centered_x = x - tf.reduce_mean(x, axis=0)
    centered_y = y - tf.reduce_mean(y) #can be precomp
    cov_xy = tf.tensordot(centered_y, centered_x, axes=1)
    auto_cov = tf.sqrt(tf.reduce_sum(centered_x**2, axis=0) * tf.reduce_sum(centered_y**2))
    corr = cov_xy / auto_cov
    return corr

# ============================ Learner class ============================ #

class ReliabilityBasedCMAES(Learner):
    """
        This class implements the CMAES algorithm to learn a model of a XOR-Arbiter PUF.
        This process uses information about the (un-)reliability of repeated challenges.

        If a response bit is unstable for a given challenge, it is likely that the delay
        difference is is close to zero: delta_diff < CONST_EPSILON
    """

    def __init__(self, training_set, k, n, transform, combiner,
                 pop_size, abort_delta, abort_iter, random_seed, logger):
        """Initialize a Reliability based CMAES Learner for the specified LTF array

        :param training_set:    Training set, a data structure containing repeated
                                challenge response pairs.
        :param k:               Width, the number of parallel LTFs in the LTF array
        :param n:               Length, the number stages within the LTF array.
        :param transform:       Transformation function, the function that modifies the
                                input within the LTF array.
        :param combiner:        Combiner, the function that combines particular chains'
                                outputs within the LTF array.
        :param pop_size:        Population size, the number of sampled points of every
                                CMAES iteration.
        :param abort_delta:     Stagnation value, the maximal delta within *abort_iter*
                                iterations before early stopped.
        :param abort_iter:      Stagnation iteration limit, the window size of iterations
                                where *abort_delta* is calculated.
        :param random_seed:     PRNG seed used by the CMAES algorithm for sampling
                                solution points.
        :param logger:          Logger, the instance that logs detailed information every
                                learning iteration.
        """
        self.training_set = training_set
        self.k = k
        self.n = n
        self.transform = transform
        self.combiner = combiner
        self.pop_size = pop_size
        self.abort_delta = abort_delta
        self.abort_iter = abort_iter
        self.prng = np.random.RandomState(random_seed)
        self.chains_learned = np.zeros((self.k, self.n))
        self.num_iterations = 0
        self.stops = ''
        self.num_abortions = 0
        self.num_learned = 0
        self.logger = logger

        # Compute PUF Reliabilities. These remain static throughout the optimization.
        self.puf_reliabilities = reliabilities_PUF(self.training_set.responses)

        # Linearize challenges for faster LTF computation (shape=(N,k,n))
        self.linearized_challenges = self.transform(self.training_set.challenges,
                                                    k=self.k)


    def print_accs(self, es):
        w = es.best.x[:-1]
        #print(es.fit.hist)
        a = [
            1 - approx_dist(
                LTFArray(v[:self.n].reshape(1,self.n), self.transform, self.combiner),
                LTFArray(w[:self.n].reshape(1,self.n) ,self.transform, self.combiner),
                10000,
                np.random.RandomState(12345)
            )
            for v in self.training_set.instance.weight_array
            ]
        print(np.array(a), self.objective(es.best.x))

    def is_iteration_stagnated(self, es):
        """
            Abort criteria. This function is called after each optimization iteration.
            When True is returned, the optimization is stopped and the current state is
            returned.
        """
        fun_history = es.fit.hist[-self.abort_iter:]
        if (len(es.fit.hist) < 100):
            return False
        if (np.abs(max(fun_history) - min(fun_history)) < self.abort_delta):
            return True
        return False

    def objective(self, state):
        """
            Objective to be minimized. Therefore we use the 'Pearson Correlation
            Coefficient' of the model reliabilities and puf reliabilities.
        """
        # Weights and epsilon have the first dim as number of population
        weights = state[:, :self.n]
        epsilon = state[:, -1]
        delay_diffs = tf.linalg.matmul(weights, self.current_challenges.T)
        model_reliabilities = reliabilities_MODEL(delay_diffs, EPSILON=epsilon)

        # Calculate pearson coefficient
        x = np.array(model_reliabilities, dtype=np.float64)
        y = np.array(self.puf_reliabilities, dtype=np.float64)
        corr = tf_pearsonr(x, y)

        return tf.abs(1 - corr)

    def test_model(self, model):
        """
            Perform a test using the training set and return the accuracy.
            This function is used at the end of the training phase to determine,
            whether the chains need to be flipped.
        """
        # Since responses can be noisy, we perform majority vote on response bits
        Y_true = mode(self.training_set.responses, axis=1)[0].T
        Y_test = model.eval(self.training_set.challenges)
        return np.mean(Y_true == Y_test)

    def learn(self):
        """
            Start learning and return optimized LTFArray.
        """
        pool = []
        # For k chains, learn a model and add to pool if "it is new"
        n_chain = 0
        while n_chain < self.k:
            print("Attempting to learn chain", n_chain)
            self.current_challenges = np.array(
                    self.linearized_challenges[:, n_chain, :],
                    dtype=np.float64) # tensorflow needs floats

            cma_options = {
                'seed': self.prng.randint(2 ** 32),
                'termination_callback': self.is_iteration_stagnated
            }
            init_state = list(self.prng.normal(0, 1, size=self.n)) + [2]
            init_state = np.array(init_state) # weights = normal_dist; epsilon = 2
            cma = CMA(
                    initial_solution=init_state,
                    initial_step_size=1.0,
                    fitness_function=self.objective,
                    termination_no_effect=5e-3)
            print("Pop size", cma.population_size)
            w, _ = cma.search()
            w = w[:-1]
            # Flip chain for comparison; invariant of reliability
            w = -w if w[0] < 0 else w

            # Check if learned model (w) is a 'new' chain (not correlated to other chains)
            for v in pool:
                if (tf.abs(pearsonr(w, v)[0]) > 0.5):
                    break
            else:
                pool.append(w)
                n_chain += 1

        # Test LTFArray. If accuracy < 0.5, we flip the first chain, hence the output bits
        model = LTFArray(np.array(pool), self.transform, self.combiner)
        if self.test_model(model) < 0.5:
            pool[0] = - pool[0]
            model = LTFArray(np.array(pool), self.transform, self.combiner)

        return model
