import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import openai

# App title
st.set_page_config(page_title="YouTube Summarizer")
st.title("🎥 YouTube Video Summarizer using ChatGPT")

# Input fields
api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
video_url = st.text_input("📺 Paste a YouTube Video URL")

# Function to extract transcript from YouTube
def get_transcript(video_url):
    try:
        video_id = video_url.split("v=")[-1].split("&")[0]

        # Get transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to find English transcript
        transcript = transcript_list.find_transcript(['en'])
        transcript_data = transcript.fetch()

        # Combine text
        text = " ".join([t['text'] for t in transcript_data])
        return text

    except (NoTranscriptFound, TranscriptsDisabled):
        st.error("🚫 Transcript not available for this video. Try another link.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error while fetching transcript: {e}")
        return None

# Function to get summary from OpenAI
def get_summary(api_key, transcript):
    try:
        openai.api_key = api_key

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes YouTube transcripts clearly and concisely."
                },
                {
                    "role": "user",
                    "content": f"Please summarize this YouTube video transcript:\n\n{transcript}"
                }
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response['choices'][0]['message']['content']

    except Exception as e:
        st.error(f"❌ Error from OpenAI API: {e}")
        return None

# Button to trigger summarization
if st.button("🧠 Summarize"):
    if not api_key or not video_url:
        st.warning("⚠️ Please provide both the OpenAI API key and the YouTube URL.")
    else:
        with st.spinner("Fetching transcript..."):
            transcript = get_transcript(video_url)

        if transcript:
            with st.spinner("Summarizing using ChatGPT..."):
                summary = get_summary(api_key, transcript)

            if summary:
                st.subheader("📝 Summary:")
                st.write(summary)
