import streamlit as st
import requests
import time
import os
API_KEY = "3fdb37741ce74dd69296a0cdea6761bf"  
HEADERS = {"authorization": API_KEY}
# imports needed libraries for the app and also import api requests library

st.title("Human Speech Sentiment Analyzer")
st.write("Upload a .mp3 or .wav file, and get the overall sentiment detected.")

audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3"])

if audio_file:
    st.audio(audio_file, format=f"audio/{audio_file.type.split('/')[-1]}") # shows audiofile to user 

  
    st.info("Uploading audio...")
    try:
        response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=HEADERS,
            files={"file": audio_file}
        )
        response.raise_for_status()
        audio_url = response.json().get("upload_url")
        if not audio_url:
            st.error("Failed to get upload URL from API.")
            st.stop()
    except Exception as e:
        st.error(f"Upload failed: {e}")
        st.stop()

 
    st.info("Analyzing emotion...")
    transcript_request = {
        "audio_url": audio_url,
        "sentiment_analysis": True  
    }

    try:
        transcript_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json=transcript_request,
            headers=HEADERS
        )
        transcript_response.raise_for_status()
        transcript_id = transcript_response.json()["id"]
    except Exception as e:
        st.error(f"Failed to request transcript: {e}")
        st.stop()

   
    st.info("Waiting for analysis to complete...")
    status_response = None
    while True:
        try:
            status_response = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers=HEADERS
            ).json()
        except Exception as e:
            st.error(f"Error checking status: {e}")
            st.stop()

        if status_response.get("status") == "completed":
            break
        elif status_response.get("status") == "failed":
            st.error("Audio processing failed!")
            st.stop()
        time.sleep(1)

    sentiment_results = status_response.get("sentiment_analysis_results")
    emotions = []

    if sentiment_results:
        for seg in sentiment_results:
            if seg is not None:
                if "sentiment" in seg:
                    emotions.append(seg["sentiment"])
                elif "label" in seg:
                    emotions.append(seg["label"])
    overall_emotion = "cannot detect"
    if emotions:
        overall_emotion = max(set(emotions), key=emotions.count)
        st.success(f"**Predicted overall emotion:** {overall_emotion}")
    else:
        st.warning("No emotions detected. Try a longer or clearer audio clip.")
    if overall_emotion.lower() == "positive":
        tint_color = "rgba(0, 255, 0, 0.2)"   # green tint
    elif overall_emotion.lower() == "negative":
        tint_color = "rgba(255, 0, 0, 0.2)"   # red tint
    else:
        tint_color = "rgba(255, 255, 255, 0)" # neutral / no tint

    # Apply the tint to the entire Streamlit app
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {tint_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    emotion_audio_map = {
    "positive": "positive.mp3",
    "negative": "negative.mp3",
    "neutral": "neutral.mp3",
}
    audio_file = emotion_audio_map.get(overall_emotion.lower())
    if overall_emotion == 'positive' or overall_emotion == 'negative' or overall_emotion == 'neutral':
        st.info("Please listen to this audio file that matches the detected emotion: ")
    if audio_file:
        st.audio(audio_file, format="audio/mp3")
    

    
