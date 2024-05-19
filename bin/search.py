import os
import sys
from collections import defaultdict

from sentence_transformers import SentenceTransformer, util

transcriptDatabasePath = os.environ['TRANSCRIPT_DATABASE_PATH']
searchedPhrase = sys.argv[1]
relevantSimilarityThreshold = float(os.environ['RELEVANT_SIMILARITY_THRESHOLD'])

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

if not os.path.exists(transcriptDatabasePath):
    print('Transcript database path `' + transcriptDatabasePath + '` does not exist, exiting...')
    exit(1)
    pass

print("Loading transcripts...")

transcripts = []
for transcriptFileName in os.listdir(transcriptDatabasePath):
    videoId = transcriptFileName.split('.')[0]
    transcriptFilePath = transcriptDatabasePath + '/' + transcriptFileName
    if not transcriptFileName.endswith('.txt') or not os.path.isfile(transcriptFilePath):
        continue
        pass
    transcriptFile = open(transcriptFilePath, 'r')
    transcript = transcriptFile.read()
    transcriptFile.close()
    transcripts.append((videoId, transcript.split('\n')))
    pass

texts = []
textsVideoId = []
for videoId, transcript in transcripts:
    for paragraph in transcript:
        texts.append(paragraph)
        textsVideoId.append(videoId)
        pass
    pass

print("Loaded transcripts")
print("Searching for phrase `" + searchedPhrase + "`...")

textEmbeddings = model.encode(texts, convert_to_tensor=True)
queryEmbedding = model.encode(searchedPhrase, convert_to_tensor=True)# Compute cosine similarity between the query and each text
similarities = util.pytorch_cos_sim(queryEmbedding, textEmbeddings).squeeze(0)
similarityScores = similarities.cpu().numpy()
rankedIndices = similarityScores.argsort()[::-1]

relevantIndices = [idx for idx in rankedIndices if similarities[idx] > relevantSimilarityThreshold]

videoTranscriptParagraphRelevanceDict = defaultdict(lambda: (0, 0))  # (Relevance sum, Count)
for idx in relevantIndices:
    videoId = textsVideoId[idx]
    videoTranscriptParagraphRelevanceDict[videoId] = (
        videoTranscriptParagraphRelevanceDict[videoId][0] + similarityScores[idx],
        videoTranscriptParagraphRelevanceDict[videoId][1] + 1
    )
    pass

videoRelevanceDict = defaultdict(lambda: 0)
for videoId, (relevanceSum, count) in videoTranscriptParagraphRelevanceDict.items():
    videoRelevanceDict[videoId] = relevanceSum / count
    pass

print("Search results:")

rankedVideoIds = sorted(videoRelevanceDict.keys(), key=lambda videoId: videoRelevanceDict[videoId], reverse=True)
for videoId in rankedVideoIds:
    print(videoId + ': ' + str(videoRelevanceDict[videoId]))
    pass
