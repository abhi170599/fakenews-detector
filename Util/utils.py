import json 
import numpy as np 
import time
import tweepy
import feedparser
import math

from gensim.models.doc2vec import Doc2Vec 
from nltk.tokenize import word_tokenize

from datetime import datetime
from dateutil import parser
from .tweet_bot import TweetBot

from threading import Thread,Barrier 




"""" Data Extractor """
class DataExtractor():

    """
    function to initiailze the extractors
    setup twitter bots
    """

    def __init__(self,config,doc2vec,num_bots,num_hours=30,emdim=50,limit=30):
        
        self.limit = limit
        self.config = config
        self.num_hours = num_hours
        self.emdim     = emdim
        self.num_bots  = num_bots
        self.bot_index = 0
        self.barrier   = Barrier(2)
        self.twitter_bots = []
        self.configure_twitter_bots(self.config)
        self.news_url = "https://news.google.com/rss/search?q={}&hl=en-IN&gl=IN&ceid=IN:en"
        self.doc2vec  = doc2vec
        


    """ function to extract tweets for a query """
    def _get_tweets(self,query=None):

        tweet_bot = self.get_next_bot()

        data = tweet_bot.search(query=query,limit=self.limit)
        
        dynamics_vector = self._get_dynamics(data)

        return dynamics_vector
        

    """ function to extract news for a query """    
    def _get_news(self,query=None):

        news_url = self.news_url.format(query)
        news_url = news_url.replace(" ","%20")

        NewsFeed = feedparser.parse(news_url)

        data = []

        for entry in NewsFeed.entries :
            parsed_time = str(parser.parse(entry.published))
            parsed_time = parsed_time[0:len(parsed_time)-6]
            news_json = {"text":entry.title,
                         "date":parsed_time}
            data.append(news_json)

        dynamics_vector = self._get_dynamics(data)
        return dynamics_vector
        

    """ function to get combined dynamics vector for a query """
    def get_vectors_for_query(self,query=None):

        tweet_vec = None 
        news_vec  = None  

        """ get tweet vectors """
        tweet_vec = self._get_tweets(query)
        news_vec  = self._get_news(query)
        
        
        if tweet_vec is None and news_vec is None:
            
            return None

        elif tweet_vec is None:
            return news_vec

        elif news_vec is None:
            return tweet_vec

        return (tweet_vec+news_vec)/2.0
        
       

    """ function to get tweet dynamics """
    def _get_dynamics(self,data):

         data.sort(key = lambda x:x["date"])

         if len(data)==0:
             return None 

         dynamics = [{"vec":np.ones(self.emdim),"count":0} for i in range(self.num_hours)]        
         init_time = data[0]["date"]

         for i in range(1,len(data)):

            _time = data[i]["date"]
            diff  = self._get_time_difference(init_time,_time)
            if diff<self.num_hours and diff>=0:

                vec = self._get_vectors(data[i]["text"])

                if dynamics[diff]["count"]==0:
                    dynamics[diff]["vec"]=vec
                    dynamics[diff]["count"]+=1
                else:
                    dynamics[diff]["vec"]+=vec
                    dynamics[diff]["count"]+=1

         matrix = []
         for i in range(self.num_hours):
            scaling =  math.log(dynamics[i]["count"]+1)+1
            matrix.append(scaling*dynamics[i]["vec"]/(dynamics[i]["count"]+1))

         return np.array(matrix)    

    """function get time difference in hours """
    def _get_time_difference(self,time1,time2):

        date_format = '%Y-%m-%d %H:%M:%S'
    
        diff = datetime.strptime(time2,date_format) - datetime.strptime(time1,date_format)

        return int(diff.total_seconds()//3600)



    """ function to initialize the tweet bots """
    def configure_twitter_bots(self,config):

        for i in range(self.num_bots):
            bot = TweetBot(config[i])
            self.twitter_bots.append(bot)


    def get_next_bot(self):

        return self.twitter_bots[(self.bot_index+1)%self.num_bots]
    
    def _get_vectors(self,text):

        return self.doc2vec.infer_vector(word_tokenize(text))





         

              
        



            









