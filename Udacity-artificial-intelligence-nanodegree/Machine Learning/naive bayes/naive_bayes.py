import os
from collections import Counter
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

def get_files(dir):
    return [os.path.join(dir, fn) for fn in os.listdir(dir)]


def get_words(files, n=3000):
    """ read files, return a list of the n most frequently used
     words in the files, ignore some uninformative words

    :param files: mail files
    :param n: number of most common words to return
    :return: a list of the n most frequently used words
    """
    word_times = Counter()
    for file in files:
        with open(file) as f:
            # I don't take into account the case where a punctuation directly follows a word
            # since the file has well organized to avoid such cases
            # this case could be dealt with in the next step if it's needed
            word_times += Counter(f.read().split())

    words = list(word_times.keys())
    for w in words:
        if not w.isalpha():
            del word_times[w]
        if len(w) == 1:
            del word_times[w]

    return [w for w, _ in word_times.most_common(n)]


def get_features_labels(files, words):
    """ read files, extract features and labels

    :param files: mail files
    :param words: words which is treated as features
    :return: (features, labels)
    """
    features = np.zeros((len(files), len(words)))
    labels = np.zeros(len(files))
    for i in range(len(files)):
        with open(files[i]) as f:
            for word in f.read().split():
                if word in words:
                    features[i][words.index(word)] += 1

        _, fn = os.path.split(files[i])
        if fn.startswith('spmsg'):
            labels[i] = 1

    return features, labels


train_files = get_files('train-mails')
test_files = get_files('test-mails')

files = train_files + test_files

words = get_words(files)
X_train, y_train = get_features_labels(train_files, words)

model = GaussianNB()
model.fit(X_train, y_train)

X_test, y_test = get_features_labels(test_files, words)

y_hat = model.predict(X_test)

accuracy = np.mean(np.equal(y_test, y_hat))

print('Accuracy: %.4f' %accuracy_score(y_test, y_hat))