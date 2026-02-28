import streamlit as st
import google.generativeai as genai
import wave
import io
import os

# ---------------- THEME TOGGLE ----------------
theme = st.sidebar.toggle("🌙 Dark Mode", value=False)

if theme:
    bg = "#0E1117"
    text = "white"
else:
    bg = "white"
    text = "black"

st.markdown(f"""
<style>
.stApp {{
    background-color: {bg};
    color: {text};
}}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
subject = st.sidebar.multiselect(
    "Select Subjects",
    ["Maths","Physics","Chemistry","Computer Science","English",
     "History","Geography","Economics","Political Science",
     "Philosophy","Arts","Music","Sports",
     "Health and Fitness","Psychology","Sociology","Literature"]
)

Level = st.sidebar.selectbox(
    "Academic Level",
    ["High School","Intermediate","Graduate","PhD"]
)

# ---------------- GEMINI CONFIG ----------------
api_Key=os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_Key)

text_model = genai.GenerativeModel("gemini-2.5-flash")
tts_model = genai.GenerativeModel("gemini-2.5-flash-preview-tts")

# ---------------- PROMPT TEMPLATE ----------------
pre_prompt = """
You are ProfessorGPT, an AI professor.
Explain topics clearly, concisely, and accurately.
Adjust response length based on question type.
Align answer with selected subject and academic level.
"""

# ---------------- UI ----------------
st.title("🎓 ProfessorGPT - Your AI Professor")
st.divider()

prompt = st.text_input("What do you want to ask?")
Askbutton = st.button("Ask ▶")

st.caption("Professor will answer when you click the Ask button.")
st.divider()

# ---------------- MAIN LOGIC ----------------
if Askbutton:

    if not prompt.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner("Thinking..."):

            subject_text = ", ".join(subject) if subject else "General"

            full_prompt = f"""
            Subject: {subject_text}
            Academic Level: {Level}
            {pre_prompt}
            Question: {prompt}
            """

            result = text_model.generate_content(full_prompt)

            if result and result.text:

                response = result.text
                st.write(response)

                # -------- TEXT TO SPEECH --------
                tts_result = tts_model.generate_content(
                    response,
                    generation_config={"response_modalities": ["AUDIO"]}
                )

                audio_part = tts_result.candidates[0].content.parts[0]
                audio_bytes = audio_part.inline_data.data

                # Wrap raw PCM into proper WAV
                wav_io = io.BytesIO()

                with wave.open(wav_io, "wb") as wf:
                    wf.setnchannels(1)      # mono
                    wf.setsampwidth(2)      # 16-bit
                    wf.setframerate(24000)  # Gemini sample rate
                    wf.writeframes(audio_bytes)

                wav_io.seek(0)

                st.audio(wav_io.read(), format="audio/wav")

            else:
                st.error("No response generated.")