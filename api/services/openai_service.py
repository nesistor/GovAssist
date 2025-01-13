import logging
from openai import OpenAI
from fastapi import HTTPException
import os

# API keys
XAI_API_KEY = os.getenv("XAI_API_KEY")
VISION_MODEL_NAME = "grok-vision-beta"
CHAT_MODEL_NAME = "grok-beta"

client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

logger = logging.getLogger(__name__)

DOCUMENTS_DB_OLD = {
    "driver_license_application": {
        "document_name": "Driver's License Application Form",
        "url": "https://www.dps.texas.gov/internetforms/forms/dl-14a.pdf"
    },
}

DOCUMENTS_DB = {
    "dmv": [
        {"document_name": "Driver's License Application", "url": "http://example.com/dmv_license"},
        {"document_name": "Vehicle Registration Form", "url": "http://example.com/dmv_registration"}
    ],
    "health": [
        {"document_name": "Healthcare Application Form", "url": "http://example.com/health_application"},
        {"document_name": "Insurance Claim Form", "url": "http://example.com/health_claim"}
    ],
    "education": [
        {"document_name": "Scholarship Application", "url": "http://example.com/scholarship_application"},
        {"document_name": "Student Loan Form", "url": "http://example.com/student_loan"}
    ],
    "tax": [
        {"document_name": "Tax Filing Form", "url": "http://example.com/tax_filing"},
        {"document_name": "Tax Refund Application", "url": "http://example.com/tax_refund"}
    ],
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


def generate_response(request: dict) -> str:
    """
    Generates a response based on the user's request and interaction.
    Includes support for various ministries.
    """
    ministry_id = request.get("ministry_id", "general")  # Default ministry if not provided
    base_messages = [
        {
            "role": "system",
            "content": "You are a friendly and helpful assistant with expertise in various government services. "
                       "I can help with DMV, Health, Education, and Tax-related queries. "
                       "My goal is to simplify processes and make things clear with a little bit of humor along the way."
        }
    ]
    
    base_messages.append({"role": "user", "content": request['question']})

    try:
        # Check the ministry and modify content accordingly
        if ministry_id == "dmv":
            base_messages[0]["content"] += " I am an expert in DMV services like driver's license and vehicle registration."
        elif ministry_id == "health":
            base_messages[0]["content"] += " I can assist with health-related services, including applications and insurance."
        elif ministry_id == "education":
            base_messages[0]["content"] += " I can guide you through the educational services like scholarships and student loans."
        elif ministry_id == "tax":
            base_messages[0]["content"] += " I can help you with tax filing, refunds, and other financial matters."
        else:
            base_messages[0]["content"] += " I can help with general government services."

        # Initial API call to generate the response
        response = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
            messages=base_messages,
        )

        # Extract the first response from the chat model
        initial_message = response.choices[0].message

        # Check if documents are needed
        requires_document = any(keyword in request['question'].lower() for keyword in ["form", "document", "application", "download"])

        # Prepare document links for all ministries
        document_links_html = ""
        if requires_document and ministry_id in DOCUMENTS_DB:
            for doc_info in DOCUMENTS_DB[ministry_id]:
                document_links_html += f'<p><a href="{doc_info["url"]}" download="{doc_info["document_name"]}">{doc_info["document_name"]}</a></p>'

        # Handle responses based on ministry and user query
        if requires_document:
            grok_response = (
                f"It seems like you need some official documents. Here are the relevant documents: "
                f"{document_links_html} Let me know if you need help filling them out!"
            )
        else:
            grok_response = f"Great question! Here's what I found: {initial_message.content}"

        # Create follow-up messages and final response
        follow_up_messages = base_messages + [initial_message, {"role": "assistant", "content": grok_response}]

        # Make the second API call to refine or extend the response
        final_response = client.chat.completions.create(
            model=CHAT_MODEL_NAME,
            messages=follow_up_messages,
        )

        final_answer = final_response.choices[0].message.content

        # Ministry redirection logic
        if "other ministry" in request['question'].lower():
            return "It seems you need help with another ministry. Let me redirect you to the main government assistant, who can help with any other queries."

        return final_answer

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing the request: {str(e)}")