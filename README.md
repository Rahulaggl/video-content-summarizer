# video-content-summarizer
A Streamlit-based tool that extracts video transcripts, generates concise summaries, suggests catchy captions, relevant hashtags for virality, and recommends famous people to tag based on video content using IBM Watsonx Mistral 7B.
Description

A Streamlit-based tool that extracts video transcripts, generates concise summaries, suggests catchy captions, relevant hashtags for virality, and recommends famous people to tag based on video content using IBM Watsonx Mistral 7B.
About the Project

This project helps content creators automate video transcript summarization, social media optimization, and audience engagement. Leveraging YouTube Transcripts and the power of IBM Watsonx AI, this app:

    Extracts YouTube video transcripts.
    Summarizes video content into readable narratives.
    Suggests engaging captions for social media.
    Provides viral hashtags for content reach.
    Recommends famous personalities to tag based on the video’s field/topic.

Tech Stack

    Python
    Streamlit
    IBM Watsonx AI
    YouTube Transcript API
    Pysbd (Sentence Segmentation)

Features

    YouTube Video Processing: Extracts and summarizes transcripts.
    Caption Generator: Suggests catchy captions for videos.
    Hashtag Recommendations:
        Viral hashtags for content engagement.
        Personalized tags featuring notable people related to the content field.
    User-Friendly Interface: Easy-to-use Streamlit interface for quick execution.

Instructions to Work on the Project
Prerequisites

    Install Python 3.8+ on your system.
    Set up an IBM Watsonx AI account and retrieve your API Key and Project ID:
        IBM Watsonx AI Documentation.
    Create a YouTube API Transcript-enabled account.

Step-by-Step Guide

    Clone the Repository

git clone https://github.com/<your-username>/video-content-summarizer.git  
cd video-content-summarizer  

Set Up the Environment

    Create a virtual environment and install dependencies.

    python -m venv env  
    source env/bin/activate  # On Windows: env\Scripts\activate  
    pip install -r requirements.txt  

Add API Keys

    Create a .env file in the project root and add your credentials:

    WATSONX_API_KEY=your_watsonx_api_key  
    PROJECT_ID=your_ibm_project_id  

Run the Application

    Start the Streamlit app:

        streamlit run app.py  

    Upload Your Video to YouTube
        Make your video Private.
        Share the YouTube link and paste it into the application to generate outputs.

    Generate Recommendations
        Paste the YouTube URL.
        View the outputs for:
            Catchy Captions
            Viral Hashtags
            Famous Personalities to Tag
        Full video transcript summary is available for further edits.

How It Works

    Input: Paste a YouTube video URL.
    Transcript Extraction: Extracts video subtitles using YouTube Transcript API.
    Summarization: Uses Pysbd for text segmentation and splits content for processing.
    Content Generation:
        IBM Watsonx AI generates captions, hashtags, and tags relevant to the content field.
    Output: Displays results in a clean and organized format.

Demo

    Sample outputs will include:
        Video Summary
        Suggested Captions
        Viral Hashtags
        Recommended Famous Personalities

Contributions

Contributions are welcome! Feel free to fork the repository and submit pull requests.
To Contribute:

    Fork the repository.
    Make your changes in a feature branch.
    Submit a pull request with proper documentation.

License

This project is licensed under the MIT License.

Let me know if you'd like any adjustments or additional sections! 🚀
