from utils.appstore_utils import get_token, fetch_reviews
import numpy as np
import time
from utils.minio_utils import init_minio_client, write_json_to_minio
import requests
from bs4 import BeautifulSoup

def get_appstore_reviews_app(country: str, app_id: str) -> list:
    all_reviews = []
    offset = '1'
    # MAX_REVIEWS = max_reviews+21

    start_time = time.time()
 
    token = get_token(country, app_id)
    while (offset != None):
        reviews, offset, response_code = fetch_reviews(country=country, 
                                                    app_id=app_id, 
                                                    token=token, 
                                                    offset=offset)
        print(f"Current response code: {response_code} | Next offset: {offset}.")
        all_reviews.extend(reviews)


    print(f"Completed scraping {len(all_reviews)} reviews in {(time.time() - start_time)/60:.2f} minutes.")
    # --------------------------------------------------------------------------

    # Check max offset
    max_offset = np.nanmax([int(rev['offset']) for rev in all_reviews 
                            if rev['offset'] is not None and rev['n_batch'] == 20])
    print(f"Backed up till offset {max_offset}.")

    # Define bucket and object name
    bucket_name = "app-reviews"
    object_name = f"appstore/app/{app_id}_reviews.json"
    
    minio_client = init_minio_client()
    # Ensure the bucket exists
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    write_json_to_minio(minio_client, bucket_name, object_name, all_reviews)

    return all_reviews

def get_reviews_appstore_web(country: str, app_id: str) -> dict:
    start_time = time.time()
    print(f"Begin to scrape reviews of {app_id} from AppStore Web")

    url = f"https://apps.apple.com/{country}/app/'app'/id{app_id}?see-all=reviews"

    # Set headers to mimic a real browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
    }

    # Send a request to the reviews page
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'lxml')

        # Find all review containers
        reviews = soup.find_all('div', class_='we-customer-review')
        # Loop through each review and extract information
        all_reviews = []

        for review in reviews:
            # Extract review title
            title = review.find('h3', class_='we-customer-review__title').get_text(strip=True)
            
            # Extract review rating (convert stars to number)
            rating_tag = review.find('figure', class_='we-customer-review__rating')
            rating = rating_tag['aria-label'].split(' ')[0]
            
            # Extract review text
            review_text = review.find('blockquote', class_='we-customer-review__body').get_text(strip=True)
            
            # Extract reviewer's name
            user = review.find('span', class_='we-customer-review__user').get_text(strip=True)
            
            # Extract review date
            date = review.find('time')['datetime']
            
            all_reviews.append(
                {
                    'user_name': user,
                    'title': title,
                    'rating': rating,
                    'review': review_text,
                    'review_date': date,
                    'app_id': app_id
                }
            )
        
        print(f"Completed scraping {len(reviews)} reviews in {(time.time() - start_time)/60:.2f} minutes.")

        # Define bucket and object name
        bucket_name = "app-reviews"
        object_name = f"appstore/web/{app_id}_reviews.json"
        
        minio_client = init_minio_client()
        # Ensure the bucket exists
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        write_json_to_minio(minio_client, bucket_name, object_name, all_reviews)
        return all_reviews
    else:
        print(f"Failed to retrieve the reviews. Status code: {response.status_code}")