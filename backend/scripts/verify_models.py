from app.athena.models import ModelType
from app.athena.registry import model_registry
from app.athena.verifier import verifier

for model in ModelType:

    ok = verifier.verify(model)

    print(
        f"{model.value:<45}",
        "OK" if ok else "FAILED",
    )

print("\nHealthy Models")

for model in model_registry.verified():

    print(model.value)
