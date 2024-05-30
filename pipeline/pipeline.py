import tensorflow_model_analysis as tfma

from typing import Optional
from tfx import v1 as tfx
from ml_metadata.proto import metadata_store_pb2
from tfx.dsl.experimental import latest_blessed_model_resolver
from tfx.types import Channel
from tfx.types.standard_artifacts import Model
from tfx.types.standard_artifacts import ModelBlessing


def create_pipeline(
    pipeline_name: str,
    pipeline_root: str,
    data_path: str,
    preprocessing_fn: str,
    run_fn: str,
    train_args: tfx.proto.TrainArgs,
    eval_args: tfx.proto.EvalArgs,
    serving_model_dir: str,
    beam_pipeline_args: list,
    metadata_connection_config: Optional[
        metadata_store_pb2.ConnectionConfig] = None
) -> tfx.dsl.Pipeline:
    """Implements the iris pipeline with TFX."""

    components = []

    example_gen = tfx.components.CsvExampleGen(input_base=data_path)
    components.append(example_gen)

    statistics_gen = tfx.components.StatisticsGen(
        examples=example_gen.outputs['examples']
    )
    components.append(statistics_gen)

    schema_gen = tfx.components.SchemaGen(
        statistics=statistics_gen.outputs['statistics'])
    components.append(schema_gen)

    example_validator = tfx.components.ExampleValidator(
        statistics=statistics_gen.outputs['statistics'],
        schema=schema_gen.outputs['schema']
    )
    components.append(example_validator)

    transform = tfx.components.Transform(
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        preprocessing_fn=preprocessing_fn)
    components.append(transform)
    
    trainer = tfx.components.Trainer(
        run_fn=run_fn,
        examples=transform.outputs['transformed_examples'],
        schema=schema_gen.outputs['schema'],
        transform_graph=transform.outputs['transform_graph'],
        train_args=train_args,
        eval_args=eval_args
    )
    components.append(trainer)

    model_resolver = tfx.dsl.Resolver(
        strategy_class=latest_blessed_model_resolver.LatestBlessedModelResolver,
        model=Channel(type=Model),
        model_blessing=Channel(
            type=ModelBlessing
        )
    ).with_id('latest_blessed_model_resolver')

    components.append(model_resolver)

    eval_config = tfma.EvalConfig(
        model_specs=[
            tfma.ModelSpec(
                signature_name='serving_default',
                label_key='target_xf',
                preprocessing_function_names=['transform_features'])
        ],
        slicing_specs=[tfma.SlicingSpec()],
        metrics_specs=[
            tfma.MetricsSpec(metrics=[
                tfma.MetricConfig(
                    class_name='SparseCategoricalAccuracy',
                    threshold=tfma.MetricThreshold(
                        value_threshold=tfma.GenericValueThreshold(
                            lower_bound={'value': 0.6}),
                        change_threshold=tfma.GenericChangeThreshold(
                            direction=tfma.MetricDirection.HIGHER_IS_BETTER,
                            absolute={'value': -1e-10})))
            ])
        ])

    evaluator = tfx.components.Evaluator(
        examples=example_gen.outputs['examples'],
        model=trainer.outputs['model'],
        baseline_model=model_resolver.outputs['model'],
        eval_config=eval_config
    )
    components.append(evaluator)

    pusher = tfx.components.Pusher(
        model=trainer.outputs['model'],
        model_blessing=evaluator.outputs['blessing'],
        push_destination=tfx.proto.PushDestination(
            filesystem=tfx.proto.PushDestination.Filesystem(
                base_directory=serving_model_dir
            )
        )
    )
    components.append(pusher)

    return tfx.dsl.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        enable_cache=True,
        metadata_connection_config=metadata_connection_config,
        beam_pipeline_args=beam_pipeline_args
    )
