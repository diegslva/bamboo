
import numpy as np

import pandas
from nose.tools import *
from bamboo.core import *
from bamboo.helpers import *
import bamboo.modeling

from bamboo.modeling.ModelingData import ModelingData

from pandas.util.testing import assert_frame_equal

from numpy.random import RandomState

from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression

from nose.tools import assert_dict_equal


assert_equal.__self__.maxDiff = None

group = [0, 0, 0, 0,
         1, 1, 1, 1,
         0, 0, 0, 1]

feature1 = [1, 1, 1, 1,
            2, 2, 3, 4,
            1, 2, 3, 4]

feature2 = [10.0, 10.5, 9.5, 11.0,
            20.0, 20.0, 35.0, -10.0,
            0.0, 200.0, 150.0, -30.0]


feature3 = ['A', 'A', 'B', 'C',
            'C', 'B', 'D', 'B',
            'A', 'B', 'C', 'D']

df = pandas.DataFrame({'group':group,
                       'feature1':feature1,
                       'feature2':feature2})

df2 = pandas.DataFrame({'group':group,
                        'feature1':feature1,
                        'feature2':feature2,
                        'feature3':feature3})



def test_split():

    random_state = RandomState(12345)

    data = ModelingData.from_dataframe(df, target='group')

    train, test = data.train_test_split(random_state=random_state)

    print train, test

    eq_(train.shape(), (9,2))
    eq_(test.shape(), (3,2))

    assert(train.is_orthogonal(test))


def test_balance_truncation():

    data = ModelingData.from_dataframe(df, target='group')

    eq_(len(data), 12)

    value_counts = data.targets.value_counts()
    eq_(value_counts[0], 7)
    eq_(value_counts[1], 5)

    # Now, balance the data
    balanced = data._balance_by_truncation()

    eq_(len(balanced), 10)

    value_counts = balanced.targets.value_counts()
    eq_(value_counts[0], 5)
    eq_(value_counts[1], 5)


def test_balance_sample():

    data = ModelingData.from_dataframe(df, target='group')

    eq_(len(data), 12)

    value_counts = data.targets.value_counts()
    eq_(value_counts[0], 7)
    eq_(value_counts[1], 5)

    # Now, balance the data
    np.random.seed(42)
    balanced = data._balance_by_sample_with_replace(size=20)

    eq_(len(balanced), 20)

    value_counts = balanced.targets.value_counts()
    eq_(value_counts[0], 10)
    eq_(value_counts[1], 10)


def test_orthogonal():

    dataA = ModelingData.from_dataframe(df.iloc[0:6], target='group')
    dataB = ModelingData.from_dataframe(df.iloc[3:9], target='group')
    dataC = ModelingData.from_dataframe(df.iloc[6:12], target='group')

    assert(dataA.is_orthogonal(dataC))
    assert(not dataA.is_orthogonal(dataB))
    assert(not dataB.is_orthogonal(dataC))


def test_numeric_features():

    data = ModelingData.from_dataframe(df2, target='group')

    eq_(data.shape(), (12,3))
    assert('feature3' in data.features.columns)

    numeric_data = data.numeric_features()

    eq_(numeric_data.shape(), (12,2))
    assert('feature3' not in numeric_data.features.columns)


def test_probas():

    clf = LogisticRegression()

    data = ModelingData.from_dataframe(df, target='group')

    data.fit(clf)

    probas = data.predict_proba(clf)

    eq_(dict(probas.irow(0)), {'index': 0.0, 'proba_0': 0.58298495576378184, 'proba_1': 0.41701504423621821, 'target': 0.0})


def test_predict():

    reg = LinearRegression()

    data = ModelingData.from_dataframe(df, target='group')

    data.fit(reg)

    predictions = data.predict(reg)

    eq_(dict(predictions.irow(0)), {'predict': 0.15360473177939843, 'index': 0.0, 'target': 0.0})
    eq_(dict(predictions.irow(-1)), {'predict': 1.2116420074937881, 'index': 11.0, 'target': 1.0})


def test_summary():

    clf = LogisticRegression()

    data = ModelingData.from_dataframe(df, target='group')
    data.fit(clf)

    probas = data.predict_proba(clf)
    summary = ModelingData.get_threshold_summary(probas, 1)

    assert_dict_equal(dict(summary), {'sensiticity': 1.0, 'target': 1, 'f1': 1.0, 'recall': 1.0, 'num_negatives': 7,
                                      'num_positives': 5, 'false_positive_rate': 0.0, 'false_positives': 0, 'precision': 1.0,
                                      'true_positives': 5, 'false_negatives': 0, 'true_positive_rate': 1.0, 'specificity': 1.0,
                                      'threshold': 0.5, 'true_negatives': 7, 'accuracy': 1.0})


def test_classifier_performance_summary():

    clf = LogisticRegression()

    data = ModelingData.from_dataframe(df, target='group')
    data.fit(clf)

    probas, summary = data.get_classifier_performance_summary(clf, 0, thresholds=np.arange(0.0, 1.0, 0.1))

    assert_dict_equal(dict(summary.irow(0)), {'f1': 0.7368421052631579, 'target': 0.0, 'sensiticity': 1.0, 'recall': 1.0,
                                              'num_negatives': 0.0, 'num_positives': 12.0, 'false_positive_rate': 1.0,
                                              'false_positives': 5.0, 'precision': 0.58333333333333337, 'true_positives': 7.0,
                                              'false_negatives': 0.0, 'true_positive_rate': 1.0, 'specificity': 0.0,
                                              'true_negatives': 0.0, 'accuracy': 0.58333333333333337})

