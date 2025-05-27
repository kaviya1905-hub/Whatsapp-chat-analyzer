# helper.py

import pandas as pd
import re
from wordcloud import WordCloud
import emoji
from collections import Counter
import matplotlib.pyplot as plt

def preprocess(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = file.readlines()

    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) (AM|PM) - ([^:]+): (.+)'
    messages = []
    for line in data:
        match = re.match(pattern, line)
        if match:
            date, time, am_pm, sender, message = match.groups()
            full_time = time + " " + am_pm
            messages.append([date, full_time, sender, message])
    df = pd.DataFrame(messages, columns=['Date', 'Time', 'Sender', 'Message'])
    return df

def generate_wordcloud(text):
    wc = WordCloud(width=800, height=400, background_color='white')
    return wc.generate(text)

def extract_emojis(messages):
    emojis = []
    for message in messages:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    return Counter(emojis).most_common(10)
def user_stats(df):
    return df['Sender'].value_counts()

def daily_timeline(df):
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    return df.groupby(df['Date'].dt.date).size()

def monthly_timeline(df):
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    return df.groupby(df['Date'].dt.to_period("M")).size()
