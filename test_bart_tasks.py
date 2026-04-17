from transformers.pipelines import PIPELINE_REGISTRY
from transformers import BartForConditionalGeneration

tasks = []
for task, data in PIPELINE_REGISTRY.supported_tasks.items():
    if BartForConditionalGeneration in [data.get("pt", []), data.get("tf", [])]:
        tasks.append(task)

print(f"Tasks supported by BartForConditionalGeneration: {tasks}")
