import streamlit as st
import torch
from diffusers import StableDiffusionPipeline

st.title("AI Image Generation")

prompt = st.text_input("Enter your prompt")

@st.cache_resource
def load_model():
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float32
    )
    pipe = pipe.to("cpu")
    return pipe

if prompt:
    with st.spinner("Loading model... First time may take few minutes..."):
        pipe = load_model()

    with st.spinner("Generating image..."):
        image = pipe(prompt).images[0]
        st.image(image, width=450)