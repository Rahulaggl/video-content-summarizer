import streamlit as st
import re
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import pysbd
import dotenv
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models import ModelInference

dotenv.load_dotenv()

def configure_watsonx():
    credentials = {
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": os.getenv("WATSONX_API_KEY")
    }
    project_id = os.getenv("PROJECT_ID")
    model_id = "mistralai/mixtral-8x7b-instruct-v01"

    parameters = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MIN_NEW_TOKENS: 1,
        GenParams.MAX_NEW_TOKENS: 150
    }

    model = ModelInference(
        model_id=model_id, 
        params=parameters, 
        credentials=credentials,
        project_id=project_id)
    
    return model

seg = pysbd.Segmenter(language='en', clean=True)

def extract_youtube_video_id(url: str) -> str:
    found = re.search(r"(?:youtu\.be\/|watch\?v=)([\w-]+)", url)
    if found:
        return found.group(1)
    return None

def get_video_transcript(video_id: str) -> list | None:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except TranscriptsDisabled:
        return None
    return transcript

def format_timestamp(timestamp: float) -> str:
    return str(round(timestamp))

def shorten_text(text: str, max_length: int = 60) -> str:
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def chunk_large_text(text_list: list, max_size: int) -> list[str]:
    txts = []
    para = ''
    for s in text_list:
        s_len = len(s)
        if para and len(para) + s_len > max_size:
            txts.append(para)
            para = ''
        if s_len <= max_size:
            para += s + '\n'
        else:
            if para:
                txts.append(para)
                para = ''
            cut = s_len // max_size
            chunk = s_len // (cut + 1)
            i = 0
            while i < s_len:
                if s_len - i <= chunk:
                    txts.append('... ' + s[i:] + ' ...')
                    break
                clip_i = s.find(' ', i + chunk)
                txts.append('... ' + s[i:clip_i] + ' ...')
                i = clip_i + 1
    if para:
        txts.append(para)
    return txts

def summarize_large_text(text_list: list, max_size: int) -> str:
    summaries = ""
    txts = chunk_large_text(text_list, max_size)
    summaries = summaries.join(txts)
    return summaries

def generate_caption_and_tags(summary: str) -> tuple:
    model = configure_watsonx()
    
    caption_prompt = f"Create a catchy social media caption based on the following text: {summary}"
    caption_response = model.generate(caption_prompt)
    caption = caption_response.get('results')[0]['generated_text']

    viral_tags_prompt = f"Generate relevant social media tags to make this content viral: {summary}"
    viral_tags_response = model.generate(viral_tags_prompt)
    viral_tags = viral_tags_response.get('results')[0]['generated_text']

    famous_tags_prompt = f"Suggest famous people in the relevant field to tag based on this content: {summary}"
    famous_tags_response = model.generate(famous_tags_prompt)
    famous_tags = famous_tags_response.get('results')[0]['generated_text']

    return caption, viral_tags, famous_tags

def format_interval(start, end):
    start_min = int(start // 60)
    start_sec = int(start % 60)
    end_min = int(end // 60)
    end_sec = int(end % 60)
    return f"{start_min:02}:{start_sec:02} - {end_min:02}:{end_sec:02}"

def display_transcript(transcript):
    transcript_text = ""
    for entry in transcript:
        formatted_interval = format_interval(entry['start'], entry['start'] + entry['duration'])
        shortened_text = shorten_text(entry['text'])
        transcript_text += f"{formatted_interval}: {shortened_text}\n\n"
    
    # Display the entire transcript with time frames
    st.text_area("Video Transcript with Time Frames", transcript_text, height=500)

# Streamlit UI
st.title('Video Content Summarization to Suggest Captions, Hashtags, and Tag Relevant People Using Watsonx Mistral 7B')

st.write("### Instructions:")
st.markdown(
    "1. Upload your video to [YouTube](https://www.youtube.com).\n"
    "2. Set the video visibility to **Private**.\n"
    "3. Copy the video link and paste it below to generate captions, hashtags, and suggestions."
)

url = st.text_input('Enter YouTube URL')
submit = st.button('Submit')

if submit and url:
    video_id = extract_youtube_video_id(url)
    if video_id:
        transcript = get_video_transcript(video_id)
        if transcript:
            st.subheader("Catchy Caption")
            
            # Generate and display caption
            text_list = seg.segment(' '.join([entry['text'] for entry in transcript]))
            summary = summarize_large_text(text_list, max_size=2048)
            if summary:
                caption, viral_tags, famous_tags = generate_caption_and_tags(summary)
                st.write(caption)

                st.subheader('Famous People to Tag')
                st.write(famous_tags)

                st.subheader('Viral Hashtags')
                st.write(viral_tags)

            # Display video transcript with time frames at the end
            st.subheader("Video Transcript with Time Frames")
            display_transcript(transcript)
        else:
            st.write("No transcript found for this video.")
    else:
        st.write("Invalid YouTube URL.")
