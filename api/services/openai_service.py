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
        return response.choices[0].messagev
    except Exception as e:
        logger.error("Error processing document: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

# A dictionary to store the conversation context per user (in a real scenario, this could be a database)
user_conversations = {}

async def generate_response(request: dict) -> str:
    # Extract user ID, session ID, and question from the request
    user_id = request.get("user_id")
    session_id = request.get("session_id")
    question = request.get("question")

    # Ensure both user ID and session ID are provided
    if not user_id or not session_id:
        raise HTTPException(status_code=400, detail="User ID and Session ID are required")

    logger.info(f"Received question: {question} from session ID: {session_id}")

    # Using async with for managing session within an async function
    async with SessionLocal() as session:
        # Retrieve conversation history from the database
        session_conversations = await get_conversation_history(session, user_id, session_id)

        # Add user's question to the conversation history in the database
        await add_message(session, user_id, session_id, "user", question)

        # Build base system messages for context
        base_messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly and helpful assistant with expertise in various government services. "
                    "I can help with DMV, Health, Education, and Tax-related queries. "
                    "My goal is to simplify processes and make things clear with a little bit of humor along the way."
                )
            }
        ]

        # Append prior conversation and the current user question
        base_messages.extend(session_conversations)
        base_messages.append({"role": "user", "content": question})

    try:
        # Request response from the OpenAI model
        logger.info("Requesting response from OpenAI model")
        response = client.chat.completions.create(
            model="grok-2-latest",
            messages=base_messages,
            max_tokens=500, 
            tools=tools_definition,
            tool_choice="auto"
        )
        logger.info("Response received from OpenAI model")

        # Retrieve the model's response
        model_response = response.choices[0].message

        # Process any tool calls from the model response
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            logger.info(f"Processing {len(tool_calls)} tool calls")

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                logger.debug(f"Tool call: {tool_name}, Args: {tool_args}")

                # Add ministry context if available
                if ministry and tool_name == "retrieve_and_answer":
                    tool_args["ministry"] = ministry

                # Execute the tool call
                if tool_name == "retrieve_and_answer":
                    tool_args["query"] = question
                    tool_args["ministry"] = ministry
                result = execute_tool(tool_name, tool_args)

                # Handle the result of the tool call
                if tool_name == "retrieve_and_answer":
                    if "answer" in result:
                        final_response = result["answer"]
                    else:
                        final_response = "I couldn't find an answer using the available tools."
                    break  # Exit the loop after the RAG tool

                # Process other types of tool results (e.g., links)
                elif "link" in result:
                    final_response = f"Here is the link for driving license in Texas: {result['link']}"
                    break  # Exit the loop once a valid response is found

            else:
                # If no valid tool response, use the model's original response
                final_response = model_response.content
        else:
            # If no tool calls, use the model's response
            final_response = model_response.content

        # Save the final response to the conversation history in the database
        async with SessionLocal() as session:
            await add_message(session, user_id, session_id, "assistant", final_response)

        logger.info("Final response processed successfully")
        return final_response

    except Exception as e:
        # Log and raise an error if something goes wrong
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")