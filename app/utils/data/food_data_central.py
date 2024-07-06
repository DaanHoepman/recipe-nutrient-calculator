import requests
import json

from app.utils.exceptions import APIRequestError, APISearchError
from app.utils.data import FDC_API_KEY, FDC_SEARCH_URL, FDC_MATCH_URL, FDC_BULK_MATCH_URL

#--------------------

def search(query: str, dataType: list[str] = ['Foundation', 'SR Legacy'], pageSize: int = 200) -> dict:
    """
    This function searches the FoodData Central API for a given query and returns a dictionary containing the results.

    Arguments:
        query (str): The food name query to search for.
        dataType (list[str]): The type of data to search for, possible values: 'Foundation', 'SR Legacy', 'Branded', 'Survey (FNDDS)'. The default is ['Foundation', 'SR Legacy'].
        pageSize (int): The number of results to return, possible values: integer between 1 and 200. The default is 200.

    Returns:
        dict: The API response.

    Raises:
        APIRequestError: The API request failed.
        APISearchError: The API response could not be parsed.
    """

    # Set parameters for the API request
    params = {
        'api_key': FDC_API_KEY,
        'query': query,
        'dataType': dataType,
        'pageSize': pageSize
        }

    # Make the API request
    response = requests.get(FDC_SEARCH_URL, params=params)

    # Check if the API request was successful
    if response.status_code != 200:
        raise APIRequestError(f"API request failed with status code {response.status_code}")
    
    # Parse the API response
    try:
        return json.loads(response.content)
    except:
        raise APISearchError("API response could not be parsed")



def match(fdcId: str, format: str = 'full') -> dict:
    """
    This function searches the FoodData Central API for a given FDC ID and returns a dictionary containing the results.

    Arguments:
        fdcId (str): The FDC ID to search for.
        format (str): The format of the response, possible values: 'full', 'abridged'. The default is 'full'.

    Returns:
        dict: The API response.

    Raises:
        APIRequestError: The API request failed.
        APISearchError: The API response could not be parsed.
    """

    # Set parameters for the API request
    url = f"{FDC_MATCH_URL}/{fdcId}"
    params = {
        'api_key': FDC_API_KEY,
        'format': format
        }
    
    # Make the API request
    response = requests.get(url, params=params)

    # Check if the API request was successful
    if response.status_code != 200:
        raise APIRequestError(f"API request failed with status code {response.status_code}")
    
    # Parse the API response
    try:
        return json.loads(response.content)
    except:
        raise APISearchError("API response could not be parsed")
    


def bulk_match(fdcIds: list[str], format: str = 'full') -> list[dict]:
    """
    This function searches the FoodData Central API for a list of given FDC IDs and returns a list of dictionaries containing the results.

    Arguments:
        fdcIds (list[str]): The list of FDC IDs to search for.
        format (str): The format of the response, possible values: 'full', 'abridged'. The default is 'full'.

    Returns:
        list[dict]: The API response.

    Raises:
        APIRequestError: The API request failed.
        APISearchError: The API response could not be parsed.
    """

    # Set parameters for the API request
    params = {
        'api_key': FDC_API_KEY,
        'fdcIds': fdcIds,
        'format': format
        }
    
    # Make the API request
    response = requests.get(FDC_BULK_MATCH_URL, params=params)

    # Check if the API request was successful
    if response.status_code != 200:
        raise APIRequestError(f"API request failed with status code {response.status_code}")
    
    # Parse the API response
    try:
        return json.loads(response.content)
    except:
        raise APISearchError("API response could not be parsed")

