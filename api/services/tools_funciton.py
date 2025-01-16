import requests

MINISTRY_PROMPTS = {
    "dmv": "You are a helpful assistant specializing in DMV-related queries, forms, and processes.",
    "tax": "You are an expert assistant in tax regulations, returns, and compliance.",
    "health": "You provide assistance with healthcare policies, benefits, and related services.",
    # Add more ministries as needed
}

# Tool function to switch prompts
def switch_prompt(ministry: str) -> dict:
    if ministry not in MINISTRY_PROMPTS:
        raise ValueError(f"Unknown ministry: {ministry}")
    return {"prompt": MINISTRY_PROMPTS[ministry]}

def get_document_license_id_for_driving(query, state="California"):
    if state.lower() != "california":
        return {
            "status": "error",
            "message": "This tool only supports queries for California."
        }
    
    # Mock endpoint for driving license-related documents
    api_url = "https://api.california.gov/driving-licenses"
    
    try:
        # Simulate API request for driving license documents
        response = requests.get(api_url, params={"query": query})
        response.raise_for_status()
        data = response.json()  # Assuming JSON response with relevant links or IDs
        return {
            "status": "success",
            "license_data": data
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to fetch data: {e}"
        }

def get_license_id(license_category, state="California"):
    if state.lower() != "california":
        return {
            "status": "error",
            "message": "This tool only supports queries for California."
        }

    # Mock API endpoint for license ID retrieval
    api_url = f"https://api.california.gov/licenses/{license_category}"
    
    try:
        # Simulate API request to fetch the license ID data
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()  # Assuming a JSON response with relevant license info
        return {
            "status": "success",
            "license_data": data
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to fetch data: {e}"
        }

def get_passport_info(passport_category, state="California"):
    if state.lower() != "california":
        return {
            "status": "error",
            "message": "This tool only supports queries for California."
        }

    # Mock API endpoint for passport info retrieval
    api_url = f"https://api.california.gov/passports/{passport_category}"
    
    try:
        # Simulate API request to fetch passport-related data
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()  # Assuming a JSON response with relevant passport info
        return {
            "status": "success",
            "passport_data": data
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to fetch data: {e}"
        }


{
        "type": "function",
        "function": {
            "name": "switch_prompt",
            "description": "Switches the assistant's prompt based on the ministry.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ministry": {
                        "type": "string",
                        "description": "The name of the ministry, e.g., 'dmv' or 'tax'."
                    }
                },
                "required": ["ministry"]
            }
        },
    }


{
    "type": "function",
    "function": {
        "name": "get_document_license_id_for_driving",
        "description": "Retrieve driving license document links or IDs for a specific query in California.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Specific details related to the driving license document request (e.g., 'renewal process', 'eligibility criteria')."},
                "state": {"type": "string", "description": "The state for which the query applies (fixed to 'California')."}
            },
            "required": ["query", "state"]
        }
    }
}

{
    "type": "function",
    "function": {
        "name": "get_license_id",
        "description": "Retrieve the License ID or related document links for specific license queries.",
        "parameters": {
            "type": "object",
            "properties": {
                "license_category": {
                    "type": "string",
                    "description": "The category of the license (e.g., driver's license, business license, etc.)."
                },
                "state": {
                    "type": "string",
                    "description": "The state where the license is registered (fixed to 'California')."
                }
            },
            "required": ["license_category", "state"]
        }
    }
}

{
    "type": "function",
    "function": {
        "name": "get_passport_info",
        "description": "Retrieve passport information or document links based on user query.",
        "parameters": {
            "type": "object",
            "properties": {
                "passport_category": {
                    "type": "string",
                    "description": "The category of the passport query (e.g., renewal, application)."
                },
                "state": {
                    "type": "string",
                    "description": "The state where the passport is issued (fixed to 'California')."
                }
            },
            "required": ["passport_category", "state"]
        }
    }
}

























































# Define tools for function calling
    # {
#     "type": "function",  # Specifies that this is a function type object
#     "function": {
#         "name": "retrieve_relevant_chunks",  # The name of the function
#         "description": "Retrieve the most relevant document chunks based on the user's query",  # A brief description of what the function does
#         "parameters": {  # Defines the parameters that the function accepts
#             "type": "object",  # The parameters are an object (a dictionary in Python)
#             "properties": {  # Specifies the properties (keys) inside the object (parameters)
#                 "query": {  # The 'query' parameter
#                     "type": "string",  # The type of the 'query' parameter is a string
#                     "description": "User's query."  # A brief description of what the 'query' represents
#                 },
#                 "category": {  # The 'category' parameter
#                     "type": "string",  # The type of the 'category' parameter is a string
#                     "description": "The category of the documents."  # A brief description of what the 'category' represents
#                 }
#             },
#             "required": ["query", "category"]  # The 'query' and 'category' parameters are required when calling the function
#         }
#     }
# },