# Dependencies
import matplotlib
matplotlib.use('Agg')
import tweepy
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import style
import time
import os
import numpy as np
style.use('ggplot')

# Import and Initialize Sentiment Analyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

# Twitter API Keys
consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")
access_token = os.getenv("access_token")
access_token_secret = os.getenv("access_token_secret")

# Setup Tweepy API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

# User handle
user = "@BzzOrange"

# define a function to search recent mentions
def search_mentions():
    # Search for all tweets
    tweets = api.search(user, count=50, result_type="recent")
    # generate empty lists
    mention_list = []
    
    # if there are any new tweets
    if tweets["statuses"]:
        # Loop through all tweets
        for tweet in tweets["statuses"]:
            # Get ID, Author and target of most recent tweet directed to me
            if len(tweet['entities']['user_mentions'])>1:
                tweet_id = tweet["id"]
                tweet_author = tweet["user"]["screen_name"]
                target_term = tweet['entities']['user_mentions'][1]['screen_name']
                mention = [target_term, tweet_id, tweet_author]
                mention_list.append(mention)
    return mention_list

# define a function to get up to 100 analyzed targets
def analyzed_targets():
    # generate empty list
    analyzed_list = []
    # get bot's tweets
    bot_tweets = api.home_timeline(count = 200)
    #loop through tweets
    for tweet in bot_tweets:
        if tweet['entities']['user_mentions']:
            analyzed = tweet['entities']['user_mentions'][0]['screen_name']
            analyzed_list.append(analyzed)
    return analyzed_list

# filter out analyzed target from recent mentions and generate a to do list
def filter_to_do_list(mention_list, analyzed_list):
    to_do_list = []
    for mention in mention_list:
        if mention[0] not in analyzed_list:
            to_do_list.append(mention)
    return to_do_list

# define a function to do sentiment analysis
def sentiment_analysis(target):
    # get 500 tweets put texts into a list
    tweet_texts = []
    for x in range(25):
        public_tweets = api.user_timeline(target, page=x)
        # Loop through all tweets
        for tweet in public_tweets:
            # Store Tweet in Array
            tweet_texts.append(tweet["text"])
    # generate empty list
    sentiment = []
    # Loop through all text 
    for text in tweet_texts:
        # Run Vader Analysis on each tweet
        results = analyzer.polarity_scores(text)
        compound = results["compound"]
        sentiment.append(compound)
    return sentiment

# define a function to plot analysis results
def plot_analysis_data(sentiment, target):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(np.arange(-len(sentiment),0),
         sentiment, marker="o", linewidth=0.5,
         alpha=0.8)

    # # Incorporate the other graph properties
    now = datetime.now()
    now = now.strftime("%m/%d/%y")
    plt.title(f"Sentiment Analysis of Tweets ({now}) for @{target}")
    plt.ylabel("Tweet Polarity")
    plt.xlabel("Tweets Ago")
    plt.savefig("fig.png")

# define a funtion to send out tweet with analysis data
def send_out_tweet(target, user):
    msg = f"New Tweet Analysis: @{target} (Thx @{user}!!)"
    api.update_with_media("fig.png", msg)

# define a function to update twitter
def update_twitter():
    mention_list = search_mentions()
    analyzed_list = analyzed_targets()
    to_do_list = filter_to_do_list(mention_list, analyzed_list)
    if to_do_list:
        for to_do in to_do_list:
            target = to_do[0]
            user = to_do[2]
            sentiment = sentiment_analysis(target)
            plot_analysis_data(sentiment, target)
            send_out_tweet(target, user)
            time.sleep(5)

update_twitter()
