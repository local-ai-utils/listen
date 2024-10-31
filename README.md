# Local AI Utils - Listen
A plugin for [local-ai-utils](https://github.com/local-ai-utils/core), adding the record audio via the microphone and get a text transcription. Currently only [OpenAI's TTS](https://platform.openai.com/docs/guides/text-to-speech/overview) is supported.

![Listen Demo](/docs/listen.gif)

## Installation
Currently installation is only supported via the GitHub remote.
```
pip install git+https://github.com/local-ai-utils/listen
```

## Configuration
Only an OpenAI Secret Key is required.

`~/.config/ai-utils.yaml`
```
plugins:
    listen:
keys:
    openai: "sk-proj-abc"
```

### Usage
```
$ listen
Life is like a box of chocolates
```

A window will pop up indicating that recording has started. Press the `Enter` key to stop recording and receive the transcription.