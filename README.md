<p align="center">
  <img src=".assets/yt-summarizer-logo.png" alt="Logo" width="250">
</p>

<h1 align="center">YouTubeGPT- Your YouTube AI</h1>

## Features :sparkles:

YouTubeGPT is a web app that can be run fully locally and lets you **summarize and chat (Q&A)** with YouTube videos. You can either use OpenAI's API or a (local) Ollama instance.

YouTubeGPT's features include:

### :writing_hand: Provide a custom prompt for summaries  [**VIEW DEMO**](https://youtu.be/rJqx3qvebws)

- you can tailor the summary to your needs by providing a custom prompt or just use the default summarization

### :question: Get answers to questions about the video content [**VIEW DEMO**](https://youtu.be/rI8NogvHplE)

- part of the application is designed and optimized specifically for question answering tasks (Q&A)
  
### :open_file_folder: Create and export your own library

- the summaries and answers can be saved to a library accessible at a separate page!
- additionally, summaries and answers can be exported/downloaded as Markdown files!

### :robot: Choose provider and models

- choose between OpenAI's API or a (local) Ollama instance
- currently available: ChatGPT 4-5 (incl. nano & mini) and *continuously updated* with new models
- by choosing a different model, you can summarize even longer videos and get better responses

### :gear: Experiment with settings

- adjust the temperature and top P of the model
  
### :paintbrush: Choose UI theme

- go to the three dots in the upper right corner, select settings and choose either light, dark or my aesthetic custom theme

## Installation & usage

If you want to use OpenAI's API, you will first need to get an OpenAI API-Key. This is very straightforward and free. Have a look at [their instructions](https://platform.openai.com/docs/quickstart/account-setup) to get started.

If you want to use Ollama, you need to have an Ollama server running locally or remotely. You can download Ollama for macOS, Linux, or Windows [on their website](https://ollama.com/download). Make sure the server is reachable either on the default port `11434` or set the `OLLAMA_HOST` environment variable to point to your Ollama server. Also, you need to **pull the models** you want to use.

> **Note**: Ollama limits the context window to 4k tokens by default. I strongly recommend to adjust it to at least 16k tokens. This can be done in the Ollama app settings.

### Run with Docker

1. set the `OPENAI_API_KEY` environment variable either in [docker-compose.yml](docker-compose.yml) or by running `export OPENAI_API_KEY=<your-actual-key>` in your terminal
2. execute the following command:

```bash
# pull from docker hub
docker-compose up -d
# or build locally
docker-compose up --build -d
```

The app will be accessible in the browser under <http://localhost:8501>.

> :information_source: For the best user-experience, you need to be in `Tier 1` [usage tier](https://platform.openai.com/docs/guides/rate-limits/usage-tiers), which requires a one-time payment of 5$. However it's worth it, since then, you'll have access to all models and higher rate limits.

<details>
<summary><h2>Configuration :gear:</h2></summary>

### Environment Variables (Optional)

You can customize the default settings using environment variables. These are optional and will use built-in defaults if not set:

| Environment Variable | Description | Default | Example |
|---------------------|-------------|---------|---------|
| `YTGPT_LLM_PROVIDER` | Default LLM provider | `OpenAI` | `OpenAI` or `Ollama` |
| `YTGPT_DEFAULT_GPT_MODEL` | Default language model | `gpt-4.1-nano` | `gpt-4o`, `llama3` |
| `YTGPT_DEFAULT_EMBEDDINGS_MODEL` | Default embeddings model | `text-embedding-3-small` | `text-embedding-3-large`, `nomic-embed-text:latest` |
| `YTGPT_TEMPERATURE` | Model temperature (0.0-2.0) | `1.0` | `0.7` |
| `YTGPT_TOP_P` | Model top-p (0.0-1.0) | `1.0` | `0.9` |

**Example usage:**

```bash
# Set environment variables
export YTGPT_LLM_PROVIDER=Ollama
export YTGPT_DEFAULT_GPT_MODEL=llama3
export YTGPT_TEMPERATURE=0.7
export YTGPT_TOP_P=0.9

# Run the app
streamlit run main.py
```

Or with Docker:

```bash
# Add to docker-compose.yml or set before running
export YTGPT_LLM_PROVIDER=OpenAI
export YTGPT_DEFAULT_GPT_MODEL=gpt-4o
docker-compose up -d
```

> **Note**: These settings apply at startup and set the initial values in the UI. Users can still change these settings in the sidebar during their session.

</details>

## Contributing & Support :handshake:

I’m working on adding more features and am open to feedback and contributions. Don't hesitate to create an issue or a pull request. Also, if you are enjoying the app or find it useful, please consider giving the repository a star :star:

This is a small side-project and it's easy to get started! If you want to contribute, here’s the gist to get your changes rolling:

1. **Fork & clone**: Fork the repo and clone your fork to start.
2. **Pick an issue or suggest One**: Choose an open issue to work on, or suggest a new feature or bug fix by creating an issue for discussion.
3. **Develop**: Make your changes.
   - Ensure your code is clean and documented. Test the changes at least exploratively. Make sure to test 'edge cases'.
   - Commit your changes with clear, descriptive messages, using [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).
4. **Stay updated**: Keep your branch in sync with the main branch to avoid merge conflicts.
5. **Pull Request**: Push your changes to your fork and submit a pull request (PR) to the main repository. Describe your changes and any relevant details.
6. **Engage**: Respond to feedback on your PR to finalize your contribution.

### Development in virtual environment

If you don't have [`uv`](https://github.com/astral-sh/uv) installed, please follow the installation instructions in the official documentation before running the commands below.
```bash
# create a virtual environment and install dependencies
uv sync
# you'll need an API key
export OPENAI_API_KEY=<your-openai-api-key>
# run chromadb (necessary for chat)
docker-compose up -d chromadb
# run app
uv run streamlit run main.py
```

Note: `pyproject.toml` and `uv.lock` are the source of truth for dependencies. `requirements.txt` is kept for legacy pip users.

The app will be accessible in the browser under <http://localhost:8501> and the ChromaDB API under <http://localhost:8000/docs>.

## Technologies used

The project is built using some amazing libraries:

- The project uses [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for fetching transcripts.
- [LangChain](https://github.com/langchain-ai/langchain) is used to create a prompt, submit it to an LLM and process it's response.
- The UI is built using [Streamlit](https://github.com/streamlit/streamlit).
- [ChromaDB](https://docs.trychroma.com/) is used as a vector store for embeddings.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
