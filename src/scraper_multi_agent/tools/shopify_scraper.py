from agents import function_tool
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests, re, logging, json


@function_tool
def scrape_shopify_collection(url: str) -> list:
    """
    Scrapes products from a Shopify collection URL and returns formatted product data
    Args:
        url: The Shopify collection URL to scrape
    Returns:
        List of product dictionaries containing Title, Price, and Description
    """
    # Extract collection handle
    path = urlparse(url).path
    match = re.search(r"/collections/([^/?#]+)", path)
    if not match:
        return []
    
    collection_handle = match.group(1)
    json_url = f"https://{urlparse(url).netloc}/collections/{collection_handle}/products.json"
    
    try:
        response = requests.get(json_url)
        response.raise_for_status()
        products = response.json().get("products", [])
        
        formatted_products = []
        for product in products:
            title = product.get("title", "")
            price = product.get("variants", [{}])[0].get("price", "")
            description_html = product.get('body_html', '')
            soup = BeautifulSoup(description_html, "html.parser")
            description = soup.get_text(separator=" ", strip=True)
            
            formatted_products.append({
                "Title": title,
                "Price": price,
                "Description": description,
            })
        # print(f"FORMATTED OUTPUT FROM TOOL {formatted_products}")
        return formatted_products
        
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return []
    

@function_tool
def extract_json_tool(input_string: str) -> list | dict | None:
    """
    Extracts a JSON object from a string enclosed in triple backticks (```json ... ```).

    Args:
        input_string: The input string potentially containing a JSON block.

    Returns:
        The extracted Python object (usually a dictionary or list), or None if no
        valid JSON block is found or parsing fails.
    """
    # Use regex to find the JSON block enclosed in ```json and ```
    # Corrected regex to handle newline after ```json  
    match = re.search(r"```json\s*\n?(.*?)\s*```", input_string, re.DOTALL)  

    extracted_json_string = None  
    if match:  
        # Group 1 (.*?) captures the content between the backticks  
        extracted_json_string = match.group(1).strip()  
    else:  
        # If no ```json ... ``` block found, return None  
        return None  

    if extracted_json_string:  
        try:  
            # Attempt to parse the extracted string as JSON  
            extracted_object = json.loads(extracted_json_string)  
            # Return the successfully parsed object  
            return extracted_object  
        except json.JSONDecodeError:  
            # If decoding fails, return None  
            return None  
        except Exception:  
             # Catch any other unexpected errors and return None  
             return None  
    else:  
        # If the extracted string is empty after stripping, return None  
        return None  

