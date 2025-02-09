import requests
from typing import Dict
from api.services.rag_utils import retrieve_relevant_documents, generate_answer_with_context  # Import RAG functions


MINISTRY_PROMPTS = {
    "dmv": "You are a helpful assistant specializing in DMV-related queries, forms, and processes.",
    "tax": "You are an expert assistant in tax regulations, returns, and compliance.",
    "health": "You provide assistance with healthcare policies, benefits, and related services.",
    # Add more ministries as needed
}

# Example U.S. state-specific service links database
SERVICE_LINKS_US = {
    "california": {
        "passport": "https://travel.state.gov/content/travel/en/passports.html",
        "license": "https://www.dmv.ca.gov/portal/driver-licenses-identification-cards/",
        "id": "https://www.dmv.ca.gov/portal/id-cards/",
        "car_registration": "https://www.dmv.ca.gov/portal/vehicle-registration/"
    },
    "texas": {
        "passport": "https://travel.state.gov/content/travel/en/passports.html",
        "license": "https://www.txdps.state.tx.us/DriverLicense/",
        "id": "https://www.txdps.state.tx.us/DriverLicense/",
        "car_registration": "https://www.txdmv.gov/motorists/register-your-vehicle"
    },
    "new_york": {
        "passport": "https://travel.state.gov/content/travel/en/passports.html",
        "license": "https://dmv.ny.gov/driver-license/get-driver-license",
        "id": "https://dmv.ny.gov/id-card/non-driver-id-card",
        "car_registration": "https://dmv.ny.gov/registration/how-register-vehicle"
    }
    # Add more states as needed
}

# Tool function to switch prompts
def switch_prompt(ministry: str) -> dict:
    if ministry not in MINISTRY_PROMPTS:
        raise ValueError(f"Unknown ministry: {ministry}")
    return {"prompt": MINISTRY_PROMPTS[ministry]}


# Tool function to get service links for U.S. states
def get_service_links_us(state: str, service_type: str) -> Dict[str, str]:
    """
    Returns links for U.S. state-specific government services based on the state and service type.
    """
    state = state.lower()
    if state not in SERVICE_LINKS_US:
        raise ValueError(f"Unsupported state: {state}")
    
    links = SERVICE_LINKS_US[state]
    if service_type not in links:
        raise ValueError(f"Unsupported service type: {service_type}")

    return {"link": links[service_type]}




# Define tools for function calling (Updated with RAG tool)
tools_definition = [
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_service_links_us",
            "description": "Returns U.S. state-specific links for government services.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "The U.S. state name, e.g., 'California', 'Texas', or 'New York'."
                    },
                    "service_type": {
                        "type": "string",
                        "description": "The type of service, e.g., 'passport', 'license', 'id', or 'car_registration'."
                    }
                },
                "required": ["state", "service_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_and_answer",
            "description": "Wyszukuje dokumenty i generuje odpowiedź na podstawie RAG.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Zapytanie użytkownika dotyczące procedur lub regulacji ministerstwa."
                    },
                    "ministry": {
                        "type": "string",
                        "description": "Ministerstwo, np. 'dmv', 'tax', 'health'."
                    }
                },
                "required": ["query", "ministry"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "dynamic_form_filler",
            "description": "Kolekcjonuje dane do dynamicznego wypełniania formularza PDF na podstawie analizy dokumentu",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_step": {
                        "type": "object",
                        "description": "Aktualny stan wypełniania formularza",
                        "properties": {
                            "current_field": {"type": "string"},
                            "collected_data": {"type": "object"},
                            "remaining_fields": {"type": "array"}
                        }
                    }
                },
                "required": ["current_step"]
            }
        }
    }
]
