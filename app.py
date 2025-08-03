import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import openai

st.set_page_config(page_title="YouTube Summarizer", layout="centered")

st.title("🎥 YouTube Video Summarizer with ChatGPT")

api_key = st.text_input("Enter your OpenAI API key", type="password")
video_url = st.text_input("Paste YouTube video link")

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

def get_transcript(video_url):
    try:
        video_id = video_url.split("v=")[-1].split("&")[0]

        # Get list of transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to find English transcript
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            st.error("⚠️ English transcript not found.")
            return None

        # Fetch the actual transcript
        transcript_data = transcript.fetch()
        text = " ".join([t['text'] for t in transcript_data])
        return text

    except (NoTranscriptFound, TranscriptsDisabled):
        st.error("🚫 Transcript not available for this video. Try another link.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error while fetching transcript: {e}")
        return None

def summarize_text(text, api_key):
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You summarize YouTube transcripts in simple, clear points."},
                {"role": "user", "content": f"Summarize the following transcript:\n\n{text}"}
            ],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Summarization Error: {e}")
        return None

if st.button("Summarize"):
    if not api_key or not video_url:
        st.warning("Please enter both API key and video link.")
    else:
        with st.spinner("Getting transcript and summarizing..."):
            transcript = get_transcript(video_url)
            if transcript:
                summary = summarize_text(transcript, api_key)
                if summary:
                    st.subheader("📝 Summary")
                    st.write(summary)
