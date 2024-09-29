import datetime
import os.path
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

TARGET_STRING = "PA"
START_DATE = '2023-09-29T00:00:00Z'  # Start date in RFC3339 forma


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        print("Getting all events")
        events_result = service.events().list(
            calendarId="primary",
            q=TARGET_STRING,
            timeMin=START_DATE,
            singleEvents=True,
            orderBy="startTime",
            maxResults=2500,     # maximum number of events to return (up to 2500)
        ).execute()
        events = events_result.get("items", [])

        # Filter events containing the string "TEST"
        filtered_events = []
        total_duration_spent = datetime.timedelta()
        total_duration_planned = datetime.timedelta()

        for event in events:
            if TARGET_STRING in event.get("summary", ""):
                start = event["start"].get(
                    "dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                start_dt = datetime.datetime.fromisoformat(start)
                end_dt = datetime.datetime.fromisoformat(end)
                duration = end_dt - start_dt

                # Check if the event is in the past or future
                if end_dt < datetime.datetime.now(datetime.timezone.utc):
                    total_duration_spent += duration
                else:
                    total_duration_planned += duration

                filtered_events.append({
                    "summary": event["summary"],
                    "start": start,
                    "end": end,
                    "duration": duration
                })

                # Create a pandas DataFrame
        df = pd.DataFrame(filtered_events)
        print(df)

        print(
            f"Total time spent on past events containing '{TARGET_STRING}': {total_duration_spent}")
        print(
            f"Total time planned for future events containing '{TARGET_STRING}': {total_duration_planned}")

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
