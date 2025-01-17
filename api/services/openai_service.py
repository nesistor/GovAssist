import logging
from openai import OpenAI
from fastapi import HTTPException
import os
from api.services.tools_function import switch_prompt, get_service_links_us, tools_definition
import json

# API keys
XAI_API_KEY = os.getenv("XAI_API_KEY")
VISION_MODEL_NAME = "grok-vision-beta"
CHAT_MODEL_NAME = "grok-beta"

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

logger = logging.getLogger(__name__)

# Mapping of function names to implementations
tools_map = {
    "switch_prompt": switch_prompt,
    "get_service_links_us": get_service_links_us,
}

def execute_tool(tool_name: str, tool_args: dict) -> dict:
    # Check if the tool name exists in the tools map
    if tool_name in tools_map:
        tool_function = tools_map[tool_name]
        # Call the corresponding function with the provided arguments
        return tool_function(**tool_args)
    else:
        raise ValueError(f"Tool {tool_name} not found")

def process_image_with_grok(base64_image: str) -> dict:
    try:
        logger.debug("Sending request to Grok Vision model.")
        response = client.chat.completions.create(
            model=VISION_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high",  # Image detail level
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "Analyze this document and extract all fields. Split the output into two categories: "
                                "'completed_fields' and 'empty_fields'. For 'completed_fields', include the "
                                "'field_name' and the 'field_value'. For 'empty_fields', include only the 'field_name'. "
                                "Additionally, identify and validate required fields, and include their statuses (e.g., "
                                "'filled' or 'missing') in the response. Return the results in a clear JSON format "
                                "structured as follows:\n{\n  \"completed_fields\": [\n    { \"field_name\": \"<field_label>\", "
                                "\"field_value\": \"<value_entered>\" }\n  ],\n  \"empty_fields\": [\n    { \"field_name\": "
                                "\"<field_label>\" }\n  ],\n  \"required_field_statuses\": [\n    { \"field_name\": "
                                "\"<field_label>\", \"status\": \"filled\" or \"missing\" }\n  ]\n}\n\nPlease note that the "
                                "'X' next to the 'Signature of Applicant' label indicates the location where the applicant is "
                                "required to sign. It does not mean that the signature has already been provided or that any "
                                "information has been marked. The applicant must place their signature in the designated area "
                                "to complete the form."
                            )
                        }
                    ]
                }
            ],
        )
        return response.choices[0].message
    except Exception as e:
        logger.error("Error processing image: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

def process_document_with_text_model(aggregated_results: list) -> dict:
    document_context = " ".join([str(result) for result in aggregated_results])
    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
             messages=[
                {
                    "role": "system",
                    "content": """You are a helpful, friendly, and clear assistant with expertise in analyzing and solving form-related issues. 
                                Provide personalized guidance based on the extracted form data:

                    1. **Completed Fields**:
                       - Acknowledge the user's effort.
                       - Verify if the values provided are logical and valid.
                       ``` 
                       {completed_fields}
                       ```

                    2. **Empty Fields**:
                       - Explain the importance of each missing field.
                       - Provide instructions and examples to help complete it.
                       ``` 
                       {empty_fields}
                       ```

                    3. **Required Field Statuses**:
                       - Identify required fields that are incomplete.
                       - Prioritize missing required fields and guide the user to address them.
                       ``` 
                       {required_field_statuses}
                       ```

                    ### Output Structure:
                    - Start with an acknowledgment of the user's effort.
                    - Highlight completed fields and confirm their validity.
                    - Provide step-by-step guidance for each missing field, prioritizing required ones.
                    - Use a supportive tone with examples where relevant.
                    - End with encouragement to finish the form.

                    ### Example Output:
                    "Great work so far! Here's what I noticed:

                    ✅ **Completed Fields**:
                    - **Full Name**: John Doe
                    - **Date of Birth**: 1990-01-01
                       These look good!

                    ⚠️ **Fields That Need Attention**:
                    - **Email Address**: Missing. Please enter your email, e.g., john.doe@example.com.

                    🚨 **Required Fields Missing**:
                    - **Address**: Enter your full address, e.g., '123 Main St, Springfield, IL 12345'.

                    Keep going, you're almost there! 📝"

                    Generate helpful, supportive text based on the provided data."""
                },
                {"role": "user", "content": document_context},
            ],
        )
        return response.choices[0].message
    except Exception as e:
        logger.error("Error processing document: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

# A dictionary to store the conversation context per user (in a real scenario, this could be a database)
user_conversations = {}

def generate_response(request: dict) -> str:
    user_id = request.get('user_id')
    question = request.get('question')

    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    logger.info(f"Received question: {question} from user ID: {user_id}")

    # Initialize user context if it doesn't exist
    if user_id not in user_conversations:
        user_conversations[user_id] = []

    # Add the new question to the conversation history
    user_conversations[user_id].append({"role": "user", "content": question})

    # Build the base messages with the current context
    base_messages = [
        {
            "role": "system",
            "content": "You are a friendly and helpful assistant with expertise in various government services. "
                       "I can help with DMV, Health, Education, and Tax-related queries. "
                       "My goal is to simplify processes and make things clear with a little bit of humor along the way."
        }
    ]

    # Append all prior conversation messages for the user
    base_messages.extend(user_conversations[user_id])

    # Request response from OpenAI model (synchronous call)
    try:
        logger.info("Requesting response from OpenAI model")
        response = client.chat.completions.create(
            model="grok-2-latest",
            messages=base_messages,
            tools=tools_definition,  # Ensure this is passed in
            tool_choice="auto"
        )
        logger.info("Response received from OpenAI model")
        
        # Process tool calls concurrently if present
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            logger.info(f"Processing {len(tool_calls)} tool calls")
            tasks = []
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                logger.debug(f"Tool call: {tool_name}, Args: {tool_args}")
                tasks.append(execute_tool(tool_name, tool_args))

            results = [task for task in tasks]  # Handling tool calls sequentially since it's not async
            logger.info("Tool calls completed, processing results")
            for result in results:
                base_messages.append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id
                })

        # Add the final response to the conversation history
        final_response = response.choices[0].message.content
        user_conversations[user_id].append({"role": "assistant", "content": final_response})

        logger.info("Final response received from OpenAI model")

        # Return the final response content
        return final_response

    except Exception as e:
        # Log and raise error
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")