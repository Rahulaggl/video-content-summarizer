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

# Watsonx AI configuration
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

# Extract video ID
def extract_youtube_video_id(url: str) -> str:
    found = re.search(r"(?:youtu\.be\/|watch\?v=)([\w-]+)", url)
    return found.group(1) if found else None

# Get transcript
def get_video_transcript(video_id: str) -> list | None:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except TranscriptsDisabled:
        return None

# Summarize transcript text
def summarize_large_text(text_list: list, max_size: int) -> str:
    summaries = ""
    txts = chunk_large_text(text_list, max_size)
    summaries = summaries.join(txts)
    return summaries

# Chunk text for processing
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

# Caption and tags generation
def generate_caption_and_tags(summary: str) -> tuple:
    model = configure_watsonx()
    
    caption_prompt = f"Create a catchy social media caption based on the following text: {summary}"
    caption_response = model.generate(caption_prompt)
    caption = caption_response.get('results')[0]['generated_text']

    viral_tags_prompt = f"Generate relevant social media tags to make this content viral: {summary}"
    viral_tags_response = model.generate(viral_tags_prompt)
    viral_tags = viral_tags_response.get('results')[0]['generated_text']

    famous_tags_prompt = f"Suggest the top five famous people in the relevant field to tag based on this content: {summary}"
    famous_tags_response = model.generate(famous_tags_prompt)
    famous_tags = famous_tags_response.get('results')[0]['generated_text']

    return caption, viral_tags, famous_tags

# Display transcript as paragraphs
def display_transcript_clean(transcript):
    clean_text = " ".join([entry['text'] for entry in transcript])
    segmented_sentences = seg.segment(clean_text)
    paragraphs = "\n\n".join(segmented_sentences)
    st.text_area("Video Transcript (Formatted)", paragraphs, height=500)

# Streamlit UI
st.title('Video Content Summarization for Captions, Hashtags, and Tags')

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

            # Display video transcript without timestamps
            st.subheader("Video Transcript")
            display_transcript_clean(transcript)
        else:
            st.write("No transcript found for this video.")
    else:
        st.write("Invalid YouTube URL.")
