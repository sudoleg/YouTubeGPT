# LLM-based YouTube Video Summarizer

## AI Summarizer vs other AI summarizers on the internet

### No tracking, runs locally

### Customization options

**Choose from different models**

- currently different GPTs from OpenAI
- Claude is planned

**provide a custom prompt**

**adjust temperature**

### Open source

## Installation

### with Docker

```bash
docker build --tag=ai-yt-summarizer .
docker run -p 8501:8501 -v $(pwd):/app/responses -e OPENAI_API_KEY=<your-openai-api-key> --name yt-summarizer ai-yt-summarizer:latest
```

### development in virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```


> :information_source: The summaries will be saved in the directory where you run the app with docker. The summaries will be available under `<YT-channel-name>/<video-title>.md`.

## Section

## Feedback and contributing

## Limitations and known issues

### no handling of exceeded rate limits
