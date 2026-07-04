"""
Feast Feature Repository Definitions — IRIS Pipeline
Single source of truth for all feature definitions.
Used by BOTH training (offline) and inference (online) paths.
"""
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float32, String

# 1. DATA SOURCE
# Points Feast at the Parquet file holding raw IRIS features.
# timestamp_field is required by Feast for point-in-time joins.
iris_source = FileSource(
    name="iris_source",
    path="data/iris_data_adapted_for_feast.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# 2. ENTITY
# The domain object the features describe.
# iris_id is the join key Feast uses to find the right feature row
# for a given iris plant in both offline and online retrieval.
iris = Entity(
    name="iris_id",
    value_type=ValueType.INT64,
    description="Unique identifier for each iris plant / measurement sample",
)

# 3. FEATURE VIEW
# Groups the 4 IRIS measurement columns + species label under one name,
# tied to the iris_id entity and the FileSource above.
# TTL = 365 days means a value stays valid for 365 days after its event_timestamp.
iris_feature_view = FeatureView(
    name="iris_features",
    entities=[iris],
    ttl=timedelta(days=365),
    schema=[
        Field(name="sepal_length", dtype=Float32),
        Field(name="sepal_width",  dtype=Float32),
        Field(name="petal_length", dtype=Float32),
        Field(name="petal_width",  dtype=Float32),
        Field(name="species",      dtype=String),
    ],
    online=True,
    source=iris_source,
    tags={"team": "mlops_week3", "dataset": "iris"},
)
