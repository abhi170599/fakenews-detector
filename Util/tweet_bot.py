import tweepy


class TweetBot():

    def __init__(self,creds):

        self.cred = creds
        self.auth = tweepy.OAuthHandler(
            self.cred["CONSUMER_KEY"],
            self.cred["CONSUMER_SEC"]
        )

        self.auth.set_access_token(
            self.cred["ACCESS_TOKEN"],
            self.cred["ACCESS_SECRT"])

        self.api = tweepy.API(self.auth)


    def search(self,query,limit=100):
        
        data = []
        
        try:

            tweets = tweepy.Cursor(self.api.search,q=query,lang='en').items(limit) 
    
        
            for tweet in tweets:
                tweet_json = {}

                tweet_text = str(tweet.text)
                tweet_date = str(tweet.created_at)

                tweet_json["text"]=tweet_text 
                tweet_json["date"]=tweet_date 

                data.append(tweet_json)

            return data
        except:
            return data           

        