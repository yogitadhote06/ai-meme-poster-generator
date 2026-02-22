import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import requests
from dotenv import load_dotenv
import io
import os
from PIL import ImageDraw, ImageFont

# Load environment variables
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

# Page settings
st.set_page_config(page_title="AI Meme Generator")
st.title("🎨 AI Meme & Poster Generator")

# Sidebar
st.sidebar.header("Customization")

tone = st.sidebar.selectbox(
    "Select Tone",
    ["Funny", "Professional", "Motivational"]
)

font_size = st.sidebar.slider("Font Size", 20, 80, 40)
text_color = st.sidebar.color_picker("Pick Text Color", "#FFFFFF")

uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png"])
topic = st.text_input("Enter Topic (Example: Tech Fest 2026)")

# Caption Generator
def generate_caption(topic, tone):
    prompt = f"Write a short {tone} caption for a poster about {topic}."
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 50,
            "temperature": 0.9
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()
    
    if isinstance(result, list):
        return result[0]["generated_text"]
    else:
        return "Caption generation failed. Try again."

# Add Text to Image
#def add_text_to_image(image, text):
    #draw = ImageDraw.Draw(image)
    #font = ImageFont.truetype("fonts/Arial.ttf", font_size)
    
def add_text_to_image(image, caption):
    draw = ImageDraw.Draw(image)

    width, height = image.size
    font_size = int(height / 10)

    font_path = os.path.join("fonts", "Arial.ttf")

    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    text_width, text_height = draw.textbbox((0, 0), caption, font=font)[2:]
    x = (width - text_width) / 2
    y = height - text_height - 20

    draw.text((x, y), caption, font=font, fill="white")

    return image

# Generate Button
if st.button("Generate Poster"):
    if uploaded_image and topic:
        with st.spinner("Generating caption..."):
            caption = generate_caption(topic, tone)
        
        image = Image.open(uploaded_image)
        final_image = add_text_to_image(image, caption)
        
        st.image(final_image, caption="Generated Poster")
        
        img_buffer = io.BytesIO()
        final_image.save(img_buffer, format="PNG")
        
        st.download_button(
            label="Download Poster",
            data=img_buffer.getvalue(),
            file_name="poster.png",
            mime="image/png"
        )
    else:
        st.warning("Please upload image and enter topic.")