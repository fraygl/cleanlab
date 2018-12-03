
# coding: utf-8

# In[1]:


# Python 2 and 3 compatibility
from __future__ import print_function, absolute_import, division, unicode_literals, with_statement


# In[2]:


DATA_DIR = 'fasttext_data/'


# In[3]:


def create_cooking_dataset(data_dir = None):
    '''This only needs to be run if you do not have
    fasttext_data/cooking.test.txt
    fasttext_data/cooking.train.txt
    
    Before you can use this method, you need to get the 
    cooking.preprocessed.txt file by running:
    bash get_cooking_stackexchange_data.sh .
    
    This is originally modified from here:
    https://github.com/facebookresearch/fastText/blob/master/tests/fetch_test_data.sh#L111
    '''
    
    if data_dir is None:
        data_dir = DATA_DIR
    
    # Create data_dir if it does not exist.
    import os, errno, shutil
    try:
        os.makedirs(data_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
            
    # Check if dataset already is available
    train_exists = os.path.isfile(data_dir + 'cooking.train.txt')    
    test_exists = os.path.isfile(data_dir + 'cooking.test.txt')
    if not(train_exists and test_exists):  
        # Dataset is not available, create it.

        import subprocess

        # Start out with cooking.preprocessed.txt by running the code here:
        # https://github.com/facebookresearch/fastText/blob/master/tests/fetch_test_data.sh#L111

        subprocess.call("bash get_cooking_stackexchange_data.sh .", shell = True)

        with open('cooking/cooking.preprocessed.txt', 'rU') as f:
            cook_data = f.readlines()

        single_label_cook_data = []
        for z in cook_data:
            num_labels = z.count('__label__') 
            z_list = z.split(" ")
            labels = z_list[:num_labels]
            content = " ".join(z_list[num_labels:])
            for l in labels:
                 single_label_cook_data.append(l + " " + content)

        with open(data_dir + 'cooking.train.txt', 'w') as f:
            f.writelines(single_label_cook_data[:-5000])

        with open(data_dir + 'cooking.test.txt', 'w') as f:
            f.writelines(single_label_cook_data[-5000:])

        # Clean-up download files
        shutil.rmtree('cooking')


# In[4]:


# fasttext only exists for these versions that are also compatible with cleanlab
import sys
v = sys.version_info[0] + 0.1 * sys.version_info[1]
if v in [3.4, 3.5, 3.6]:
    from fastText import train_supervised
    from cleanlab.models.fasttext import FastTextClassifier
    from sklearn.metrics import accuracy_score
    import numpy as np
else:
    import warnings
    warning = '''\n    fastText only supports Python 3.
    cleanlab supports Python versions 2.7, 3.4, 3.5, and 3.6.
    You are using Python version {}. To use cleanlab with fasttext, 
    you'll need to use Python 3.4, 3.5, or 3.6.'''.format(v)
    warnings.warn(warning)    


# In[5]:


def test_predict_proba_masking():
    ''''''
    psx = ftc.predict_proba(X = [500, 1000, 4999])
    assert(psx.shape[0] == 3)


# In[6]:


def test_predict_masking():
    ''''''
    pred = ftc.predict(X = [500, 1000, 4999])
    assert(pred.shape[0] == 3)


# In[7]:


def test_score_masking():
    ''''''
    score = ftc.score(X = [4, 8,  500, 1000, 4999], k = 5)
    assert(0. <= score <= 1.0)


# In[8]:


def test_apk_strictly_increasing():
    '''apk = average precision @ k. Instead of accuracy,
    we check if the true label is on the top k of the predicted
    labels. Thus, as k is increased, our accuracy should only increase
    or stay the same.'''
    prev_score = 0
    for k in range(1, 10):
        score = ftc.score(X = range(500), k = k)
        assert(score >= prev_score)
        prev_score = score
        print(prev_score)


# In[9]:


def test_predict_and_predict_proba():
    '''Test that we get exactly the same results
    for predicting the class label and the max
    predicted probability for each example regardless
    of if we use the fasttext model or our class to 
    predict the labels and the probabilities.'''
    
    # Check labels
    us = ftc.predict(train_data = False)
    them = [ftc.label2num[z[0]] for z in ftc.clf.predict(text)[0]]
    assert(accuracy_score(us, them) == 1)
    
    # Check probabilities
    us_prob = ftc.predict_proba(train_data = False).max(axis = 1)
    them_prob = ftc.clf.predict(text, k = len(us_prob))[1].max(axis = 1)
    assert(np.sum((us_prob - them_prob)**2) < 1e-4)
    
    return ftc


# In[11]:


def test_predict_and_predict_proba():
    '''Test that we get exactly the same results
    for predicting the class label and the max
    predicted probability for each example regardless
    of if we use the fasttext model or our class to 
    predict the labels and the probabilities.'''
    
    # Check labels
    us = ftc.predict(train_data = False)
    them = [ftc.label2num[z[0]] for z in ftc.clf.predict(text)[0]]
    assert(accuracy_score(us, them) == 1)
    
    # Check probabilities
    us_prob = ftc.predict_proba(train_data = False).max(axis = 1)
    them_prob = ftc.clf.predict(text, k = len(us_prob))[1].max(axis = 1)
    assert(np.sum((us_prob - them_prob)**2) < 1e-4)
    
    return ftc


# In[12]:


def test_correctness():
    '''Test to see if our model produces exactly the 
    same results as the '''
    
    with open(DATA_DIR + 'cooking.test.txt', 'r') as f:
        test_data = [z.strip() for z in f.readlines()]
    _, text = [list(t) for t in zip(*(z.split(" ", 1) for z in test_data))]
    
    ftc = FastTextClassifier(
        train_data_fn = DATA_DIR + 'cooking.train.txt', 
        test_data_fn = DATA_DIR + 'cooking.test.txt',
        kwargs_train_supervised = {
            'epoch': 5,
        },
        del_intermediate_data = True,
    )
    ftc.fit(X = None)
    
    original = train_supervised(DATA_DIR + 'cooking.train.txt', )
    
    # Check labels
    us = ftc.predict(train_data = False)
    them = [ftc.label2num[z[0]] for z in original.predict(text)[0]]
    assert(accuracy_score(us, them) == 1)
    
    # Check probabilities
    us_prob = ftc.predict_proba(train_data = False).max(axis = 1)
    them_prob = original.predict(text, k = len(us_prob))[1].max(axis = 1)
    assert(np.sum((us_prob - them_prob)**2) < 1e-4)


# In[179]:


def test_cleanlab_with_fasttext():
    import cleanlab

    top = 3
    label_counts = list(zip(np.unique(y_train + y_test), cleanlab.util.value_counts(y_train + y_test)))
    # Find which labels occur the most often.
    top_labels = [v for v,c in sorted(label_counts, key=lambda x: x[1])[::-1][:top]]

    # Get indices of data and labels for the top labels
    X_train_idx, y_train_top = [list(w) for w in zip(*[(i, z.split(" ", 1)[0]) for i, z in enumerate(train_data) if z.split(" ", 1)[0] in top_labels])]
    X_test_idx, y_test_top = [list(w) for w in zip(*[(i, z.split(" ", 1)[0]) for i, z in enumerate(test_data) if z.split(" ", 1)[0] in top_labels])]

    # Pre-train
    ftc = FastTextClassifier(
        train_data_fn = DATA_DIR + 'cooking.train.txt', 
        test_data_fn = DATA_DIR + 'cooking.test.txt', 
        kwargs_train_supervised = {
            'epoch': 20,
        },
        del_intermediate_data = True,
    )
    ftc.fit(X_train_idx, y_train_top)
    # Set epochs to 1 for getting cross-validated predicted probabilities
    ftc.clf.epoch = 1

    # Dictionary mapping string labels to non-negative integers 0, 1, 2...
    label2num = dict(zip(np.unique(y_train_top), range(top)))
    # Map labels
    s_train = np.array([label2num[z] for z in y_train_top])
    # Compute confident joint and predicted probability matrix for each example
    cj, psx = estimate_confident_joint_and_cv_pred_proba(X = np.array(X_train_idx), s = s_train, clf = ftc, cv_n_folds=5)
    # Find inidices of errors
    noise_idx = cleanlab.pruning.get_noise_indices(
        s_train, 
        psx, 
        confident_joint=cj, 
        prune_count_method='calibrate_confident_joint',
        prune_method = 'prune_by_class'
    )
    # Extract errors. This works by:
    # (1) masking the training examples we used with the noise indices identified.
    # (2) we find the actual train_data corresponding to those indices.
    errors = np.array(train_data)[np.array(X_train_idx)[noise_idx]]

    # Known error - this should be tagged as substituion, not baking.
    assert('__label__baking what can i use instead of corn syrup ?' in errors)
