import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field

# 1. Initialize the OpenAI client
# Ensure your OPENAI_API_KEY environment variable is set
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ==========================================
# PYDANTIC MODELS
# ==========================================

# Model for Function Calling Arguments
class GetWeatherArgs(BaseModel):
    location: str = Field(..., description="The city and state, e.g., Tokyo, Japan")
    unit: str = Field(default="celsius", description="The temperature unit, 'celsius' or 'fahrenheit'")

# Model for the Final Structured Output
class WeatherReport(BaseModel):
    location: str = Field(..., description="The location of the weather report")
    temperature: float = Field(..., description="The current temperature")
    summary: str = Field(..., description="A brief summary of the weather conditions")
    clothing_advice: str = Field(..., description="Advice on what to wear based on the weather")

# ==========================================
# DUMMY FUNCTION (TOOL)
# ==========================================

def get_weather(location: str, unit: str) -> str:
    """Simulates an API call to a weather service."""
    print(f"\n[System] Executing function 'get_weather' for {location} in {unit}...")
    
    # Mock response
    return json.dumps({
        "location": location,
        "temperature": 22.5
        "condition": "Sunny and clear",
        "unit": unit
    })

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    # Initial conversation history
    messages = [
        {"role": "system", "content": "You are a helpful weather assistant."},
        {"role": "user", "content": "What's the weather like in Tokyo today? Please give me a full report."}
    ]

    # Define the tool using Pydantic's built-in JSON schema generator
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": GetWeatherArgs.model_json_schema()
            }
        }
    ]

    print("[Step 1] Sending user request to LLM to trigger function call...")
    
    # Standard completion call with tools
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06", # Use a model that supports structured outputs
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    messages.append(response_message) # Append the assistant's tool call to history

    # Check if the model decided to call our function
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            if tool_call.function.name == "get_weather":
                
                # Parse the JSON arguments returned by the LLM directly into our Pydantic model
                args_json = tool_call.function.arguments
                args = GetWeatherArgs.model_validate_json(args_json)
                
                # Execute the actual Python function
                function_result = get_weather(location=args.location, unit=args.unit)
                
                # Append the function's result back to the conversation history
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": function_result
                })

        print("\n[Step 2] Sending function result back to LLM for Structured Output...")
        
        # Use the new `.parse()` method to force the final output into our Pydantic model
        final_response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=WeatherReport
        )

        # The output is no longer a raw string, but a fully validated Pydantic object!
        weather_report: WeatherReport = final_response.choices[0].message.parsed
        
        print("\n=== Final Structured Output (Pydantic Object) ===")
        print(repr(weather_report))
        
        print("\n=== Formatted Application Output ===")
        print(f"Location: {weather_report.location}")
        print(f"Temperature: {weather_report.temperature}")
        print(f"Summary: {weather_report.summary}")
        print(f"Advice: {weather_report.clothing_advice}")

if __name__ == "__main__":
    main()