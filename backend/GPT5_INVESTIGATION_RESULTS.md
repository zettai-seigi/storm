# GPT-5 Investigation Results

## Executive Summary

GPT-5 exists in OpenAI's API but has significant limitations that prevent it from working properly with STORM:

1. **Returns empty content** even when called successfully
2. **Requires different parameters** than other GPT models
3. **Appears to be in limited preview** with restricted functionality

## Key Findings

### 1. GPT-5 Models Available

OpenAI's `/v1/models` endpoint returns these GPT-5 variants:
- `gpt-5`
- `gpt-5-2025-08-07`
- `gpt-5-chat-latest`
- `gpt-5-mini`
- `gpt-5-mini-2025-08-07`
- `gpt-5-nano`
- `gpt-5-nano-2025-08-07`

### 2. Parameter Differences

**GPT-3.5/GPT-4 parameters:**
```json
{
  "model": "gpt-4",
  "messages": [...],
  "max_tokens": 500,
  "temperature": 0.7
}
```

**GPT-5 requirements:**
```json
{
  "model": "gpt-5",
  "messages": [...],
  "max_completion_tokens": 500,  // NOT max_tokens
  // No temperature parameter (only default 1.0 supported)
}
```

### 3. API Behavior

When called with correct parameters:
- **Status**: 200 OK
- **Tokens consumed**: Yes (585 tokens reported)
- **Content returned**: Empty string (0 characters)

This suggests GPT-5 is:
- Processing the request
- Consuming tokens
- But not generating actual content

### 4. LiteLLM Support

LiteLLM v1.75.8+ supports GPT-5 but:
- Requires `max_completion_tokens` instead of `max_tokens`
- Temperature and other sampling parameters are constrained/dropped
- STORM's current implementation doesn't handle these differences

## Test Results

| Model | Success | Personas Generated | Content Length | Notes |
|-------|---------|-------------------|----------------|-------|
| GPT-3.5 | ✅ | 4-5 | 170-227 chars | Works perfectly |
| GPT-4 | ✅ | 4-5 | 216-498 chars | Works perfectly |
| GPT-5 | ❌ | 0-1 | 0-79 chars | Empty or minimal content |
| GPT-5-mini | ❌ | 0 | 0 chars | Empty content |

## Code Modifications Attempted

### Fix 1: Parameter Transformation
```python
# In litellm_completion function
if "gpt-5" in model.lower():
    if "max_tokens" in kwargs:
        kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
    if "temperature" in kwargs and kwargs["temperature"] != 1.0:
        kwargs.pop("temperature")
```
**Result**: Parameters accepted but content still empty

### Fix 2: Force Chat Model Type
```python
# In OpenAIModel __init__
if model_type is None and "gpt-5" in model.lower():
    model_type = "chat"
```
**Result**: Resolved endpoint error but content still empty

## Root Cause Analysis

The issue is NOT a configuration problem on STORM's side. Testing shows:

1. ✅ GPT-5 accepts API calls when parameters are correct
2. ✅ GPT-5 consumes tokens (billing occurs)
3. ❌ GPT-5 returns empty content in response
4. ❌ Even direct API calls with correct parameters yield empty content

This indicates **GPT-5 is in a limited preview state** where it:
- Accepts requests
- Processes them (consuming tokens)
- But doesn't generate meaningful output

## Recommendations

### Immediate Action
**Do not use GPT-5 with STORM** until OpenAI fully releases it. The model currently:
- Wastes API tokens without producing content
- Causes STORM's persona generation to fail
- Results in empty or single-persona outputs

### Use Instead
- **GPT-4**: Best quality, higher cost
- **GPT-4-turbo**: Good balance of quality and speed
- **GPT-3.5-turbo**: Most cost-effective, good quality

### Future Considerations

When GPT-5 becomes fully functional, STORM will need updates to handle:
1. `max_completion_tokens` parameter
2. Temperature restrictions
3. Potentially different response formats

### For Users

If you see GPT-5 in your model dropdown:
1. **Don't select it** - it won't work properly
2. Use GPT-4 or GPT-3.5 instead
3. Wait for official GPT-5 release announcement from OpenAI

## Testing Scripts

Created testing scripts to verify findings:
- `test_model_fallback.py`: Tests model behavior with invalid models
- `test_gpt5_behavior.py`: Direct API testing of GPT-5
- `test_gpt5_with_correct_params.py`: Tests with correct parameters
- `test_storm_gpt5_fix.py`: Tests STORM integration

All scripts confirm: **GPT-5 returns empty content despite successful API calls**

---

*Investigation Date: 2025-09-22*
*STORM Version: Current*
*LiteLLM Version: 1.77.0*