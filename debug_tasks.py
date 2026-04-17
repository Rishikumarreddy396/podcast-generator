from transformers.pipelines import PIPELINE_REGISTRY
import pprint
pprint.pprint(list(PIPELINE_REGISTRY.supported_tasks.keys()))
