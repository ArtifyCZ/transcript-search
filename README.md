# Video transcripter & search tool

This is just a proof of concept for a video transcripter and search tool.
It uses the AssemblyAI API to transcribe the video and then saves the text into specified file.
For searching, it uses then the text files to search using a sentence transformer model.

It splits up the transcript into paragraphs and then uses the sentence transformer model to test the similarity of each
paragraph to the search query. Each paragraph that passes the similarity threshold will be added to the average of the
video and later the score average will be used as the score of the video itself.

## Usage

### Install the requirements

```bash
pip install -r requirements.txt
```

### Set the environment variables

Create a `.env` file, as shown in the `.env.example` file.

You will need to set the following environment variables:

- `ASSEMBLYAI_API_KEY`: The API key for the AssemblyAI API.
- `TMPDIR`: The directory where the temporary files will be stored. For example, it can be `/tmp/transcripter`.
- `TRANSCRIPT_DATABASE_PATH`: This is the directory where the transcripts will be stored for later searching.
- `RELEVANT_SIMILARITY_THRESHOLD`: The similarity threshold for the search.
  The higher the threshold, the more similar the search results will be.

### Load the environment variables

```bash
set -o allexport

source .env

set +o allexport
```

### Add some videos

`python bin/transcripter.py <Youtube URL>`

This will download the video, transcribe it and save the transcript to the `TRANSCRIPT_DATABASE_PATH` as
`<video id>.txt`.

### Search

`python bin/search.py <search query>`

This will search the transcripts in the `TRANSCRIPT_DATABASE_PATH` for the search query or a related meaning.

Each relevant match will be printed to the console with its similarity score.
