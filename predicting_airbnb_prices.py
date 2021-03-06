# -*- coding: utf-8 -*-
"""Predicting Airbnb prices.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pDBxhZucBDUkvMlcDISHZuQG3XbGyDA_
"""

# Commented out IPython magic to ensure Python compatibility.
# To support both python 2 and python 3
from __future__ import division, print_function, unicode_literals
# Common imports
import numpy as np
import os
import pandas as pd

# to make this notebook's output stable across runs
np.random.seed(42)

# To plot pretty figures
# %matplotlib inline
import matplotlib
import matplotlib.pyplot as plt
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12

# Where to save the figures
PROJECT_ROOT_DIR = "."
CHAPTER_ID = "end_to_end_project"
IMAGES_PATH = os.path.join(PROJECT_ROOT_DIR, "images", CHAPTER_ID)

def save_fig(fig_id, tight_layout=True, fig_extension="png", resolution=300):
    path = os.path.join(IMAGES_PATH, fig_id + "." + fig_extension)
    print("Saving figure", fig_id)
    if tight_layout:
        plt.tight_layout()
    try:
        plt.savefig(path, format=fig_extension, dpi=resolution)
    except:
        plt.savefig(fig_id + "." + fig_extension, format=fig_extension, dpi=resolution)

# Ignore useless warnings (see SciPy issue #5998)
import warnings
warnings.filterwarnings(action="ignore", message="^internal gelsd")
pd.options.display.max_columns = None

github_p = "https://raw.githubusercontent.com/Finance-781/FinML/master/Lecture%202%20-%20End-to-End%20ML%20Project%20/Practice/"

df = pd.read_csv(github_p+'datasets/sydney_airbnb.csv')

df.head()

# To get detailed summary of data
print ("Rows     : " , df.shape[0])
print ("Columns  : " , df.shape[1])
print ("\nFeatures : \n" , df.columns.tolist())
print ("\nMissing values :  ", df.isnull().sum().values.sum())
print ("\nUnique values :  \n",df.nunique())

incl = ["price","city","longitude","latitude","review_scores_rating","number_of_reviews","minimum_nights","security_deposit","cleaning_fee",
        "accommodates","bathrooms","bedrooms","beds","property_type","room_type","availability_365" ,"host_identity_verified", 
        "host_is_superhost","host_since","cancellation_policy"]

df1=df[incl]

df1.head()

# To get detailed summary of data
print ("Rows     : " , df1.shape[0])
print ("Columns  : " , df1.shape[1])
print ("\nFeatures : \n" , df1.columns.tolist())
print ("\nMissing values :  ", df1.isnull().sum().values.sum())
print ("\nUnique values :  \n",df1.nunique())

df1.describe()

df1.info()

# Importing regex
import re

# The price fields in our data frame
price_list = ["price","cleaning_fee","security_deposit"]

# We change any blanks to 0 and use our regex function to remove anything that isn't a number (or negative number which is changed to 0)
for col in price_list:
    df1[col] = df1[col].fillna("0")
    df1[col] = df1[col].apply(lambda x: float(re.compile('[^0-9eE.]').sub('', x)) if len(x)>0 else 0)

df1['host_since'] = pd.to_datetime(df1['host_since'])

df1.describe()

import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

sns.distplot(df1['price'])

df1['price'].skew()

df1['price'].kurtosis()

print(df1["price"].quantile(0.996))
print(df1["price"].mean())
print(df1["price"].median())

df2 = df1[df1["price"]<df1["price"].quantile(0.995)].reset_index(drop=True)

df2['price'].skew()

df2['price'].kurtosis()

sns.distplot(df2['price'])

df2.isnull().sum()

# Now let's explore our correlation matrix

corr_matrix = df2.corr()

# Heatmap
plt.figure(figsize = (10,10))
cmap = sns.diverging_palette(220,10,as_cmap = True)

#Deep dive into diverging_pattern
sns.heatmap(corr_matrix, xticklabels=corr_matrix.columns.values,
           yticklabels=corr_matrix.columns.values, cmap=cmap, vmax=1, center=0, square=True, linewidths=.5, cbar_kws={"shrink": .82})
plt.title('Heatmap of Correlation Matrix')

sns.distplot(df2['review_scores_rating'])

mode = df2["review_scores_rating"].median()
df2["review_scores_rating"].fillna(mode, inplace=True) # option 3

df3.isnull().sum()

df2.head()

sns.distplot(df2['review_scores_rating'])

df3=df2.drop(["review_scores_rating"], axis=1)

df3.info()

df3=df3.dropna()

# We now remove the rare occurences in categories as it's necessary for the cross validation step
# the below step is somewhat similar for what has been done with cities above

# We store the counts of each type in the variable item_counts
item_counts = df3.groupby(['property_type']).size()

# Store a list of the rare property types here i.e. the types that have a count less than 10 
rare_items = list(item_counts.loc[item_counts <= 10].index.values)

# drop the property types that were rare
df3 = df3[~df3["property_type"].isin(rare_items)].reset_index(drop=True)

# Sanity check
df3["property_type"].value_counts()

## For this taks we will keep the top 20 Sydney locations

list_of_20 = list(df3["city"].value_counts().head(20).index)
df3 = df3[df3["city"].isin(list_of_20)].reset_index(drop=True)
df3['city'].value_counts()

df3.info()

print(df3['room_type'].value_counts())
print(df3['cancellation_policy'].value_counts())

#### Now let's create some new features

df3["bedrooms_per_person"] = df3["bedrooms"]/df3["accommodates"]
df3["bathrooms_per_person"] = df3["bathrooms"]/df3["accommodates"]
df3['host_since'] = pd.to_datetime(df3['host_since'])
df3['days_on_airbnb'] = (pd.to_datetime('today') - df3['host_since']).dt.days

from sklearn.preprocessing import OneHotEncoder

X_cat = df3.select_dtypes(include=[object]).columns
df4 = pd.get_dummies(df3, columns=X_cat, drop_first=True)
df4.head()

df4=df4.drop(["host_since"], axis=1)

# Train test split

from sklearn.model_selection import train_test_split

# We remove the label values from our training data
X = df4.drop(['price'],axis=1).values

# We assigned those label values to our Y dataset
y = df4['price'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error

model = LinearRegression()
model.fit(X_train, y_train)

predictions = model.predict(X_test)
score = model.score(X_test, y_test)


lin_mse = mean_squared_error(y_test, predictions)
lin_rmse = np.sqrt(lin_mse)
lin_rmse

from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(random_state=89)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
score = model.score(X_test, y_test)


lin_mse = mean_squared_error(y_test, predictions)
lin_rmse = np.sqrt(lin_mse)
lin_rmse

from sklearn.model_selection import GridSearchCV

param_grid = [
    # try 12 (3×4) combinations of hyperparameters
    {'n_estimators': [3, 10, 30], 'max_features': [2, 4, 6, 8]},
    # then try 6 (2×3) combinations with bootstrap set as False
    {'bootstrap': [False], 'n_estimators': [3, 10], 'max_features': [2, 3, 4]},
  ]

forest_reg = RandomForestRegressor(random_state=42)
# train across 5 folds, that's a total of (12+6)*5=90 rounds of training 
grid_search = GridSearchCV(forest_reg, param_grid, cv=5,
                           scoring='neg_mean_squared_error', return_train_score=True)
grid_search.fit( X_train, y_train)

cvres = grid_search.cv_results_
for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
    print(np.sqrt(-mean_score), params)
    
print("")
print("Best grid-search performance: ", np.sqrt(-cvres["mean_test_score"].max()))

model = grid_search.best_estimator_
model.fit(X_train, y_train)

predictions = model.predict(X_test)
score = model.score(X_test, y_test)


lin_mse = mean_squared_error(y_test, predictions)
lin_rmse = np.sqrt(lin_mse)
lin_rmse



feature_importances = grid_search.best_estimator_.feature_importances_
feature_importances

feats = pd.DataFrame()
feats["Name"] = list(df4.drop(["price"], axis=1).columns)
feats["Score"] = feature_importances

feats.sort_values("Score",ascending=False).round(5).head(20)

