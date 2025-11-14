"""
Google Calendar Integration Service for MindLab Health
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import os

# Google Calendar imports (will be available after pip install)
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    logging.warning("Google Calendar libraries not available. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """Service for integrating with Google Calendar API"""
    
    # If modifying these scopes, delete the file token.json
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.enabled = GOOGLE_CALENDAR_AVAILABLE and os.path.exists(credentials_file)
        
        if self.enabled:
            self._initialize_service()
        else:
            logger.warning("Google Calendar integration disabled - missing dependencies or credentials")
    
    def _initialize_service(self):
        """Initialize the Google Calendar service with authentication"""
        if not GOOGLE_CALENDAR_AVAILABLE:
            return
            
        try:
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            self.enabled = False
    
    def create_event(self, appointment_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a Google Calendar event for an appointment
        
        Args:
            appointment_data: Dictionary containing appointment details
            
        Returns:
            Google Calendar event ID if successful, None otherwise
        """
        if not self.enabled or not self.service:
            logger.warning("Google Calendar service not available")
            return None
        
        try:
            # Extract appointment details
            start_time = appointment_data['appointment_datetime']
            duration = appointment_data.get('duration_minutes', 60)
            end_time = start_time + timedelta(minutes=duration)
            
            # Create event object
            event = {
                'summary': f"Therapy Appointment - {appointment_data.get('appointment_type', 'Consultation')}",
                'description': f"""
MindLab Health Appointment

Type: {appointment_data.get('appointment_type', 'Consultation')}
Patient: {appointment_data.get('patient_name', 'N/A')}
Therapist: {appointment_data.get('therapist_name', 'N/A')}
Location: {appointment_data.get('location', 'Office Visit')}

Notes: {appointment_data.get('notes', 'No additional notes')}

Appointment ID: {appointment_data.get('appointment_id')}
                """.strip(),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 60},  # 1 hour before
                        {'method': 'popup', 'minutes': 15},  # 15 minutes before
                    ],
                },
            }
            
            # Add attendees if email addresses are provided
            if appointment_data.get('patient_email'):
                event['attendees'].append({'email': appointment_data['patient_email']})
            if appointment_data.get('therapist_email'):
                event['attendees'].append({'email': appointment_data['therapist_email']})
            
            # Create the event
            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            logger.info(f"Google Calendar event created: {created_event.get('id')}")
            return created_event.get('id')
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return None
    
    def update_event(self, event_id: str, appointment_data: Dict[str, Any]) -> bool:
        """
        Update an existing Google Calendar event
        
        Args:
            event_id: Google Calendar event ID
            appointment_data: Updated appointment details
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.service:
            return False
        
        try:
            # Get existing event
            existing_event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Update event details
            start_time = appointment_data['appointment_datetime']
            duration = appointment_data.get('duration_minutes', 60)
            end_time = start_time + timedelta(minutes=duration)
            
            existing_event['summary'] = f"Therapy Appointment - {appointment_data.get('appointment_type', 'Consultation')}"
            existing_event['start']['dateTime'] = start_time.isoformat()
            existing_event['end']['dateTime'] = end_time.isoformat()
            existing_event['description'] = f"""
MindLab Health Appointment

Type: {appointment_data.get('appointment_type', 'Consultation')}
Patient: {appointment_data.get('patient_name', 'N/A')}
Therapist: {appointment_data.get('therapist_name', 'N/A')}
Location: {appointment_data.get('location', 'Office Visit')}

Notes: {appointment_data.get('notes', 'No additional notes')}

Appointment ID: {appointment_data.get('appointment_id')}
            """.strip()
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId='primary', 
                eventId=event_id, 
                body=existing_event
            ).execute()
            
            logger.info(f"Google Calendar event updated: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Google Calendar API error updating event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating calendar event: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a Google Calendar event
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.service:
            return False
        
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            logger.info(f"Google Calendar event deleted: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Google Calendar API error deleting event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting calendar event: {e}")
            return False
    
    def get_calendar_availability(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get calendar availability for a date range
        
        Args:
            start_date: Start of the date range
            end_date: End of the date range
            
        Returns:
            Dictionary with availability information
        """
        if not self.enabled or not self.service:
            return {"available": False, "message": "Calendar service not available"}
        
        try:
            # Get busy times
            freebusy_request = {
                'timeMin': start_date.isoformat(),
                'timeMax': end_date.isoformat(),
                'items': [{'id': 'primary'}]
            }
            
            freebusy_result = self.service.freebusy().query(body=freebusy_request).execute()
            busy_times = freebusy_result.get('calendars', {}).get('primary', {}).get('busy', [])
            
            return {
                "available": True,
                "busy_times": busy_times,
                "message": "Calendar availability retrieved successfully"
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error getting availability: {e}")
            return {"available": False, "message": f"API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting calendar availability: {e}")
            return {"available": False, "message": f"Error: {e}"}

# Global instance
calendar_service = GoogleCalendarService()