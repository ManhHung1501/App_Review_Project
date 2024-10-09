from google_play_scraper import Sort, reviews_all
from utils.minio_utils import init_minio_client, write_json_to_minio
import time
import logging

def get_google_play_reviews(app_id: str) -> list:
    start_time = time.time()
    logging.info(f"Begin to scrape reviews of {app_id} from Google play")
    try:
        reviews = reviews_all(
            app_id,
            sleep_milliseconds=0,
            sort=Sort.NEWEST
        )
    except Exception as e:
        logging.error(f"Failed to crawl data from google play with error {e}")

    for entry in reviews:
        entry['app_id'] = app_id
        entry['at'] = entry['at'].strftime('%Y-%m-%d %H:%M:%S')
        entry['repliedAt'] = entry['repliedAt'].strftime('%Y-%m-%d %H:%M:%S')

    # Define bucket and object name
    bucket_name = "app-reviews"
    object_name = f"google_play/{app_id}_reviews.json"
    
    minio_client = init_minio_client()
    # Ensure the bucket exists
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    write_json_to_minio(minio_client, bucket_name, object_name, reviews)

    logging.info(f"Completed scraping {len(reviews)} reviews in {(time.time() - start_time)/60:.2f} minutes.")
    return reviews
