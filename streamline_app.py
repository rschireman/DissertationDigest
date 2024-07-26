import streamlit as st
import shutil
import sieve
import os
from bs4 import BeautifulSoup
import requests

# Utility function to get the title of a YouTube video
def fetch_video_title(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    title_tag = soup.find("title")
    title = title_tag.text if title_tag else "Untitled"
    return title

# Function to convert YouTube video to MP4 using Sieve's API
def convert_youtube_to_mp4(youtube_url):
    youtube_to_mp4 = sieve.function.get("sieve/youtube_to_mp4")
    title = fetch_video_title(youtube_url)
    local_file_path = f"{os.getcwd()}/{title}.mp4"

    if os.path.exists(local_file_path):
        return local_file_path
    else:
        output = youtube_to_mp4.run(url=youtube_url, include_audio=True)
        shutil.copyfile(output.path, local_file_path)
        return local_file_path

# Function to summarize a video transcript using Sieve's API
def analyze_video_transcript(file_path, generate_chapters, generate_highlights, max_summary_length, max_title_length, num_tags, denoise_audio, use_vad, speed_boost, highlight_search_phrases, return_as_json_file):
    video_transcript_analyzer = sieve.function.get("sieve/video_transcript_analyzer")
    output = video_transcript_analyzer.push(
        sieve.File(path=file_path), 
        generate_chapters=generate_chapters, 
        generate_highlights=generate_highlights, 
        max_summary_length=max_summary_length, 
        max_title_length=max_title_length, 
        num_tags=num_tags, 
        denoise_audio=denoise_audio, 
        use_vad=use_vad, 
        speed_boost=speed_boost, 
        highlight_search_phrases=highlight_search_phrases, 
        return_as_json_file=return_as_json_file
    )
    return list(output)

# Streamlit app
def main():
    st.title("YouTube Video Summarizer")

    video_url = st.text_input("Enter YouTube video URL")
    col1, col2 = st.columns(2)

    with col1:
        generate_chapters = st.checkbox("Generate Chapters", value=True)
        generate_highlights = st.checkbox("Generate Highlights", value=False)
        denoise_audio = st.checkbox("Denoise Audio", value=False)
        use_vad = st.checkbox("Use VAD", value=True)
        speed_boost = st.checkbox("Speed Boost", value=False)

    with col2:
        max_summary_length = st.slider("Max Summary Length", 1, 20, 5)
        max_title_length = st.slider("Max Title Length", 5, 50, 10)
        num_tags = st.slider("Number of Tags", 1, 20, 5)

    highlight_search_phrases = st.text_input("Highlight Search Phrases", value="Most interesting")
    return_as_json_file = st.checkbox("Return as JSON File", value=False)

    if st.button("Summarize"):
        with st.spinner("Downloading Video..."):
            video_path = convert_youtube_to_mp4(video_url)

        with st.spinner("Summarizing video..."):
            summary = analyze_video_transcript(
                file_path=video_path, 
                generate_chapters=generate_chapters, 
                generate_highlights=generate_highlights, 
                max_summary_length=max_summary_length, 
                max_title_length=max_title_length, 
                num_tags=num_tags, 
                denoise_audio=denoise_audio, 
                use_vad=use_vad, 
                speed_boost=speed_boost, 
                highlight_search_phrases=highlight_search_phrases, 
                return_as_json_file=return_as_json_file
            )

        st.subheader("Video Summary")
        st.write(summary[2]["summary"])

if __name__ == "__main__":
    main()
