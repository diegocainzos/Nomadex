import os
import requests
from django.http import JsonResponse
import json
from dotenv import load_dotenv
# Get token from environment variable for security


load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"


def text_inference(prompt):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "model": "openai/gpt-oss-20b",
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]


tools = [
    {
        "name": "query_hotels",
        "description": "Searches for hotels in a specific location, sorted from cheapest to most expensive. If the user indicates anything about a trip, select this tool; you should use it almost by default.",
        "parameters": [
            {
                "name": "q",
                "type": "string",
                "description": "The city or place to search for hotels. For example: 'Paris', 'Playa del Carmen, Mexico'."
            },
            {
                "name": "engine",
                "type": "string",
                "description": "The value of this parameter will always be: google_hotels"
            },
            {
                "name": "check_in_date",
                "type": "string",
                "description": "Check-in date in YYYY-MM-DD format. If the user doesn't specify a concrete period, invent one, always after 2025-11-01."
            },
            {
                "name": "check_out_date",
                "type": "string",
                "description": "Check-out date in YYYY-MM-DD format. Example: '2025-09-16'. If the user doesn't specify a concrete period, invent one. Always after the invented check_in_date."
            },
            {
                "name": "adults",
                "type": "string",
                "description": "Number of adults. Example: '2'. When not specified use 2."
            },
            # {
            #     "name": "children",
            #     "type": "string",
            #     "description": "Parameter defines the number of children. Default to 0."
            # },
            # {
            #     "name": "children_ages",
            #     "type": "string",
            #     "description": """Parameter defines the ages of children. The age range is from 1 to 17. Parameter defines the ages of children. The age range is from 1 to 17. Example for single child only: 5. Example for multiple children (seperated by comma ,): 5,8,10. Empty if there is 0 children. Default of 8 separated by comma as many children""",
            # },
            {
                "name": "hotel_class",
                "type": "string",
                "description": "Parameter defines to include only certain hotel class in the results. Available options: 2 - 2-star, 3 - 3-star, 4 - 4-star, 5 - 5-star. When not specified ignore this parameter."
            },
            {
                "name": "sort_by",
                "type": "string",
                "description": "Parameter is used for sorting the results. Available options: 3 - Lowest price ,8 - Highest rating ,13 - Most reviewed. When not specified ignore this parameter."
            },
            {
                "name": "currency",
                "type": "string",
                "description": "Currency. Default option is EUR, but USD or other can be used if indicated."
            },
        ]
    }
]


def crear_prompt_decision(mensaje_usuario):
    """Create the prompt for the LLM to decide whether to use a tool."""
    return f"""
Your task is to analyze the user's message and decide whether you need to call a tool to respond.
Reply only with a JSON object.

Available tools:
{json.dumps(tools, indent=2)}

If a tool is necessary, respond with:
{{
  "decision": "use_tool",
  "name": "tool_name",
  "parameters": {{ "param_name": "extracted_value" }}
}}

If no tool is needed, respond with:
{{
  "decision": "answer_directly"
}}

User message: "{mensaje_usuario}"
"""


def crear_prompt_sintesis(mensaje_usuario, datos_hoteles):
    """
    Create an advanced prompt for the LLM to generate a final, conversational,
    and visually appealing response using the hotel data.
    """
    # Convert the data to a well-formatted JSON string for the prompt.
    # Limit the number of hotels here if necessary to avoid exceeding context.
    hoteles_json_string = json.dumps(
        datos_hoteles, indent=2, ensure_ascii=False)
    print(hoteles_json_string)

    # Improved prompt with clear instructions and examples (few-shot prompting)
    return f"""
# ROLE AND GOAL
You are Kódigo, a virtual travel assistant, expert at finding the best options for users. Your tone is friendly, helpful, and a bit enthusiastic. Your mission is to transform raw hotel data into a clear, useful, and visually appealing response.

# CONTEXT
A user has made the following request: "{mensaje_usuario}"
After searching your system, you obtained this data in JSON format:
```json
{hoteles_json_string}
```

# TASK AND FORMATTING RULES
Now, create a conversational response for the user. You MUST follow these rules:

1.  **Conversational Start:** Begin with a friendly greeting. Summarize in one sentence what you found, including the location. Example: "Of course! I found several hotels in [City] for your stay between [check_in_date] and [check_in_date] for [adults] adults. Here are the top results:"

2.  **Markdown Table:** Present all the hotel options in a compact Markdown table.
    *   The table columns should be: `Hotel`, `Price`, `Rating`, `Reviews`,`Hotel Class` .
    *   The `Hotel` name MUST be a clickable Markdown link using the `enlace_google` field: `[Hotel Name](enlace_google)`.
    *   Do not use any emojis.

3.  **Data Integrity:**
    *   You may only use information present in the provided JSON.
    *   If a field (like `puntuacion` or `precio`) is not available for a hotel, use "N/A" in the table cell. DO NOT INVENT ANY DATA.

4.  **Friendly Close:** End the response with a brief, open-ended question. Example: "Would you like more details on any of these?"


"""
