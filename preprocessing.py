#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from ydata_profiling import ProfileReport
import numpy as np
import random
import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import  cross_val_score
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from mlxtend.plotting import plot_confusion_matrix
import warnings
warnings.filterwarnings("ignore")
from sql_lib import sql
from imblearn.over_sampling import SMOTE
from sklearn.utils import resample
from sklearn.ensemble import RandomForestClassifier
import tensorflow as tf
from tensorflow.keras import regularizers

training_raw = sql("""
    SELECT * FROM canciones_features
    LEFT JOIN canciones_overview ON
    canciones_overview.id = canciones_features.id
    """) 
prediction_raw = sql("SELECT * FROM canciones_2023")

def create_target_variable(df):
    """
    Returns a DataFrame of countries predicted to make it in the top five of Eurovision 2023.

    Parameters:
    -----------
    model : sklearn estimator object
        The trained machine learning model to predict the top five countries.
    data_2023 : pandas DataFrame
        The data for countries participating in Eurovision 2023.

    Returns:
    --------
    pandas DataFrame
        A DataFrame containing the countries predicted to make it in the top five.
    """
    target_array = []
    for i in df["final_place"]:
        if i < 6:
            target = 1
        else:
            target = 0
        target_array.append(target)
    return np.array(target_array)

def statistics(model, X_test, y_test):

    """
    Calculate and print various statistics (accuracy, precision, recall, and F1 score) 
    for a given classification model and test data. Also, plot a confusion matrix.

    Args:
    model: a trained classification model with a predict() method.
    X_test: input data to test the model on.
    y_test: true labels corresponding to the input data.

    Returns:
    None
    """

    from sklearn.metrics import confusion_matrix
    y_pred = model.predict(X_test)
    confusion_matrix = confusion_matrix(y_test, y_pred)

    accuracy = accuracy_score(y_test, y_pred)
    print('Accuracy: %f' % accuracy)

    precision = precision_score(y_test, y_pred)
    print('Precision: %f' % precision)

    recall = recall_score(y_test, y_pred)
    print('Recall: %f' % recall)

    f1 = f1_score(y_test, y_pred)
    print('F1 score: %f' % f1)

    plot_confusion_matrix(conf_mat=confusion_matrix, figsize=(6, 6), cmap=plt.cm.RdPu)
    plt.suptitle("Confusion matrix")
    plt.show()
    
def top_2023(model, data_2023):
    """
    Create target variable array from final_place column of a dataframe.

    Args:
    - df (pd.DataFrame): Dataframe containing the final_place column.

    Returns:
    - np.ndarray: Array of binary values representing whether the country finished 
                  in the top 5 (1) or not (0).
    """

    prediccion_m1_2023= model.predict(data_2023)

    paises= sql("""SELECT country FROM canciones_2023""")

    top = pd.concat([paises, pd.DataFrame(prediccion_m1_2023)], axis=1)
    print(f"Model predicts {len(top[top[0] == 1])} countries will make it in the top five")
    return top[top[0] == 1]
def nn_statistics(model, X_test, y_test):
    """
    Calculate and print various statistics (accuracy, precision, recall, and F1 score) 
    for a given classification model and test data. Also, plot a confusion matrix.

    Args:
    model: a trained classification model with a predict() method.
    X_test: input data to test the model on.
    y_test: true labels corresponding to the input data.

    Returns:
    None
    """
    
    from sklearn.metrics import confusion_matrix


    y_pred = model.predict(X_test).flatten()
    y_pred = [np.round(i).astype(int) for i in y_pred]
    confusion_matrix = confusion_matrix(y_test, y_pred)
    plot_confusion_matrix(conf_mat=confusion_matrix, figsize=(6, 6), cmap=plt.cm.RdPu)
    plt.suptitle("Confusion matrix")
    plt.show()

    accuracy = accuracy_score(y_test, y_pred)
    print('Accuracy: %f' % accuracy)

    precision = precision_score(y_test, y_pred)
    print('Precision: %f' % precision)

    recall = recall_score(y_test, y_pred)
    print('Recall: %f' % recall)

    f1 = f1_score(y_test, y_pred)
    print('F1 score: %f' % f1)
 