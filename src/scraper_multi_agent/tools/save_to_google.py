import gspread
import pandas as pd
import logging
import traceback
import os # Import os for path joining
from gspread.exceptions import WorksheetNotFound, NoValidUrlKeyFound
from gspread.utils import extract_id_from_url
from urllib.parse import urlparse, unquote # Import for URL parsing
from google.oauth2.service_account import Credentials
from agents import function_tool

# GOOGLE_CREDENTIALS_FILE = os.path.join(os.getcwd(), "new_gc.json")
GOOGLE_CREDENTIALS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "new_gc.json"))
# Authenticate with Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=scope)
client = gspread.authorize(creds)

@function_tool
def save_to_sheet(sheet_url: str, products: list, source_url: str) -> str:
    """
    Saves product data to a Google Sheet, Extracts sheet ID from the sheet URL and 
    generates tab name from the source URL.

    Args:
        sheet_url: The URL of the Google Sheet
        products: List of product dictionaries to save
        source_url: The URL of the page where the products were scraped from.

    Returns:
        Status message indicating success or failure
    """
    if not isinstance(client, gspread.Client):
         logging.error("Invalid client provided to save_to_sheet.")
         return "Failed to save to Google Sheet: Invalid client provided."

    if not products:
        logging.warning("No products to save for source URL: %s", source_url)
        return f"No products to save for source URL: {source_url}"

    try:
        # --- Extract Tab Name from Source URL ---
        parsed_url = urlparse(source_url)
        # Get the last part of the path and remove leading/trailing slashes
        path_segments = [segment for segment in parsed_url.path.split('/') if segment]
        if path_segments:
            # Decode URL-encoded characters and replace hyphens/underscores with spaces
            dynamic_tab_name = unquote(path_segments[-1]).replace('-', ' ').replace('_', ' ')
            # Capitalize the first letter of each word for better readability
            dynamic_tab_name = dynamic_tab_name.title()
            # Truncate if necessary (Google Sheets tab names have limits)
            dynamic_tab_name = dynamic_tab_name[:100] # Google Sheets limit is 100 characters
        else:
            dynamic_tab_name = "Scraped Data" # Default if path is empty


        # --- Google Sheets Interaction ---
        # Extract the sheet ID from the sheet URL
        sheet_id = extract_id_from_url(sheet_url)

        # Open the spreadsheet using the provided client and extracted ID
        spreadsheet = client.open_by_key(sheet_id)

        # Remove existing worksheet with the dynamic tab name if it exists
        try:
            worksheet = spreadsheet.worksheet(dynamic_tab_name)
            logging.info(f"Deleting existing worksheet: {dynamic_tab_name}")
            spreadsheet.del_worksheet(worksheet)
        except WorksheetNotFound:
            logging.info(f"Worksheet '{dynamic_tab_name}' not found, proceeding to create.")
            pass
        except Exception as e:
             logging.warning(f"Could not delete existing worksheet '{dynamic_tab_name}': {e}. Attempting to create anyway.")
             # Continue attempting to create, in case the error was temporary

        # Create new worksheet
        logging.info(f"Creating new worksheet: {dynamic_tab_name}")
        # Adjust rows/cols if you expect very large datasets
        worksheet = spreadsheet.add_worksheet(title=dynamic_tab_name, rows=1000, cols=20)

        # Convert data to DataFrame and update sheet
        df = pd.DataFrame(products)

        # Ensure consistent columns across tabs by reindexing (optional but recommended)
        # If different pages have slightly different product data fields, this helps
        # You'll need to define a master list of expected columns or handle missing data.
        # For this example, we'll just use the columns found in the current data.

        logging.info(f"Updating worksheet '{dynamic_tab_name}' with {len(products)} rows.")
        # Add headers and data
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())

        return f"Successfully saved {len(products)} products from {source_url} to '{dynamic_tab_name}' worksheet"

    except NoValidUrlKeyFound:
        error_msg = f"Failed to save to Google Sheet: The provided Sheet URL does not contain a valid Google Sheet ID. Please check the URL."
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Failed to save to Google Sheet: {str(e)}\nTraceback:\n{traceback.format_exc()}"
        logging.error(error_msg)
        return error_msg
