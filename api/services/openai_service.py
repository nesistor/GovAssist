import logging
from openai import OpenAI
from fastapi import HTTPException
import os
from api.services.tools_funciton import switch_prompt,get_service_links_us 

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


def generate_response_old(request: dict) -> str:
    """
    Generates a response based on the user's request and interaction.
    """
    base_messages = [
        {
            "role": "system",
            "content": "You are a funny, friendly, and incredibly knowledgeable assistant who works at the DMV. "
                       "You are an expert in all DMV processes, forms, regulations, and problem-solving scenarios. "
                       "Your job is to help users in a lighthearted, easy-to-understand, and supportive way. "
                       "Explain complex processes in simple terms, use relatable analogies, and add a touch of humor to make DMV topics less stressful. "
                       "Always stay polite, positive, and provide clear, actionable solutions to any DMV-related questions or issues."
        }
    ]
    base_messages.append({"role": "user", "content": request['question']})

    try:
        # Initial API call to the chat model
        response = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
            messages=base_messages,
        )

        # Extract the first response from the chat model
        initial_message = response.choices[0].message

        # Check if the user's query involves document-related topics
        requires_document = any(keyword in request['question'].lower() for keyword in ["form", "document", "application", "download"])

        # If documents are relevant, prepare document links HTML
        document_links_html = ""
        if requires_document:
            for doc_key, doc_info in DOCUMENTS_DB.items():
                document_links_html += f'<p><a href="{doc_info["url"]}" download="{doc_info["document_name"]}">{doc_info["document_name"]}</a></p>'

        # Create an interactive response depending on the context
        if requires_document:
            grok_response = (
                f"Sure thing! It sounds like you need some official documents. Here are the ones I think will help you: "
                f"{document_links_html} Let me know if you'd like help filling them out or understanding what to do next!"
            )
        else:
            grok_response = (
                f"Great question! {initial_message.content} "
                f"If at any point you think a DMV document might help, just let me know!"
            )

        # Prepare follow-up messages for continued conversation
        follow_up_messages = base_messages + [initial_message, {"role": "assistant", "content": grok_response}]

        # Make the second API call to refine or extend the response
        final_response = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
            messages=follow_up_messages,
        )

        # Extract and process the final response content
        final_answer = final_response.choices[0].message.content
        return final_answer

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")

# Main response generation function
def generate_response(request: dict) -> str:
    """
    Handles user requests and dynamically provides service links for U.S. states using tools.
    """
    messages = [
        {"role": "user", "content": request['question']}
    ]
    
    try:
        # Initial API call with tools defined
        response = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
            messages=messages,
            tools=tools_definition,
            tool_choice="auto"
        )
        
        # Process tool calls if the response includes them
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Execute the tool function and get results
                result = tools_map[tool_name](**tool_args)
                
                # Append tool result to messages
                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id
                    }
                )
        
        # Final API call with tool results
        final_response = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
            messages=messages,
            tools=tools_definition,
            tool_choice="auto"
        )
        
        return final_response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")














def generate_response_old(request: dict) -> str:
    """
    Generates a response based on the user's request and interaction.
    Supports all government ministries.
    """
    print("Starting to generate response.")

    # Step 1: Extract ministry_id from the request (default to 'general')
    ministry_id = request.get("ministry_id", "general")  
    logger.debug(f"Ministry ID set to: {ministry_id}")

    base_messages = [
        {
            "role": "system",
            "content": "You are a friendly and helpful assistant with expertise in various government services. "
                       "I can help with DMV, Health, Education, and Tax-related queries. "
                       "My goal is to simplify processes and make things clear with a little bit of humor along the way."
        }
    ]
    
    # Step 2: Append user's query to the message
    base_messages.append({"role": "user", "content": request['question']})
    logger.debug(f"User question added to message: {request['question']}")

    try:
        # Step 3: Detect the ministry based on the query
        logger.debug("Detecting ministry based on user query.")
        ministry_response = detect_ministry(request['question'])
        ministry_id = ministry_response.get("ministry", "general")  # Default to "general" if not found
        logger.debug(f"Detected ministry: {ministry_id}")

        # Step 4: Modify the system message based on the detected ministry
        if ministry_id == "dmv":
            base_messages[0]["content"] += " I specialize in DMV services like driver's license and vehicle registration."
        elif ministry_id == "health":
            base_messages[0]["content"] += " I can assist with health-related services, including applications and insurance."
        elif ministry_id == "education":
            base_messages[0]["content"] += " I can guide you through educational services like scholarships and student loans."
        elif ministry_id == "tax":
            base_messages[0]["content"] += " I can help you with tax filing, refunds, and other financial matters."
        else:
            base_messages[0]["content"] += " I can help with general government services."

        # Step 5: Initial API call to generate the response using function calls for documents
        logger.debug("Making API call to OpenAI to generate response.")
        response = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
            messages=base_messages,
            functions=tools_definition  # Pass tools_definition for function calls
        )
        logger.debug(f"Received API response: {response}")

        # Step 6: Extract the first response from the chat model
        initial_message = response.choices[0].message
        logger.debug(f"Initial message content from API: {initial_message.content}")

        # Step 7: Check if documents are needed based on the user's request
        requires_document = any(keyword in request['question'].lower() for keyword in ["form", "document", "application", "download"])
        logger.debug(f"Does the user require documents? {'Yes' if requires_document else 'No'}")

        # Step 8: If documents are needed, call the get_documents_links function
        if requires_document:
            logger.debug(f"Retrieving documents for ministry '{ministry_id}' based on user query.")
            documents_response = get_documents_links(ministry_id, request['question'])
            document_links_html = ""
            if documents_response['documents']:
                for doc_info in documents_response['documents']:
                    document_links_html += f'<p><a href="{doc_info["url"]}" download="{doc_info["document_name"]}">{doc_info["document_name"]}</a></p>'
                grok_response = (
                    f"It seems like you need some official documents. Here are the relevant documents: "
                    f"{document_links_html} Let me know if you need help filling them out!"
                )
                logger.debug(f"Generated document links: {document_links_html}")
            else:
                grok_response = "I couldn't find any documents based on your request. Could you please be more specific about the document you need?"
                logger.debug("No documents found based on user query.")
        else:
            grok_response = f"Great question! Here's what I found: {initial_message.content}"
            logger.debug(f"Generated response without documents: {grok_response}")

        # Step 9: Return the final response including document links if applicable
        logger.debug(f"Final response to return: {grok_response}")
        return grok_response

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")
