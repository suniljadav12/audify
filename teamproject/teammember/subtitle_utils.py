def parse_subtitles(rec_text):
    # Implement your logic to parse the recognized text and generate subtitles
    # with proper timing information
    subtitles = []

    # Example implementation: Split the recognized text into individual sentences
    # and assign each sentence a timestamp
    sentences = rec_text.split('. ')
    start_time = 0.0
    duration = 2.0  # Duration for each subtitle (in seconds)

    for sentence in sentences:
        subtitle = {
            'start': start_time,
            'end': start_time + duration,
            'text': sentence
        }
        subtitles.append(subtitle)
        start_time += duration

    return subtitles
