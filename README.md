<p align="center">
  <img src=".assets/yt-summarizer-logo.png" alt="Logo" width="250">
</p>

<h1 align="center">YouTubeGPT- Your YouTube AI</h1>

## Features :sparkles:

YouTubeGPT lets you **summarize and chat (Q&A)** with YouTube videos. Its features include:

- **provide a custom prompt for summaries** :writing_hand:
  - you can tailor the summary to your needs by providing a custom prompt or just use the default summarization
- **automatically save summaries** :open_file_folder:
  - the summaries can be automatically saved in the directory where you run the app. The summaries will be available under `<YT-channel-name>/<video-title>.md`
- **create your own knowledge base**  :floppy_disk:
  - once you process a video, you can chat with it at any time!
- **choose from different OpenAI models** :robot:
  - currently available: gpt-3.5-turbo, gpt-4 (turbo), gpt-4o (mini)
  - by choosing a different model, you can summarize even longer videos and potentially get better responses
- **experiment with settings** :gear:
  - adjust the temperature and top P of the model
- **choose UI theme** :paintbrush:
  - go to the three dots in the upper right corner, select settings and choose either light, dark or my aesthetic custom theme

## Installation & usage

No matter how you choose to run the app, you will first need to get an OpenAI API-Key. This is very straightforward and free. Have a look at [their instructions](https://platform.openai.com/docs/quickstart/account-setup) to get started.  

### build & run with Docker (or docker-compose)

1. make sure to provide an OpenAI API key (l. 43 in [docker-compose.yml](docker-compose.yml))
2. adjust the path to save the summaries (l. 39 in [docker-compose.yml](docker-compose.yml))
3. execute the following command:

```bash
# pull from docker hub
docker-compose up -d
# or build locally
docker-compose up --build -d
```

### if you are only interested in summaries

```bash
# pull from Docker Hub
docker pull sudoleg/yotube-gpt:latest
# or build locally
docker build --tag=sudoleg/yotube-gpt:latest .
docker run -d -p 8501:8501 \
    -v $(pwd):/app/responses \
    -e OPENAI_API_KEY=<your-openai-api-key> \
    --name youtube-ai sudoleg/yotube-gpt:latest
```

> :information_source: For the best user-experience, you need to be in `Tier 1` [usage tier](https://platform.openai.com/docs/guides/rate-limits/usage-tiers), which requires a one-time payment of 5$. However it's worth it, since then, you'll have access to all models and higher rate limits.

## Contributing

Feedback and contributions are welcome! This is a small side-project and it's very easy to get started! Here’s the gist to get your changes rolling:

1. **Fork & clone**: Fork the repo and clone your fork to start.
2. **Pick an issue or suggest One**: Choose an open issue to work on, or suggest a new feature or bug fix by creating an issue for discussion.
3. **Develop**: Make your changes.
   - Ensure your code is clean and documented. Test the changes at least exploratively. Make sure to test 'edge cases'.
   - Commit your changes with clear, descriptive messages, using [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).
4. **Stay updated**: Keep your branch in sync with the main branch to avoid merge conflicts.
5. **Pull Request**: Push your changes to your fork and submit a pull request (PR) to the main repository. Describe your changes and any relevant details.
6. **Engage**: Respond to feedback on your PR to finalize your contribution.

### development in virtual environment

```bash
# create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate
# install requirements
pip install -r requirements.txt
# you'll need an API key
export OPENAI_API_KEY=<your-openai-api-key>
# run chromadb (necessary for chat)
docker-compose up -d chromadb
# run app
streamlit run main.py
```

## Technologies used

The project is built using some amazing libraries:

- The project uses [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for fetching transcripts.
- [LangChain](https://github.com/langchain-ai/langchain) is used to create a prompt, submit it to an LLM and process it's response.
- The UI is built using [Streamlit](https://github.com/streamlit/streamlit).
- [ChromaDB](https://docs.trychroma.com/) is used as a vector store for embeddings.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
