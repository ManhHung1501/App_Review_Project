from utils.appstore_utils import get_token, fetch_reviews
import numpy as np
import time
from utils.minio_utils import init_minio_client, write_json_to_minio

def get_appstore_reviews(country: str, app_id: str) -> list:
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
    object_name = f"appstore/{app_id}_reviews.json"
    
    minio_client = init_minio_client()
    # Ensure the bucket exists
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    write_json_to_minio(minio_client, bucket_name, object_name, all_reviews)

    return all_reviews
