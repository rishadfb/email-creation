from typing import Dict, Optional
import requests
from ..core.config import get_api_key
from ..core.exceptions import AIServiceError, ContactDataError

class ApolloClient:
    """Client for interacting with the Apollo API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Apollo client with an API key"""
        self.api_key = api_key or get_api_key("APOLLO_API_KEY")
        if not self.api_key:
            raise AIServiceError("API key is required", "Apollo")
        
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def enrich_contact(self, contact: Dict) -> Dict:
        """
        Enrich a contact with additional information from Apollo
        
        Args:
            contact: Dictionary containing contact information
                    Must include either email or (first_name, company)
        
        Returns:
            Enriched contact dictionary
        """
        # Endpoint for enrichment
        endpoint = f"{self.base_url}/people/match"
        
        # Prepare search criteria
        search_params = {
            "email": contact.get("email"),
            "first_name": contact.get("first_name"),
            "organization_name": contact.get("company")
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=search_params
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get("person"):
                return contact
            
            # Update contact with enriched data
            enriched = data["person"]
            updates = {
                "job_title": enriched.get("title") or contact.get("job_title", ""),
                "company": enriched.get("organization", {}).get("name") or contact.get("company", ""),
                "industry": enriched.get("organization", {}).get("industry") or contact.get("industry", ""),
                "location": f"{enriched.get('city', '')}, {enriched.get('state', '')}" if enriched.get('city') else contact.get("location", "")
            }
            
            return {**contact, **updates}
            
        except requests.exceptions.RequestException as e:
            # Log the error but don't raise an exception to keep the application running
            # Just return the original contact without enrichment
            error_msg = f"Error enriching contact {contact.get('email')}: {str(e)}"
            # We could raise an exception here, but it's better to degrade gracefully
            # raise ContactDataError(error_msg)
            return contact 