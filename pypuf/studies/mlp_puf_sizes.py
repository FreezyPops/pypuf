"""
This module describes a study that defines a set of experiments in order to find good hyperparameters and to examine
the quality of Deep Learning based modeling attacks on XOR Arbiter PUFs. Furthermore, some plots are defined to
visualize the experiment's results.
The Deep Learning technique used here is the Optimization technique Adam for a Stochastic Gradient Descent on a Feed-
Forward Neural Network architecture called Multilayer Perceptron (MLP). Implementations of the MLP and Adam are
used from Scikit-Learn and Tensorflow, respectively.
"""

from matplotlib.pyplot import subplots
from matplotlib.ticker import FixedLocator
from numpy.ma import ones, log10
from numpy.random.mtrand import seed
from seaborn import stripplot, lineplot, scatterplot

from pypuf.studies.base import Study
from pypuf.experiments.experiment.mlp_tf import ExperimentMLPTensorflow, Parameters as Parameters_tf
from pypuf.experiments.experiment.mlp_skl import ExperimentMLPScikitLearn, Parameters as Parameters_skl


class MLPPUFSizesStudy(Study):
    """
    Define a set of experiments by combining several sets of hyperparameters.
    """

    TRANSFORMATION = 'id'
    COMBINER = 'xor'
    PREPROCESSING = 'no'
    ACTIVATION = 'relu'
    ITERATION_LIMIT = 100
    LOSS = 'log_loss'
    DOMAINS = (-1, -1)
    PATIENCE = 4
    TOLERANCE = 0.0025
    PENALTY = 0.0002
    BETA_1 = 0.9
    BETA_2 = 0.999
    MAX_NUM_VAL = 10000
    MIN_NUM_VAL = 20
    PRINT_LEARNING = False

    PLOT_ESTIMATORS = []

    SIZES = {
        (32, 1): [1e3, 2e3, 5e3],
        (32, 2): [2e3, 5e3, 10e3],
        (32, 3): [5e3, 10e3, 20e3],
        (64, 1): [2e3, 3e3, 5e3],
        (64, 2): [2e3, 4e3, 8e3],
        (64, 3): [8e3, 15e3, 30e3],
        (128, 1): [2e3, 4e3, 6e3],
        (128, 2): [5e3, 10e3, 20e3],
        (128, 3): [10e3, 20e3, 40e3],
        (256, 1): [2e3, 5e3, 7e3],
        (256, 2): [5e3, 20e3, 40e3],
        (256, 3): [20e3, 50e3, 80e3],
        (512, 1): [2e3, 5e3, 8e3],
        (512, 2): [10e3, 30e3, 50e3],
        (512, 3): [100e3, 300e3, 600e3],
        (1024, 1): [5e3, 8e3, 10e3],
        (1024, 2): [20e3, 50e3, 80e3],
        (1024, 3): [200e3, 500e3, 800e3],
    }

    SAMPLES_PER_POINT = {
        (32, 1): 20,
        (32, 2): 20,
        (32, 3): 20,
        (64, 1): 20,
        (64, 2): 20,
        (64, 3): 20,
        (128, 1): 20,
        (128, 2): 20,
        (128, 3): 20,
        (256, 1): 20,
        (256, 2): 20,
        (256, 3): 20,
        (512, 1): 20,
        (512, 2): 20,
        (512, 3): 20,
        (1024, 1): 20,
        (1024, 2): 20,
        (1024, 3): 20,
    }

    LAYERS = {
        (32, 1): [[2**1, 2**1, 2**1]],
        (32, 2): [[2**2, 2**2, 2**2]],
        (32, 3): [[2**3, 2**3, 2**3]],
        (64, 1): [[2**1, 2**1, 2**1]],
        (64, 2): [[2**2, 2**2, 2**2]],
        (64, 3): [[2**3, 2**3, 2**3]],
        (128, 1): [[2**1, 2**1, 2**1]],
        (128, 2): [[2**2, 2**2, 2**2]],
        (128, 3): [[2**3, 2**3, 2**3]],
        (256, 1): [[2**1, 2**1, 2**1]],
        (256, 2): [[2**2, 2**2, 2**2]],
        (256, 3): [[2**3, 2**3, 2**3]],
        (512, 1): [[2**1, 2**1, 2**1]],
        (512, 2): [[2**2, 2**2, 2**2]],
        (512, 3): [[2**3, 2**3, 2**3]],
        (1024, 1): [[2**1, 2**1, 2**1]],
        (1024, 2): [[2**2, 2**2, 2**2]],
        (1024, 3): [[2**3, 2**3, 2**3]],
    }

    LEARNING_RATES = {
        (32, 1): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (32, 2): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (32, 3): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (64, 1): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (64, 2): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (64, 3): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (128, 1): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (128, 2): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (128, 3): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (256, 1): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (256, 2): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (256, 3): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (512, 1): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (512, 2): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (512, 3): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (1024, 1): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (1024, 2): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
        (1024, 3): [0.0005, 0.00075, 0.001, 0.00125, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.012, 0.014, 0.017, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.1],
    }

    EXPERIMENTS = []

    def experiments(self):
        """
        Generate an experiment for every parameter combination corresponding to the definitions above.
        For each combination of (size, samples_per_point, learning_rate) different random seeds are used.
        """
        domain_in = self.DOMAINS[0]
        domain_out = self.DOMAINS[1]
        for c1, (n, k) in enumerate(self.SIZES.keys()):
            for N in self.SIZES[(n, k)]:
                for c2 in range(self.SAMPLES_PER_POINT[(n, k)]):
                    for c3, learning_rate in enumerate(self.LEARNING_RATES[(n, k)]):
                        cycle = c1 * (self.SAMPLES_PER_POINT[(n, k)] * len(self.LEARNING_RATES[(n, k)])) \
                                + c2 * len(self.LEARNING_RATES[(n, k)]) + c3
                        validation_frac = max(min(N // 20, self.MAX_NUM_VAL), self.MIN_NUM_VAL) / N
                        for layers in self.LAYERS[(n, k)]:
                            self.EXPERIMENTS.append(
                                ExperimentMLPScikitLearn(
                                    progress_log_prefix=None,
                                    parameters=Parameters_skl(
                                        seed_simulation=0x3 + cycle,
                                        seed_challenges=0x1415 + cycle,
                                        seed_model=0x9265 + cycle,
                                        seed_distance=0x3589 + cycle,
                                        n=n,
                                        k=k,
                                        N=int(N),
                                        validation_frac=validation_frac,
                                        transformation=self.TRANSFORMATION,
                                        combiner=self.COMBINER,
                                        preprocessing=self.PREPROCESSING,
                                        layers=layers,
                                        activation=self.ACTIVATION,
                                        domain_in=domain_in,
                                        learning_rate=learning_rate,
                                        penalty=self.PENALTY,
                                        beta_1=self.BETA_1,
                                        beta_2=self.BETA_2,
                                        tolerance=self.TOLERANCE,
                                        patience=self.PATIENCE,
                                        iteration_limit=self.ITERATION_LIMIT,
                                        batch_size=1000 if k < 6 else 10000,
                                        print_learning=self.PRINT_LEARNING,
                                    )
                                )
                            )
                            self.EXPERIMENTS.append(
                                ExperimentMLPTensorflow(
                                    progress_log_prefix=None,
                                    parameters=Parameters_tf(
                                        seed_simulation=0x3 + cycle,
                                        seed_challenges=0x1415 + cycle,
                                        seed_model=0x9265 + cycle,
                                        seed_distance=0x3589 + cycle,
                                        n=n,
                                        k=k,
                                        N=int(N),
                                        validation_frac=validation_frac,
                                        transformation=self.TRANSFORMATION,
                                        combiner=self.COMBINER,
                                        preprocessing=self.PREPROCESSING,
                                        layers=layers,
                                        activation=self.ACTIVATION,
                                        loss=self.LOSS,
                                        domain_in=domain_in,
                                        domain_out=domain_out,
                                        learning_rate=learning_rate,
                                        penalty=self.PENALTY,
                                        beta_1=self.BETA_1,
                                        beta_2=self.BETA_2,
                                        tolerance=self.TOLERANCE,
                                        patience=self.PATIENCE,
                                        iteration_limit=self.ITERATION_LIMIT,
                                        batch_size=1000 if k < 6 else 10000,
                                        print_learning=self.PRINT_LEARNING,
                                    )
                                )
                            )
        return self.EXPERIMENTS

    def plot(self):
        """
        Visualize the quality, process, and runtime of learning by plotting the accuracy, the accuracies of each epoch,
        and the measured time of each experiment, respectively.
        """
        if not self.EXPERIMENTS:
            self.experiments()
        self.plot_helper(
            name='ScikitLearn',
            df=self.experimenter.results,
            param_x='learning_rate',
            param_1='N',
            param_2=None,
        )
        self.plot_helper(
            name='Tensorflow',
            df=self.experimenter.results,
            param_x='learning_rate',
            param_1='N',
            param_2=None,
        )

    def plot_helper(self, name, df, param_x, param_1, param_2=None):
        param_y = 'accuracy'
        df['layers'] = df['layers'].apply(str)
        df = df[df['experiment'] == 'ExperimentMLP' + name]
        ncols = len(self.SIZES.keys())
        nrows = 2
        fig, axes = subplots(ncols=ncols, nrows=nrows)
        fig.set_size_inches(9 * ncols, 4 * nrows)
        axes = axes.reshape((nrows, ncols))
        for j, (n, k) in enumerate(self.SIZES.keys()):
            data = df[(df['k'] == k) & (df['n'] == n)]
            lineplot(
                x=param_x,
                y=param_y,
                hue=param_1,
                style=param_2,
                data=data,
                ax=axes[0][j],
                legend=False,
                estimator='mean',
                ci=None,
            )
            scatterplot(
                x=param_x,
                y=param_y,
                hue=param_1,
                style=param_2,
                data=data,
                ax=axes[0][j],
                legend='full',
            )
            lib = 'tensorflow' if name == 'Tensorflow' else 'scikit-learn' if name == 'ScikitLearn' else ''
            total = sum([e.parameters.k == k and lib in e.NAME for e in self.EXPERIMENTS])
            axes[0][j].set_title('n={}, k={}\n\n{} experiments per combination,   {}/{}\n'.format(
                n, k, self.SAMPLES_PER_POINT[(n, k)], len(data), total))
            axes[0][j].legend(loc='upper right', bbox_to_anchor=(1.235, 1.03))
            """
            if param_1:
                axes[0][j].legend(loc='upper right', bbox_to_anchor=(1.25, 1.06))
            #axes[0][j].set_ylim((0.96, 1.03))

            axes[0][j].xaxis.set_major_locator(FixedLocator(list(set(
                self.experimenter.results[param_x][self.experimenter.results['k'] == k]))))
            axes[0][j].yaxis.set_minor_locator(FixedLocator([.7, .9, .98]))
            axes[0][j].grid(b=True, which='minor', color='gray', linestyle=':')
            
            axes[1][j].xaxis.set_major_locator(FixedLocator(list(set(
                self.experimenter.results[param_x][self.experimenter.results['k'] == k]))))
            axes[1][j].yaxis.set_minor_locator(FixedLocator([.7, .9, .98]))
            axes[1][j].grid(b=True, which='minor', color='gray', linestyle=':')
            if param_1:
                axes[1][j].legend(loc='upper right', bbox_to_anchor=(1.325, 1.06))
            """
            lineplot(
                x='accuracy',
                y='measured_time',
                hue=param_1,
                style=param_2,
                data=data,
                ax=axes[1][j],
                legend='full',
                estimator='mean',
                ci=None,
            )
            axes[1][j].set_xscale('linear')
            axes[1][j].set_yscale('linear')
            axes[1][j].set_xlabel(param_y)
            axes[1][j].set_ylabel('runtime in s')
            axes[1][j].set_ylim(bottom=0)
            axes[1][j].xaxis.set_minor_locator(FixedLocator([.7, .9, .98]))
            axes[1][j].grid(b=True, which='minor', color='gray', linestyle=':')
            axes[1][j].legend(loc='upper right', bbox_to_anchor=(1.235, 1.03))
            """
            for i in range(nrows - 1):
                ticks = axes[i][j].get_xticks()
                tmp = min([float(tick) for tick in ticks])
                e = int(log10(tmp if tmp > 0 else .0001)) - 1
                axes[i][j].set_xticklabels(['{0:.1f}'.format(float(tick) * 10**(-e)) for tick in ticks])
                axes[i][j].set_xticklabels([str(round(float(label))) if float(label).is_integer() else label
                                            for label in [item.get_text() for item in axes[i][j].get_xticklabels()]])
                axes[i][j].set_xlabel('learning_rate times 1e{}'.format(e))
            """
        fig.subplots_adjust(hspace=.5, wspace=.5)
        title = fig.suptitle('Accuracy of {} Results on XOR Arbiter PUF'.format(name))
        title.set_position([.5, 1.05])
        fig.savefig('figures/{}_{}.pdf'.format(self.name(), name), bbox_inches='tight', pad_inches=.5)

