import praw
import config
import time
import os
import requests
import pandas
from scrape_data import scrape_stats

def bot_login():
    print("Logging in...")
    r = praw.Reddit(username = config.username,
            password = config.password,
            client_id = config.client_id,
            client_secret = config.client_secret,
            user_agent="Display player stats this season")
    print("Logged in")

    return r

def run_bot(r, comments_replied_to):
    #print("Obtaining 25 comments")
    try:
        for comment in r.subreddit('reddevils+soccer+test').comments(limit=25):
            if "!statsbot" in comment.body and comment.id not in comments_replied_to and comment.author != r.user.me():
                print ("String with \"!statsbot\" found in comment")

                reply = parse_data(comment.body)

                comment.reply(reply)
                print("replied to comment" + comment.id)

                comments_replied_to.append(comment.id)

                with open ("comments_replied_to.txt", "a") as f:
                    f.write(comment.id + "\n")

    except:
        pass
    print("Sleeping for 10 seconds")
    #Sleep for 10 seconds
    time.sleep(10)

def get_saved_comments():
    if not os.path.isfile("comments_replied_to.txt"):
        comments_replied_to = []
    else:
        with open("comments_replied_to.txt","r") as f:
                comments_replied_to = f.read()
                comments_replied_to = comments_replied_to.split("\n")
                comments_replied_to = list(filter(None, comments_replied_to))
    return comments_replied_to


def parse_data(comment):

    a = comment.split(',')
    p = a[1]
    df = scrape_stats(p)

    if df is not None:
        df = df.replace(to_replace=r'-', value='00', regex=True)
        df = df.replace(to_replace=r'\.', value='', regex=True)

        df['MinutesPlayed'] = df['MinutesPlayed'].str.slice_replace(-1)
        df[['Goals', 'Assists','Games Played','MinutesPlayed']] = df[['Goals', 'Assists','Games Played','MinutesPlayed']].astype(float)

        goal_sum = int(df['Goals'].sum())
        assist_sum = int(df['Assists'].sum())
        matches = int(df['Games Played'].sum())
        minutes =int (df['MinutesPlayed'].sum())
        goal_cont = goal_sum+assist_sum
        if goal_cont >0:
            min_per_goal_cont = int(round(minutes/goal_cont))
        else:
            min_per_goal_cont = "N/A"
        league = df.at[0,'Competition']
        league_goals = int(df.at[0,'Goals'])
        league_games = int(df.at[0,'Games Played'])
        league_assists = int(df.at[0,'Assists'])

        comment_reply = "In the "+league+""+p+" has played "+str(league_games)+" games scoring "+str(league_goals)+ \
                                " goals while providing "+str(league_assists)+" assists.\n\nIn all Competitons- Games Played: "+str(matches)+ \
                                ", scoring "+str(goal_sum)+" goals and "+str(assist_sum)+" assists providing a goal contribution(g+a) every "+ \
                                str(min_per_goal_cont)+" minutes."
        return comment_reply
    else:
            return "Can't find the data for this player"


r = bot_login()
comments_replied_to = get_saved_comments()
#print(comments_replied_to)

while True:
    run_bot(r, comments_replied_to)
