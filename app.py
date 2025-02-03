from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from textblob import TextBlob
import matplotlib.pyplot as plt
import csv
import os

# Replace with your actual API key and video ID
API_KEY = "AIzaSyC6A02We3z0BIHZfUFS06_hV7Y7vBtKkH4"
video_id = "zSDgwvQoSHg"

def get_youtube_comments(video_id, max_results=50):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    comments = []
    next_page_token = None  

    while True:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                textFormat="plainText",
                pageToken=next_page_token
            )
            response = request.execute()

            # Check if 'items' exists in the response and is not empty
            if "items" not in response or not response["items"]:
                print("No comments found in the response.")
                break

            for item in response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)

            # Check if there's another page of comments
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        except HttpError as e:
            print(f"An error occurred: {e}")
            print(f"Error details: {e.content}")
            break

    return comments

# Fetch comments
comments = get_youtube_comments(video_id)

if comments:
    print(f"Fetched {len(comments)} comments successfully.")
else:
    print("No comments were fetched.")

# Perform Sentiment Analysis
sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
sentiment_results = []

for comment in comments:
    sentiment_score = TextBlob(comment).sentiment.polarity  # Score between -1 and 1
    if sentiment_score > 0:
        sentiment_label = "Positive"
    elif sentiment_score < 0:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"
    
    sentiment_counts[sentiment_label] += 1
    sentiment_results.append((comment, sentiment_label))

# Save results to a CSV file
with open("youtube_sentiment_analysis.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Comment", "Sentiment"])
    for comment, sentiment in sentiment_results:
        writer.writerow([comment, sentiment])

print("Sentiment analysis completed! Results saved in youtube_sentiment_analysis.csv")

# Visualization: Pie Chart
def visualize_sentiments(sentiments):
    total = sum(sentiments.values())
    if total == 0:
        print("No sentiment data to display in pie chart.")
        return

    labels = list(sentiments.keys())
    sizes = list(sentiments.values())

    # Define an autopct function that avoids division by zero
    def autopct_func(pct):
        return f'{pct:.1f}%' if total > 0 else '0%'

    plt.pie(sizes, labels=labels, autopct=autopct_func, startangle=140, colors=["green", "gray", "red"])
    plt.title('Sentiment Analysis of YouTube Comments')
    plt.show()

visualize_sentiments(sentiment_counts)

# Save the comments to a CSV file (if needed)
def save_to_csv(comments, filename='comments.csv'):
    if comments:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Comment"])
            for comment in comments:
                writer.writerow([comment])
        print(f"Saved comments to {filename}")
    else:
        print("No comments to save.")

save_to_csv(comments)
