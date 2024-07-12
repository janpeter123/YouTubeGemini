from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from Gemini.Prompts import *
from VectorDB.VectorDB import *
from Gemini.Gemini import model

videos = set()
video_summaries = dict()

def get_youtube_video_id(url :str)->str:
  """
  ### Summary
  Extracts the video ID from a YouTube watch URL.

  ### Parameters
  url: The YouTube watch URL.

  ### Returns
  The extracted video ID, or None if the URL is not a valid YouTube watch URL.
  """

  # Check if the URL is a valid YouTube watch URL
  if not url or not url.startswith("https://www.youtube.com/watch?"):
    return None

  # Split the URL by parameters
  params = url.split("?")[1].split("&")

  # Iterate over parameters to find the video ID
  for param in params:
    if param.startswith("v="):
      return param[2:]

  # Video ID not found in the URL
  return None



def get_full_text(video_lines :list[str])->str:
    '''
    ### Summary
    Function to get full text of Youtube Video

    ### Parameters
    video_lines - Chunks of youtube texts.

    ### Returns
    String of complete video text.
    '''

    full_text = ""

    for line in video_lines:
        full_text+=line['text']

    return full_text




def answer_question_about_video(video_id :str, question :str)->str:
    '''
    ### Summary
    Function to answer question about Youtube Videos

    ### Parameters
    Video_id - Youtube Video ID
    Question - user question about youtube video content

    ### Return
    string - Video Answer
    '''

    if video_id not in videos:  # If video not present in VectorDB Collections.
        videos.add(video_id)    # Add video id in VectorDB collection.
        video_content = YouTubeTranscriptApi.get_transcript(video_id,languages=['en'],preserve_formatting=False) # Get video transcript.
        full_text = get_full_text(video_content)          # Get full video text.
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) # Text Splitter.
        chunks = text_splitter.split_text(full_text)      # Splits text in chunks of 1000 characters.
        setup_collection(name=video_id,documents=chunks)  # Sets vectordb collection.

    query_results = query_database(query=question,collection_name=video_id)[0]  # Query Documents database
    results = '\n\n'.join(query_results)  #Join results to insert into prompt
    prompt = generate_q_a_prompt_youtube_video(video_content=results,user_query=question) #Generate QA Video
    return model.generate_content(prompt).text

def summarize_video_chunks(chunks :list[str])->list[str]:
    '''
    ### Summary
    Function to summarize a whole video into smaller chunks

    ### Parameters
    chunks - list of youtube video chunks to send
    steps - number of chunks to use at once.

    ### Return
    List of summaries
    '''

    while(len(chunks)>1):
        # Create a new list to store the combined strings
        combined_summaries = []

        # Iterate over the list two by two and combine the strings
        for i in range(0, len(chunks), 2):
            if i + 1 < len(chunks):
                text_chunk = chunks[i] + " " + chunks[i + 1]
                prompt = summarization_prompt(text_chunk) #Generate summarization prompt
                summary= model.generate_content(prompt) # Call LLM Model
                combined_summaries.append(summary.text)      
            else:
                combined_summaries.append(chunks[i])

        chunks = combined_summaries
        combined_summaries = []
        
    return chunks

def get_video_summary(video_id:str)->str:
    '''
    ### Summary
    Gets Youtube Summary

    ### Parameters
    Video_id - string

    ### Returns
    Summary of video
    '''

    if(video_id not in video_summaries.keys()):    
        video_content = YouTubeTranscriptApi.get_transcript(video_id=video_id,languages=['en'],preserve_formatting=False) #Get Video Transcript
        full_text = get_full_text(video_content) #Get full text of video
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200) #Configuring text splitter
        chunks = text_splitter.split_text(full_text) # Split text into chunks
        setup_collection(name=video_id,documents=chunks)  # Sets vectordb collection.
        videos.add(video_id) 
        complete_summary = summarize_video_chunks(chunks)[0] # Function to summarize video
        video_summaries[video_id] = complete_summary #Add to cache complete video Summary
    else:
       complete_summary = video_summaries[video_id]
       
    return complete_summary