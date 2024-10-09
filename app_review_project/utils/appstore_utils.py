import random
import requests
import re
import time
from tqdm import tqdm
import logging

user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        ]



def get_token(country:str , app_id: str):

    """
    Retrieves the bearer token required for API requests
    Regex adapted from base.py of https://github.com/cowboy-bebug/app-store-scraper
    """

    response = requests.get(f'https://apps.apple.com/{country}/app/app_name/id{app_id}', 
                            headers = {'User-Agent': random.choice(user_agents)},
                            )
    
    if response.status_code != 200:
        logging.info(f"GET request failed. Response: {response.status_code} {response.reason}")
        return
    
    tags = response.text.splitlines()
    for tag in tags:
        if re.match(r"<meta.+web-experience-app/config/environment", tag):
            token = re.search(r"token%22%3A%22(.+?)%22", tag).group(1)
    
    logging.info(f"Bearer {token}")
    return token
    
def fetch_reviews(country:str , app_id: str, token: str, offset: str = '1'):

    """
    Fetches reviews for a given app from the Apple App Store API.

    - Default sleep after each call to reduce risk of rate limiting
    - Retry with increasing backoff if rate-limited (429)
    - No known ability to sort by date, but the higher the offset, the older the reviews tend to be
    """

    ## Define request headers and params ------------------------------------
    landingUrl = f'https://apps.apple.com/{country}/app/app_name/id{app_id}'
    requestUrl = f'https://amp-api.apps.apple.com/v1/catalog/{country}/apps/{app_id}/reviews'

    headers = {
        'Accept': 'application/json',
        'Authorization': f'bearer {token}',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://apps.apple.com',
        'Referer': landingUrl,
        'User-Agent': random.choice(user_agents)
        }

    params = (
        ('l', 'en-GB'),                 # language
        ('offset', str(offset)),        # paginate this offset
        ('limit', '20'),                # max valid is 20
        ('platform', 'web'),
        ('additionalPlatforms', 'appletv,ipad,iphone,mac')
        )

    ## Perform request & exception handling ----------------------------------
    retry_count = 0
    MAX_RETRIES = 5
    BASE_DELAY_SECS = 10
    # Assign dummy variables in case of GET failure
    result = {'data': [], 'next': None}
    reviews = []

    while retry_count < MAX_RETRIES:

        # Perform request
        response = requests.get(requestUrl, headers=headers, params=params)

        # SUCCESS
        # Parse response as JSON and exit loop if request was successful
        if response.status_code == 200:
            result = response.json()
            reviews = result['data']
            if len(reviews) < 20:
                logging.info(f"{len(reviews)} reviews scraped. This is fewer than the expected 20.")
            break

        # FAILURE
        elif response.status_code != 200:
            # RATE LIMITED
            if response.status_code == 429:
                # Perform backoff using retry_count as the backoff factor
                retry_count += 1
                backoff_time = BASE_DELAY_SECS * retry_count
                logging.info(f"Rate limited! Retrying ({retry_count}/{MAX_RETRIES}) after {backoff_time} seconds...")
                
                with tqdm(total=backoff_time, unit="sec", ncols=50) as pbar:
                    for _ in range(backoff_time):
                        time.sleep(1)
                        pbar.update(1)
                continue

            # NOT FOUND
            elif response.status_code == 404:
                logging.info(f"{response.status_code} {response.reason}. There are no more reviews.")
                break
                
            else:
                logging.info(f"GET request failed. Response: {response.status_code} {response.reason}")

    ## Final output ---------------------------------------------------------
    # Get pagination offset for next request
    if 'next' in result and result['next'] is not None:
        offset = re.search("^.+offset=([0-9]+).*$", result['next']).group(1)
        logging.info(f"Offset: {offset}")
    else:
        offset = None
        logging.info("No offset found.")

    # Append offset, number of reviews in batch, and app_id
    for rev in reviews:
        rev['offset'] = offset
        rev['n_batch'] = len(reviews)
        rev['app_id'] = app_id

    # Default sleep to decrease rate of calls
    time.sleep(0.5)
    return reviews, offset, response.status_code 
