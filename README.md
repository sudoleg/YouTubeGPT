<p align="center">
  <img src=".assets/yt-summarizer-logo.png" alt="Logo" width="250">
</p>

<h1 align="center">YTAI - Your YouTube AI</h1>

## Features :sparkles:

YTAI summarizes YouTube videos and is not the first project to do that. However, it offers some features that other similar projects and AI summarizers on the internet don't:

- **provide a custom prompt** :writing_hand:
  - you can tailor the response to your needs by providing a custom prompt just use the default summarization
- **automatically save summaries** :open_file_folder:
  - the summaries can be automatically saved in the directory where you run the app. The summaries will be available under `<YT-channel-name>/<video-title>.md`
- **choose from different models** :robot:
  - currently available: GPTs from OpenAI
  - Claude is planned
  - by choosing a different model, you can summarize even longer videos and potentially get better responses
- **experiment with settings** :gear:
  - adjust the temperature of the model
- **choose UI theme** :paintbrush:
  - go to the three dots in the upper right corner, select settings and choose either light, dark or my aesthetic custom theme

## Installation & usage

No matter how you choose to run the app, you will first need to get an OpenAI API-Key. This is very straightforward and free. Have a look at [their instructions](https://platform.openai.com/docs/quickstart/account-setup) to get started.

### build & run with Docker

```bash
# build locally
docker build --tag=ytai:latest .
# or pull from Docker Hub
docker pull sudoleg/ytai:latest
docker run -d -p 8501:8501 -v $(pwd):/app/responses -e OPENAI_API_KEY=<your-openai-api-key> --name yt-summarizer sudoleg/ytai:latest
```

### development in virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=<your-openai-api-key>
streamlit run main.py
```

## Contributing

Feedback and contributions are welcome! This is a small side-project and it's very easy to get started! Here’s the gist to get your changes rolling:

1. **Fork & clone**: Fork the repo and clone your fork to start.
2. **Pick an issue or suggest One**: Choose an open issue to work on, or suggest a new feature or bug fix by creating an issue for discussion.
3. **Develop**: Make your changes.
   - Ensure your code is clean and documented. Test the changes at least exploratively. Make sure to test 'edge cases'.
   - Commit your changes with clear, descriptive messages, preferably using [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).
4. **Stay updated**: Keep your branch in sync with the main branch to avoid merge conflicts.
5. **Pull Request**: Push your changes to your fork and submit a pull request (PR) to the main repository. Describe your changes and any relevant details.
6. **Engage**: Respond to feedback on your PR to finalize your contribution.

## Technologies used

The project is built using some amazing libraries:

- The project uses [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for fetching transcripts.
- [LangChain](https://github.com/langchain-ai/langchain) is used to create a prompt, submit it to an LLM and process it's response.
- The UI is built using [Streamlit](https://github.com/streamlit/streamlit).

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
