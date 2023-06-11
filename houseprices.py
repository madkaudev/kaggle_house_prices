# -*- coding: utf-8 -*-
"""HousePrices.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dNqldMZVygkBP2LwPG75qQdT70nLHcOG

# Import basic libraries and load the data

Import basic required libraries
"""

import pandas as pd
import numpy as np
import math

"""Load training data"""

train_csv = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/Housing Prices/train_housing.csv")

"""Set Id column to be index of dataframe"""

train_csv.set_index("Id")

"""# Visualize the data (optional)

Take a quick glance at data
"""

train_csv.head()

train_csv.info()

train_csv.describe()

"""Plot numerical data"""

import matplotlib.pyplot as plt


plt.rc("font", size = 14)
plt.rc("axes", labelsize = 12, titlesize = 12)

train_csv.hist(bins = 50, figsize = (24,16))
plt.show()

"""# Look for correlations between the features and the sale price (optional)

Look for which attributes correlate with target variable
"""

corr_matrix = train_csv.corr()
corr_matrix.SalePrice.sort_values(ascending=False)

train_csv.plot(kind="scatter", x="OverallQual", y="SalePrice", alpha=0.1)

"""Create copy of data to test new features and test their correlation to the target value"""

corr_train_csv = train_csv
corr_train_csv["LotAreaPerOvrCond"] = corr_train_csv["LotArea"] / corr_train_csv["OverallCond"]
corr_train_csv["1stFlrVs2ndFlr"] = corr_train_csv["1stFlrSF"] - corr_train_csv["2ndFlrSF"]
corr_train_csv["TotalGrade"] = corr_train_csv["OverallCond"] + corr_train_csv["OverallQual"]
corr_train_csv["FullAndHalfBsmtBath"] = corr_train_csv["BsmtFullBath"] + corr_train_csv["BsmtHalfBath"]

"""Create new correaltion matrix and check correlation with new features"""

new_corr_matrix = corr_train_csv.corr()
new_corr_matrix.SalePrice.sort_values(ascending=False)

"""# Prepare training data by creating features and labels and numerical and string features

Seperate data from target values
"""

housingFeatures = train_csv.drop("SalePrice", axis = 1)
housingLabels = train_csv.SalePrice

"""Seperate numerical features from string features"""

numFeats = housingFeatures.select_dtypes(exclude="object").columns
strFeats = housingFeatures.select_dtypes(include="object").columns

"""# Create custom class and methods to deal with numerical features

Define a custom transformer for numerical features
"""

from sklearn.base import BaseEstimator, TransformerMixin


listOfNumFeats = numFeats.to_list()

class New_Attributes(BaseEstimator, TransformerMixin):
  def __init__(self, add_new_features = True):
    self.add_new_features = add_new_features
  def fit(self, X, y=None):
    return self
  def transform(self, X, y=None):
    if self.add_new_features == True:
      LotAreaPerOvrCond = X[:, listOfNumFeats.index("LotArea")] / X[:, listOfNumFeats.index("OverallCond")]
      FirstFlrVsSecondFlr = X[:, listOfNumFeats.index("1stFlrSF")] - X[:, listOfNumFeats.index("2ndFlrSF")]
      TotalGrade = X[:, listOfNumFeats.index("OverallCond")] + X[:, listOfNumFeats.index("OverallQual")]
      FullAndHalfBsmtBath = X[:, listOfNumFeats.index("BsmtFullBath")] + X[:, listOfNumFeats.index("BsmtHalfBath")]
      return np.c_[X, LotAreaPerOvrCond, FirstFlrVsSecondFlr, TotalGrade, FullAndHalfBsmtBath]

"""Define method to handle numerical columns with some string values"""

def string_to_numerical(column):
  column = pd.to_numeric(column, errors="coerce")
  median = np.nanmedian(column)
  return column.fillna(median)

"""# Create data pipeline

Create data pipelines for numerical features and string features
"""

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


num_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median")), 
                         ("newAttr", New_Attributes()),
                         ("stdScaler", StandardScaler())])

str_pipeline = Pipeline([("ordinal", OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)),
                         ("oneHot", OneHotEncoder(handle_unknown="ignore"))])

"""Create full uniform data pipeline"""

from sklearn.compose import ColumnTransformer


data_pipeline = ColumnTransformer([("num", num_pipeline, numFeats),
                                   ("str", str_pipeline, strFeats)])
trainTransformed = data_pipeline.fit_transform(train_csv)

"""# Train multiple models and evaulate with the training set

Train a linear regression model and evaluate on the training set
"""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


linRegModel = LinearRegression()
linRegModel.fit(trainTransformed, housingLabels)

housingPredictionsLinReg = linRegModel.predict(trainTransformed)
linRegMSE = mean_squared_error(housingLabels, housingPredictionsLinReg)
linRegRMSE = math.sqrt(linRegMSE)

print("The RMSE based on a sample of the training data is: ")
print(linRegRMSE)

"""Train a decision tree regression model and evaluate on the training set"""

from sklearn.tree import DecisionTreeRegressor

decTreeModel = DecisionTreeRegressor()
decTreeModel.fit(trainTransformed, housingLabels)

housingPredictionsDecTree = decTreeModel.predict(trainTransformed)
decTreeMSE = mean_squared_error(housingLabels, housingPredictionsDecTree)
decTreeRMSE = math.sqrt(decTreeMSE)

print("The RMSE based on a sample of the training data is: ")
print(decTreeRMSE)

"""Train a random forest regression model and evaluate on the training set"""

from sklearn.ensemble import RandomForestRegressor

randomForestModel = RandomForestRegressor()
randomForestModel.fit(trainTransformed, housingLabels)

housingPredictionsRandomForest = randomForestModel.predict(trainTransformed)
randomForestMSE = mean_squared_error(housingLabels, housingPredictionsDecTree)
randomForestRMSE = math.sqrt(randomForestMSE)

print("The RMSE based on a sample of the training data is: ")
print(randomForestRMSE)

"""# Test the models with better methods

Test the models using cross-validation
"""

from sklearn.model_selection import cross_val_score

linRegKFoldScores = cross_val_score(linRegModel, trainTransformed, housingLabels, scoring="neg_mean_squared_error", cv=10)
linRegRMSE = np.sqrt(-linRegKFoldScores)
decTreeKFoldScores = cross_val_score(decTreeModel, trainTransformed, housingLabels, scoring="neg_mean_squared_error", cv=10)
decTreeRMSE = np.sqrt(-decTreeKFoldScores)
randomForestKFoldScores = cross_val_score(randomForestModel, trainTransformed, housingLabels, scoring="neg_mean_squared_error", cv=10)
randomForestRMSE = np.sqrt(-randomForestKFoldScores)

def print_kfold_scores(modelScores):
  print("Scores: ", modelScores)
  print("Mean: ", modelScores.mean())
  print("Standard Deviation: ", modelScores.std())

print("Linear Regression Model:")
print_kfold_scores(linRegRMSE)
print("")
print("Decision Tree Model:")
print_kfold_scores(decTreeRMSE)
print("")
print("Random Forest Model:")
print_kfold_scores(randomForestRMSE)

"""Evaluate the best model on the test set"""

test_csv = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/Housing Prices/test_housing.csv")

testFeaturesTransformed = data_pipeline.transform(test_csv)
testPredictions = randomForestModel.predict(testFeaturesTransformed)

"""# Create the csv file for submission

Create a function to transform an array of predictions into a dataframe
"""

def predictions_to_df(predictions):
  testId = test_csv.Id

  idSeries = pd.Series(testId)
  predictionsSeries = pd.Series(predictions)
  df = pd.DataFrame({"Id":idSeries, "SalePrice":predictionsSeries})

  df.set_index("Id")

  return df

"""Create csv of predictions"""

finalDf = predictions_to_df(testPredictions)
finalDf.to_csv("submission.csv", index=False)