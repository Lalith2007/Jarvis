# Grounding Validation — Sprint 12.9

## Validation Contract

Before `runtime.generate` builds its prompt, it calls `_validate_grounding()`:

```python
missing = self._validate_grounding(context)
if missing:
    return CapabilityResult(
        success=True,
        status="grounding_refused",
        result="I was unable to retrieve ... I will not fabricate ...",
    )
```

## What Is Validated

For each capability in `AthenaDecision.recommended_capabilities`:
- If `cap.capability` is in `_GROUNDING_CAP_IDS` AND `cap.required == True`
- Then `cap.capability` must exist as a key in `context.runtime_state`

`_GROUNDING_CAP_IDS = {"registry.models", "registry.capabilities", "memory.retrieve", "repository.read"}`

## Validation Outcomes

| Outcome | Condition | Action |
|---|---|---|
| PASSED | All required grounding outputs present | Generate normally |
| FAILED | One or more required grounding outputs missing | Return refusal, status=grounding_refused |

## Logging

Validation logs at `WARNING` when missing capabilities detected:
```
Grounding validation FAILED — missing required capability outputs: ['registry.models']
```

Logs at `INFO` when all required outputs pass:
```
Grounding validation PASSED — required outputs present: ['registry.models']
```

## Refusal Response Structure

`CapabilityResult(success=True, status="grounding_refused", result=<refusal_string>)`

`success=True` means the capability itself ran correctly — the refusal is the
correct response, not an error.  The controller still returns this string as the
mission response.

## Non-Grounding Queries

For queries where no grounding capability was recommended as required,
`_validate_grounding()` returns `[]` immediately and generation proceeds.
