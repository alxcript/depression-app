import tweepy

class TwitterUserManager:
    def __init__(self, api_key, api_secret_key, access_token, access_token_secret):
        auth = tweepy.OAuth1UserHandler(api_key, api_secret_key, access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def search_users(self, query, count=10):
        users = []
        for user in tweepy.Cursor(self.api.search_users, q=query, count=count).items(count):
            user_data = {
                'id': user.id,
                'name': user.name,
                'screen_name': user.screen_name,
                'profile_image_url': user.profile_image_url_https
            }
            users.append(user_data)
        return users

    def get_user(self, user_id):
        user = self.api.get_user(user_id)
        user_data = {
            'id': user.id,
            'name': user.name,
            'screen_name': user.screen_name,
            'description': user.description,
            'location': user.location,
            'followers_count': user.followers_count,
            'friends_count': user.friends_count,
            'statuses_count': user.statuses_count,
            'profile_image_url': user.profile_image_url,
            'profile_banner_url': user.profile_banner_url
        }
        return user_data
    
    def get_tweets(self, user_id):
        tweets = []
        for tweet in  self.api.user_timeline(user_id=user_id, 
            count=150,
            include_rts = False,
            # Necessary to keep full_text 
            # otherwise only the first 140 words are extracted
            tweet_mode = 'extended'
            ):
            tweet_data = {
                'full_text': tweet.full_text,
                'created_at': tweet.created_at
            }
            tweets.append(tweet_data)
        return tweets
