from pytube import YouTube, Search

def download_youtube(search_query):
    '''
    Downloads either the highest resolution video or audio from YouTube based on the provided search query.
    @param search_query: str, The search query for the YouTube video.
    @return: 
    Example:
        >> download_youtube("Desired YouTube Video")
    '''
    try:
        # Perform a YouTube search
        search_results = Search(search_query).results
        if not search_results:
            raise ValueError("No search results found.")

        # Get the first video's URL
        url = search_results[0].watch_url

        # Get YouTube video details
        yt = YouTube(url)

        # Get the highest resolution audio stream
        stream = yt.streams.filter(only_audio=True).first()

        # Download the audio or video to the current directory
        print("Downloading...")
        out_file = stream.download()
        print("Download complete.")

        print(f"{yt.title} by {yt.author} has been successfully downloaded.")

    except Exception as e:
        print(f"Error: {e}")

