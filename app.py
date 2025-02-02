import streamlit as st
from googleapiclient.discovery import build
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd

# Streamlit UI Title
st.title("YouTube Comment Sentiment Analysis")
st.write("Enter a YouTube Video ID below to analyze comments:")

# Input for YouTube Video ID
video_id = st.text_input("YouTube Video ID")

# YouTube API Key (Replace with your own)
API_KEY = "YOUR_YOUTUBE_API_KEY"

# Function to fetch comments
def get_youtube_comments(video_id, max_results=100):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    )
    response = request.execute()

    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)

    return comments

# Sentiment Analysis Function
def analyze_sentiments(comments):
    sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    sentiment_results = []

    for comment in comments:
        sentiment_score = TextBlob(comment).sentiment.polarity
        sentiment_label = (
            "Positive" if sentiment_score > 0 else
            "Negative" if sentiment_score < 0 else
            "Neutral"
        )
        sentiment_counts[sentiment_label] += 1
        sentiment_results.append([comment, sentiment_label])

    return sentiment_results, sentiment_counts

# Button to Fetch and Analyze Comments
if st.button("Analyze Comments"):
    if video_id:
        with st.spinner("Fetching comments..."):
            comments = get_youtube_comments(video_id)
            if comments:
                st.success(f"Fetched {len(comments)} comments!")

                # Perform Sentiment Analysis
                sentiment_results, sentiment_counts = analyze_sentiments(comments)
                
                # Display Results as Table
                df = pd.DataFrame(sentiment_results, columns=["Comment", "Sentiment"])
                st.subheader("Sentiment Analysis Results")
                st.dataframe(df)

                # Save to CSV
                df.to_csv("youtube_sentiment_analysis.csv", index=False)
                st.download_button(
                    label="Download Results as CSV",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="youtube_sentiment_analysis.csv",
                    mime="text/csv"
                )

                # Visualization: Pie Chart
                st.subheader("Sentiment Distribution")
                fig, ax = plt.subplots()
                ax.pie(
                    sentiment_counts.values(),
                    labels=sentiment_counts.keys(),
                    autopct="%1.1f%%",
                    startangle=140,
                    colors=["green", "gray", "red"]
                )
                ax.set_title("Sentiment Analysis of YouTube Comments")
                st.pyplot(fig)
            else:
                st.error("No comments found for this video.")
    else:
        st.error("Please enter a valid YouTube Video ID.")
