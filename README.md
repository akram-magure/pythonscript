# Weather Assistant – OpenAI Function Calling + Structured Output

A Python script that demonstrates OpenAI's **function calling** and **structured output** features using Pydantic models. It sends a weather query to GPT-4o, which triggers a tool call, executes a mock weather function, and returns a fully validated Pydantic object as the final response.

## How It Works

1. User asks for the weather in Tokyo.
2. The LLM decides to call the `get_weather` tool and returns structured arguments.
4. The result is sent back to the LLM, which returns a structured `WeatherReport` Pydantic object.

## Setup

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install openai pydantic

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

## Run

```bash
python test.py
```

## Example Output

```
[Step 1] Sending user request to LLM to trigger function call...

[System] Executing function 'get_weather' for Tokyo, Japan in celsius...

[Step 2] Sending function result back to LLM for Structured Output...

=== Final Structured Output (Pydantic Object) ===
WeatherReport(location='Tokyo, Japan', temperature=22.5, summary='Sunny and clear skies', clothing_advice='A light jacket should suffice.')

=== Formatted Application Output ===
Location: Tokyo, Japan
Temperature: 22.5
Summary: Sunny and clear skies
Advice: A light jacket should suffice.
```

## Requirements

- Python 3.8+
- OpenAI API key with access to `gpt-4o-2024-08-06`
