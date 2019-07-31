import time
import sys
import numpy as np
from collections import Counter


# Encapsulate our neural network in a class
class SentimentNetwork:
    def __init__(self, reviews, labels, min_count=50, polarity_cutoff=.1, hidden_nodes=10, learning_rate=0.1):
        """Create a SentimenNetwork with the given settings
        Args:
            reviews(list) - List of reviews used for training
            labels(list) - List of POSITIVE/NEGATIVE labels associated with the given reviews
            hidden_nodes(int) - Number of nodes to create in the hidden layer
            learning_rate(float) - Learning rate to use while training

        """
        # Assign a seed to our random number generator to ensure we get
        # reproducable results during development
        np.random.seed(1)

        # process the reviews and their associated labels so that everything
        # is ready for training
        self.pre_process_data(reviews, labels, min_count, polarity_cutoff)

        # Build the network to have the number of hidden nodes and the learning rate that
        # were passed into this initializer. Make the same number of input nodes as
        # there are vocabulary words and create a single output node.
        self.init_network(len(self.review_vocab), hidden_nodes, 1, learning_rate)

    def pre_process_data(self, reviews, labels, min_count, polarity_cutoff):

        pos_counts = Counter()
        neg_counts = Counter()
        total_counts = Counter()

        for i, review in enumerate(reviews):
            for word in review.split(' '):
                (pos_counts if labels[i] == 'POSITIVE' else neg_counts)[word] += 1
                total_counts[word] += 1

        pos_neg_ratios = Counter([(word, pos_counts[word]/float(neg_counts[word]+1))
                                  for word, count in total_counts.most_common() if count > min_count])

        # Add to vocabulary only words with the absolute pos/neg ratio at least polarity_cutoff
        self.review_vocab = [w for w, r in pos_neg_ratios if abs(r) >= polarity_cutoff]
        self.label_vocab = list(set([label for label in labels]))

        # Store the sizes of the review and label vocabularies.
        self.review_vocab_size = len(self.review_vocab)
        self.label_vocab_size = len(self.label_vocab)

        # Create a dictionary of words in the vocabulary mapped to index positions
        self.word2index = {w: i for (i, w) in enumerate(self.review_vocab)}

        # Create a dictionary of labels mapped to index positions
        self.label2index = {l: i for (i, l) in enumerate(self.label_vocab)}

    def init_network(self, input_nodes, hidden_nodes, output_nodes, learning_rate):
        # Store the number of nodes in input, hidden, and output layers.
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes

        # Store the learning rate
        self.learning_rate = learning_rate

        # Initialize weights

        # initialize the weights between the input layer and the hidden layer.
        self.weights_0_1 = np.zeros((self.input_nodes, self.hidden_nodes))

        # initialize the weights between the hidden layer and the output layer.
        self.weights_1_2 = np.random.normal(0, self.output_nodes ** -0.5,
                                            size=(self.hidden_nodes, self.output_nodes))

        self.layer_1 = np.zeros((1, hidden_nodes))

    def get_target_for_label(self, label):
        return 1 if label == "POSITIVE" else 0

    def sigmoid(self, x):
        # do not use np.exp(x), it will overflow!!!
        return 1 / (1 + np.exp(-x))

    def sigmoid_output_2_derivative(self, output):
        # Return the derivative of the sigmoid activation function,
        # where "output" is the original output from the sigmoid fucntion
        return output * (1 - output)

    def train(self, training_reviews_raw, training_labels):

        # make sure out we have a matching number of reviews and labels
        assert (len(training_reviews_raw) == len(training_labels))

        # Keep track of correct predictions to display accuracy during training
        correct_so_far = 0

        # Remember when we started for printing time statistics
        start = time.time()

        # ***new stuff***
        # make sure the second dimension contains very word only once
        # otherwise the network won't train successfully
        training_reviews = [list(set(self.word2index[word] for word in review.split(' ') if word in self.word2index))
                            for review in training_reviews_raw]

        # loop through all the given reviews and run a forward and backward pass,
        # updating weights for every item
        for i in range(len(training_reviews)):
            review, label = training_reviews[i], self.get_target_for_label(training_labels[i])
            # Implement the forward pass through the network.
            # That means use the given review to update the input layer,
            # then calculate values for the hidden layer,
            # and finally calculate the output layer.
            #
            # Do not use an activation function for the hidden layer,
            # but use the sigmoid activation function for the output layer.
            # ***new stuff: embedding***
            self.layer_1 = np.sum([self.weights_0_1[wi] for wi in review], axis=0, keepdims=True)
            layer_2 = self.sigmoid(self.layer_1.dot(self.weights_1_2))
            # Implement the back propagation pass here.
            # That means calculate the error for the forward pass's prediction
            # and update the weights in the network according to their
            # contributions toward the error, as calculated via the
            # gradient descent and back propagation algorithms you
            # learned in class.
            loss = layer_2 - label
            layer_2_delta = loss * self.sigmoid_output_2_derivative(layer_2)

            layer_1_delta = layer_2_delta.dot(self.weights_1_2.T)

            self.weights_1_2 -= self.learning_rate * self.layer_1.T.dot(layer_2_delta)
            # ***new stuff: update weights in embedding layer***
            for wi in review:
                self.weights_0_1[wi] -= self.learning_rate * layer_1_delta[0]

            # Keep track of correct predictions. To determine if the prediction was
            # correct, check that the absolute value of the output error
            # is less than 0.5. If so, add one to the correct_so_far count.
            correct_so_far += 1 if abs(loss) <= .5 else 0
            # For debug purposes, print out our prediction accuracy and speed
            # throughout the training process.

            elapsed_time = float(time.time() - start)
            reviews_per_second = i / elapsed_time if elapsed_time > 0 else 0

            sys.stdout.write("\rProgress:" + str(100 * i / float(len(training_reviews)))[:4] \
                             + "% Speed(reviews/sec):" + str(reviews_per_second)[0:5] \
                             + " #Correct:" + str(correct_so_far) + " #Trained:" + str(i + 1) \
                             + " Training Accuracy:" + str(correct_so_far * 100 / float(i + 1))[:4] + "%")
            if (i % 2500 == 0):
                print("")

    def test(self, testing_reviews, testing_labels):
        """
        Attempts to predict the labels for the given testing_reviews,
        and uses the test_labels to calculate the accuracy of those predictions.
        """

        # keep track of how many correct predictions we make
        correct = 0

        # we'll time how many predictions per second we make
        start = time.time()

        # Loop through each of the given reviews and call run to predict
        # its label.
        for i in range(len(testing_reviews)):
            pred = self.run(testing_reviews[i])
            if (pred == testing_labels[i]):
                correct += 1

            # For debug purposes, print out our prediction accuracy and speed
            # throughout the prediction process.

            elapsed_time = float(time.time() - start)
            reviews_per_second = i / elapsed_time if elapsed_time > 0 else 0

            sys.stdout.write("\rProgress:" + str(100 * i / float(len(testing_reviews)))[:4] \
                             + "% Speed(reviews/sec):" + str(reviews_per_second)[0:5] \
                             + " #Correct:" + str(correct) + " #Tested:" + str(i + 1) \
                             + " Testing Accuracy:" + str(correct * 100 / float(i + 1))[:4] + "%")

    def run(self, review_raw):
        """
        Returns a POSITIVE or NEGATIVE prediction for the given review.
        """
        # Run a forward pass through the network, like you did in the
        # "train" function. That means use the given review to
        # update the input layer, then calculate values for the hidden layer,
        # and finally calculate the output layer.
        #
        # Note: The review passed into this function for prediction
        #       might come from anywhere, so you should convert it
        #       to lower case prior to using it.
        # ***new stuff***
        review = [self.word2index[word] for word in review_raw.lower().split(' ') if word in self.word2index]
        self.layer_1 = np.sum([self.weights_0_1[i] for i in review], axis=0, keepdims=True)
        layer_2 = self.sigmoid(self.layer_1.dot(self.weights_1_2))

        return 'POSITIVE' if layer_2 >= .5 else 'NEGATIVE'



# g = open('reviews.txt','r') # What we know!
# reviews = list(map(lambda x:x[:-1],g.readlines()))
# g.close()
#
# g = open('labels.txt','r') # What we WANT to know!
# labels = list(map(lambda x:x[:-1].upper(),g.readlines()))
# g.close()
#
# mlp = SentimentNetwork(reviews[:-1000], labels[:-1000], learning_rate=0.1)
# mlp.train(reviews[:-1000], labels[:-1000])