import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences
from numpy.lib.scimath import logn


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Baysian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        best_score = float('inf')
        best_model = None

        for n in range(self.min_n_components, self.max_n_components+1):
            try:
                model = self.base_model(n)
                if model is not None:
                    logL = model.score(self.X, self.lengths)
                    p = n * n + 2 * n * len(self.X[0]) - 1
                    logN = np.log(len(self.X))
                    BIC = -2 * logL + p * logN
                    if BIC < best_score:
                        best_score = BIC
                        best_model = model
            except:
                if self.verbose:
                    print("failure on {} with {} states".format(self.this_word, n))
                
        if best_model is None:
            print("failure to use Bayesian information criteria to select model")
        return best_model


class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        best_score = float('-inf')
        best_model = None

        for n in range(self.min_n_components, self.max_n_components+1):
            model = self.base_model(n)
            if model is not None:
                try:
                    logL = model.score(self.X, self.lengths)
                    other_word_average_logL = np.mean([model.score(self.hwords[word][0], self.hwords[word][1])
                                                       for word in self.words if word != self.this_word])
                    DIC = logL - other_word_average_logL
                    if DIC > best_score:
                        best_score = DIC
                        best_model = model
                except:
                    if self.verbose:
                        print("failure on {} with {} states".format(self.this_word, n))
        
        if best_model is None:
            print("failure to use discriminative information criterion to select model")
        return best_model


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)

        best_score = float('-inf')
        best_model = None

        for n in range(self.min_n_components, self.max_n_components+1):
            kf = KFold(n_splits=min(3, len(self.sequences)))
            kf_score = 0
            model = self.base_model(n)

            if model is not None:
                try:
                    for train_index, test_index in kf.split(self.sequences):
                        train_X, train_lengths = combine_sequences(train_index, self.sequences)
                        test_X, test_lengths = combine_sequences(test_index, self.sequences)
                        training_model = model.fit(train_X, train_lengths)
                        kf_score += training_model.score(test_X, test_lengths)

                    average_kf_score = kf_score / kf.get_n_splits()
                    if average_kf_score > best_score:
                        best_score = average_kf_score
                        best_model = model
                except:
                    if self.verbose:
                        print("failure on {} with {} states".format(self.this_word, n))
                    
        if best_model is None:
            print("failure to use cross validation folds to select model")
            return None
        return best_model