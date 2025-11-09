import streamlit as st
from pydub import AudioSegment
import io
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import pandas as pd
import tempfile
import os
from scipy.io import wavfile

# -----------------------------
# Functions
# -----------------------------
def convert_audio(file, target_format):
    try:
        audio = AudioSegment.from_file(file)
        buffer = io.BytesIO()
        audio.export(buffer, format=target_format)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error converting audio: {e}")
        return None

def get_audio_stats(file):
    try:
        audio = AudioSegment.from_file(file)
        duration = round(len(audio) / 1000, 2)  # seconds
        channels = audio.channels
        frame_rate = audio.frame_rate
        samples = np.array(audio.get_array_of_samples())
        if channels == 2:
            samples = samples.reshape((-1, 2))
        return duration, frame_rate, channels, samples
    except Exception as e:
        st.error(f"Error getting audio stats: {e}")
        return 0, 0, 0, np.array([])

def plot_waveform(samples, channels):
    fig, ax = plt.subplots(figsize=(10, 3))
    if channels == 2:
        ax.plot(samples[:, 0], label="Left Channel")
        ax.plot(samples[:, 1], label="Right Channel")
    else:
        ax.plot(samples, label="Mono")
    ax.set_title("Audio Waveform")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Amplitude")
    ax.legend()
    st.pyplot(fig)

def plot_amplitude_distribution(samples):
    if samples.ndim == 2:
        samples = samples.flatten()
    fig = px.histogram(samples, nbins=100, title="Amplitude Distribution")
    st.plotly_chart(fig)

def convert_currency(amount, from_currency, to_currency):
    try:
        url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
        response = requests.get(url).json()
        return response['result']
    except Exception as e:
        st.error(f"Currency conversion error: {e}")
        return None

def get_top_currency_rates(base_currency):
    try:
        top_currencies = ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD', 'NZD']
        url = f"https://api.exchangerate.host/latest?base={base_currency}&symbols={','.join(top_currencies)}"
        response = requests.get(url).json()
        rates = response['rates']
        df = pd.DataFrame(list(rates.items()), columns=['Currency', 'Rate'])
        return df
    except Exception as e:
        st.error(f"Error fetching currency rates: {e}")
        return pd.DataFrame()

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="Audio & Currency App", layout="wide")
st.title("🎵 Audio Converter & 💱 Currency Converter")

# Sidebar
st.sidebar.header("Options")

# Audio Section
st.sidebar.subheader("Audio Converter")
uploaded_file = st.sidebar.file_uploader("Upload Audio", type=["mp3", "wav", "m4a", "flac", "ogg"])
output_format = st.sidebar.selectbox("Select Output Format", ["mp3", "wav", "m4a", "flac"])

if uploaded_file:
    st.subheader("Audio File Info & Visualization")
    duration, rate, channels, samples = get_audio_stats(uploaded_file)
    st.write(f"**Duration:** {duration} sec")
    st.write(f"**Sample Rate:** {rate} Hz")
    st.write(f"**Channels:** {channels}")
    plot_waveform(samples, channels)
    plot_amplitude_distribution(samples)
    
    if st.sidebar.button("Convert Audio"):
        converted_audio = convert_audio(uploaded_file, output_format)
        if converted_audio:
            st.success(f"Audio converted to {output_format.upper()} successfully!")
            st.download_button(
                label="Download Converted Audio",
                data=converted_audio,
                file_name=f"converted_audio.{output_format}",
                mime=f"audio/{output_format}"
            )

# Currency Section
st.sidebar.subheader("Currency Converter")
amount = st.sidebar.number_input("Amount", min_value=0.0, value=1.0)
from_currency = st.sidebar.selectbox("From Currency", ["USD","EUR","GBP","JPY","AUD","CAD","CHF","CNY","HKD","NZD"])
to_currency = st.sidebar.selectbox("To Currency", ["USD","EUR","GBP","JPY","AUD","CAD","CHF","CNY","HKD","NZD"])

if st.sidebar.button("Convert Currency"):
    converted_amount = convert_currency(amount, from_currency, to_currency)
    if converted_amount is not None:
        st.subheader(f"💱 {amount} {from_currency} = {round(converted_amount, 4)} {to_currency}")

    st.subheader(f"Top 10 Currency Rates against {from_currency}")
    df_rates = get_top_currency_rates(from_currency)
    st.dataframe(df_rates)
    fig = px.bar(df_rates, x="Currency", y="Rate", title=f"Top 10 Currencies against {from_currency}")
    st.plotly_chart(fig)
