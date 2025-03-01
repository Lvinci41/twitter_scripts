import requests
from requests.auth import HTTPBasicAuth


def create_bearer_token(api_key, api_secret_key):
    # The endpoint for generating the Bearer Token
    url = 'https://api.x.com/oauth2/token'
    
    # Set the data for the POST request
    data = {
        'grant_type': 'client_credentials'
    }
    # Make the POST request with basic authentication
    response = requests.post(url, auth=HTTPBasicAuth(api_key, api_secret_key), data=data)

    if response.status_code == 200:
        token_info = response.json()
        return token_info.get('access_token')
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_tweet_text(tweet_url, bearer_token):
    # Extract the tweet ID from the URL
    tweet_id = tweet_url.split('/')[-1]

    # Define the endpoint and parameters
    endpoint_url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    params = {
        "tweet.fields": "text"  # Request only the text field
    }

    # Make the request
    response = requests.get(endpoint_url, headers=headers, params=params)

    if response.status_code == 200:
        tweet_data = response.json()
        return tweet_data.get("data", {}).get("text", "No text found")
    else:
        return f"Error: {response.status_code}, {response.text}"

def get_tweet_metrics(tweet_url, bearer_token):
    # Extract the tweet ID from the URL
    tweet_id = tweet_url.split('/')[-1]

    # Define the endpoint and parameters
    endpoint_url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    params = {
        "tweet.fields": "public_metrics"  # Request public metrics (likes, retweets, views)
    }

    # Make the request
    response = requests.get(endpoint_url, headers=headers, params=params)

    if response.status_code == 200:
        tweet_data = response.json()
        metrics = tweet_data.get("data", {}).get("public_metrics", {})
        return {
            "likes": metrics.get("like_count", 0),
            "retweets": metrics.get("retweet_count", 0),
            "views": metrics.get("impression_count", 0)  # Note: Views may not be available in all endpoints
        }
    else:
        return f"Error: {response.status_code}, {response.text}"

def get_tweet_details_consol(tweet_url, bearer_token):
    # Extract the tweet ID from the URL
    tweet_id = tweet_url.split('/')[-1]

    # Define the endpoint and parameters
    endpoint_url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    params = {
        "tweet.fields": "text,created_at,public_metrics"  # Request text, created_at, and public metrics
    }

    # Make the request
    response = requests.get(endpoint_url, headers=headers, params=params)

    if response.status_code == 200:
        tweet_data = response.json()
        tweet_info = tweet_data.get("data", {})
        
        # Extracting required information
        tweet_text = tweet_info.get("text", "No text found")
        created_at = tweet_info.get("created_at", "No date found")
        metrics = tweet_info.get("public_metrics", {})
        
        return {
            "text": tweet_text,
            "created_at": created_at,
            "likes": metrics.get("like_count", 0),
            "retweets": metrics.get("retweet_count", 0),
            "views": metrics.get("impression_count", 0)  # Note: Views may not be available in all endpoints
        }
    else:
        return f"Error: {response.status_code}, {response.text}"

def get_tweet_id_from_url(tweet_id):
    return tweet_url.split('/')[-1]


if __name__ == '__main__':
    try:
        tweet_url = input("Enter the URL of the tweet: ")
        with open("x_keys.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            keys = list(reader)[1:]
        
        x_key = keys[0]
        x_sk = keys[1]

        print( get_tweet_details_consol(tweet_id, create_bearer_token(x_key, x_sk) ) )
        
    except Exception as e:
        print(f"Error: {e}")



   
