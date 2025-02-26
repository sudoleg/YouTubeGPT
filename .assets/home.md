# YouTubeGPT - Your personal YouTube AI

Get insights from YouTube videos with YouTubeGPT, an LLM-based app that allows you to summarize or even ask questions and receive answers about them! Check out the project on [GitHub](https://github.com/sudoleg/YouTubeGPT) for more information! Also, if you like the app, I would be very happy about a star :star:

## Summary

If you have a relatively short video (<45 minutes), you can use the `Summary` part of the application. It allows you to provide **a custom prompt** to tailor the summary to your needs. As the video is short anyways, you could, for example, provide your questions here. Or you could ask to list all the topics in the video and then ask specific questions about them using the other part of the application (see below) 😉

## Q&A - Chat

The `Chat` part of the application is best suited when you have a longer video you have specific questions about. It is more efficient and less cost consuming, as only the relevant parts of the video are provided to the language model. Moreover, once you process a video, you can Q&A it whenever you want (as long as you don't remove the volume accidentally 😅).

Personally, I use the chat feature for lengthy podcasts with timestamps, like podcasts from [Andrew Huberman](https://www.youtube.com/@hubermanlab), [Lex Fridman](https://www.youtube.com/@lexfridman) or [Chris Williamson](https://www.youtube.com/@ChrisWillx). You can just copy the title of the section/timestamp and get a good overview of the topics discussed.

> ❗ Unfortunately, the `Chat` part is not available on streamlit cloud as it requires an instance of ChromaDB. However, you can set this up locally very easilly with Docker on your PC! Check out the [usage instructions](https://github.com/sudoleg/YouTubeGPT?tab=readme-ov-file#installation--usage) on GitHub!

## Library

The summaries and answers can be saved to a library, which is accessible on a separate page. Thus, you can review them at any time. Moreover, you can filter and export your library items as Markdown files.
