from datetime import timedelta
from feast import Entity, FeatureView, Field, ValueType
from feast.types import Float32, String
from feast import BigQuerySource

iris_bq_source = BigQuerySource(
    name="iris_bq_source",
    table="project-eac74fb9-0e15-492a-ab1.feast_iris_feature_store.iris_features",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

iris = Entity(
    name="iris_id",
    value_type=ValueType.INT64,
    description="Unique identifier for each iris sample",
)

iris_feature_view_bq = FeatureView(
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
    source=iris_bq_source,
    tags={"team": "mlops_week3", "backend": "bigquery"},
)
