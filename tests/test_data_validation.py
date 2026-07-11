import pandas as pd
import pytest

DATA_PATH = "data/iris.csv"

FEATURE_COLUMNS = [
    "sepal length (cm)",
    "sepal width (cm)",
    "petal length (cm)",
    "petal width (cm)",
]
EXPECTED_COLUMNS = FEATURE_COLUMNS + ["target"]
VALID_TARGETS = {0, 1, 2}


@pytest.fixture(scope="module")
def df():
    return pd.read_csv(DATA_PATH)


def test_file_not_empty(df):
    assert len(df) > 0, "Dataset is empty"


def test_expected_columns_present(df):
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    assert not missing, f"Missing columns: {missing}"


def test_no_missing_values(df):
    nulls = df[EXPECTED_COLUMNS].isnull().sum().sum()
    assert nulls == 0, f"Found {nulls} missing values"


def test_feature_dtypes_numeric(df):
    for col in FEATURE_COLUMNS:
        assert pd.api.types.is_numeric_dtype(df[col]), f"{col} is not numeric"


def test_feature_value_ranges(df):
    for col in FEATURE_COLUMNS:
        assert df[col].min() > 0, f"{col} has non-positive values"
        assert df[col].max() < 20, f"{col} has implausible values (>20 cm)"


def test_target_values_valid(df):
    found = set(df["target"].unique())
    assert found.issubset(VALID_TARGETS), f"Unexpected target values: {found - VALID_TARGETS}"


def test_target_is_integer_type(df):
    assert pd.api.types.is_integer_dtype(df["target"]), "target column should be integer-encoded"
