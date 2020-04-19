import glob
from collections import OrderedDict

import numpy as np
import pandas as pd
from pathlib import Path

from scipy.io import arff
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import Bunch


def construct_flat_2pc_df(X, y) -> pd.DataFrame:
    """
    This function takes two dimensional X and one dimensional y arrays, concatenates and returns them as data frame
    Parameters
    ----------
    X two dimensional numpy array
    y one dimensional numpy array with labels
    -------
    Data frame with 3 columns x1 x2 and y and with number of rows equal to number of rows in X
    """

    y = pd.DataFrame({'y': y})
    X_df = pd.DataFrame(data=X, columns=['x1', 'x2'])

    df = pd.concat([X_df, y], axis=1)

    return df


def get_project_root() -> Path:  # pragma no cover
    """Returns project root folder."""
    return Path(__file__).parent.parent.parent


def preprocess_dataset(path, return_non_cat_length=False):
    data, meta = arff.loadarff(path)

    df = pd.DataFrame(data)
    y_index = len(df.columns) - 1
    y = df.pop(df.columns[y_index])

    le = LabelEncoder()
    y = le.fit_transform(y)

    categorical_feature_mask = df.dtypes == object

    categorical_cols = df.columns[categorical_feature_mask].tolist()
    non_categorical_cols = df.columns[~categorical_feature_mask].tolist()

    df[categorical_cols] = df[categorical_cols].replace({b'?': np.NaN})
    mode = df.mode().iloc[0]
    mean = df.filter(non_categorical_cols).mean()

    df[categorical_cols] = df.filter(categorical_cols).fillna(mode)
    df[non_categorical_cols] = df.filter(non_categorical_cols).fillna(mean)

    X = pd.get_dummies(df, columns=categorical_cols)
    if return_non_cat_length:
        return X.to_numpy(), y, len(non_categorical_cols)
    else:
        return X.to_numpy(), y


def load_arff_datasets(return_non_cat_length=False, dataset_paths=None):
    if dataset_paths is None:
        dataset_paths = glob.glob(f'{get_project_root()}/data/arff/*')

    datasets = OrderedDict()
    for path in sorted(dataset_paths):
        dataset_file = path.split('/')[-1]
        dataset_name = dataset_file.split('.')[0]
        if return_non_cat_length:
            X, y, cat_length = preprocess_dataset(path, return_non_cat_length)
            datasets[dataset_name] = Bunch(data=X, target=y, cat_length=cat_length, DESCR=dataset_name)
        else:
            X, y = preprocess_dataset(path, return_non_cat_length)
            datasets[dataset_name] = Bunch(data=X, target=y, DESCR=dataset_name)

    return datasets
