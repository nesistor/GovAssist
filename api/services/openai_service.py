import logging
import uuid
from openai import OpenAI
from fastapi import HTTPException
import os
from api.services.tools_definition import switch_prompt, get_service_links_us, tools_definition
from api.db.database import SessionLocal
from api.db.queries import get_conversation_history, add_message, get_document_analysis, get_user_profile
from api.services.fill_pdf_service import fill_pdf_service
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
async def generate_initial_message(name: str = None, user_id: str = None) -> str:
    """
    Generates a concise initial greeting message with no extra details.
    
    Parameters:
      - name (str): The name of the user. Defaults to "citizen" if not provided.
      - user_id (str): The ID of the user; if provided, it will be included in the metadata.
    
    The function constructs a prompt that includes the name and calls the Grok endpoint with
    a metadata field. The metadata is sent as a list where the first element is null and the second
    element contains user_id.
    
    Returns:
      A string containing a short initial greeting message.
    """
    # Use "citizen" if name is None or empty.
    if not name:
        name = "citizen"

    # Construct the messages list with the conversation prompt
    messages = [
        {"role": "user", "content": f"Hello, my name is {name}. How can I get assistance with government services?"},
        {"role": "assistant", "content": f"Hey {name}! What would you like assistance with today? 📋"}
    ]

    # Build the metadata payload; the first element is None, the second element contains user_id.
    metadata = [None, {"user_id": user_id}]
    
    try:
        # Call the Grok completions endpoint with the correct messages format
        response = client.chat.completions.create(
            model="grok-2-latest",
            max_tokens=60,  # Keep the response short
            temperature=0.7,  # A bit of creativity for a friendly response
            messages=messages,
            metadata=metadata,
        )
    
        # Log the raw API response to check its structure
        logger.info(f"Raw API response: {response}")
    
        # Try accessing the response differently depending on its structure
        if hasattr(response, 'choices') and len(response.choices) > 0:
            # Access the 'content' of the message in the first choice
            completion = response.choices[0].message.content.strip()
            # Return just the short greeting without additional info
            initial_message = f"Hey {name}! What would you like assistance with today? 📋"  
            logger.info(f"Initial message generated: {initial_message}")
            return initial_message
        else:
            logger.error("Response does not contain expected 'choices' attribute.")
            raise HTTPException(status_code=500, detail="Error generating initial message")
    
    except Exception as e:
        logger.error(f"Error generating initial message: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating initial message")





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
                                "detail": "low",  # Image detail level
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
                       {completed_fields}async def generate_response(request: dict, session_id: str) -> str:
 
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


async def generate_response(request: dict, session_id: str) -> str:
    user_id = request.get("user_id")
    question = request.get("question")

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    logger.info(f"Received question: {question} from session ID: {session_id}")

    async with SessionLocal() as session:
        # Retrieve conversation history
        session_conversations = await get_conversation_history(session, user_id, session_id)

        # Add user's question to conversation history
        await add_message(session, user_id, session_id, "user", question)

        # Prepare base messages
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

        # Append prior conversation and the current question
        base_messages.extend(session_conversations)
        base_messages.append({"role": "user", "content": question})

    try:
        # Request response from AI model
        logger.info("Requesting response from OpenAI model")
        response = client.chat.completions.create(
            model="grok-2-latest",
            messages=base_messages,
            max_tokens=500, 
            tools=tools_definition,
            tool_choice="auto"
        )
        logger.info("Response received from OpenAI model")

        fingerprint = response.system_fingerprint  
        logger.info(f"System Fingerprint: {fingerprint}")

        model_response = response.choices[0].message
        tool_calls = model_response.tool_calls

        final_response = None

        if tool_calls:
            logger.info(f"Processing {len(tool_calls)} tool calls")
            
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                logger.debug(f"Tool call: {tool_name}, Args: {tool_args}")

                # Obsługa istniejących narzędzi
                if tool_name == "retrieve_and_answer":
                    ministry = tool_args.get("ministry")
                    result = execute_tool(tool_name, tool_args)
                    final_response = result.get("answer", "I couldn't find an answer using the available tools.")
                    
                elif tool_name == "get_service_links_us":
                    result = execute_tool(tool_name, tool_args)
                    if "link" in result:
                        final_response = f"Here is the link: {result['link']}"
                        
                # Nowa funkcjonalność: dynamiczne wypełnianie formularza
                elif tool_name == "dynamic_form_filler":
                    current_state = tool_args.get('current_step', {})
                    
                    # Pobierz strukturę formularza z bazy danych
                    async with SessionLocal() as session:
                        analysis = await get_document_analysis(session, session_id)
                        form_structure = json.loads(analysis.fields) if analysis else []
                    
                    required_fields = [f for f in form_structure if f.get('is_required')]
                    
                    # Inicjalizacja stanu jeśli potrzeba
                    if not current_state.get('remaining_fields'):
                        current_state['remaining_fields'] = required_fields.copy()
                        current_state['collected_data'] = {}
                    
                    if current_state['remaining_fields']:
                        next_field = current_state['remaining_fields'].pop(0)
                        # Przed pytaniem o pole - sprawdź czy dane istnieją w profilu
                        async with SessionLocal() as session:
                            profile = await get_user_profile(session, user_id)
                        
                        if next_field['field_name'].lower() in profile.personal_data:
                            current_state['collected_data'][next_field['field_name']] = profile.personal_data[next_field['field_name'].lower()]
                            continue  # Pomijaj pytanie o znane dane
                        else:
                            final_response = f"Proszę podać {next_field['field_name']}..."
                    else:
                        # Generuj PDF gdy wszystkie dane są zebrane
                        filled_pdf = await fill_pdf_service(
                            analysis.document_path,
                            current_state['collected_data']
                        )
                        download_url = generate_download_link(filled_pdf)
                        final_response = f"Formularz gotowy! Pobierz tutaj: {download_url}"
                        
                else:
                    logger.warning(f"Unknown tool called: {tool_name}")
                    continue

        # Zachowaj istniejącą logikę dla odpowiedzi
        if not final_response:
            final_response = model_response.content

        # Save assistant response if user is logged in
        if user_id:
            async with SessionLocal() as session:
                await add_message(session, user_id, session_id, "assistant", final_response)

        logger.info("Final response processed successfully")
        return final_response

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")


async def generate_conversation_title(user_id: str, session_id: str) -> str:
    """ 
    Generates a title for a given conversation based on its history.
    """
    async with SessionLocal() as session:
        history = await get_conversation_history(session, user_id, session_id)

    if not history:
        return "New Conversation"

    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "Your task is to generate a short, relevant, and summarizing title for this conversation. "
                               "The title should be concise, descriptive, and no more than 6 words."
                },
                *messages
            ],
            max_tokens=20
        )
        
        title = response.choices[0].message.content.strip()
        logger.info(f"Generated conversation title: {title}")
        return title

    except Exception as e:
        logger.error(f"Error generating conversation title: {str(e)}")
        return "Unknown Title"

def generate_download_link(pdf_content: bytes) -> str:
    # Tymczasowe rozwiązanie - zapisz plik i zwróć ścieżkę
    file_path = f"/tmp/filled_form_{uuid.uuid4()}.pdf"
    with open(file_path, "wb") as f:
        f.write(pdf_content)
    return f"/download?file={file_path}"