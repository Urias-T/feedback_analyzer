import os
import requests
import config
import math
import json
import re

# api_key = config.APIKEY  # Use this for "config.py" module

api_key = os.getenv("APIKEY")  # Comment this out if you're using the "config.py" module

BASE_URL = "https://app.thetextapi.com/text/"

HEADERS = {
    "Content-Type": "application/json",
    "apikey": api_key
}


def chunker(text):
    """Function to divide the overall text into chunks to allow proper summarization at API endpoint.

    Args:
        text (str): Text to be chunked

    Returns:
        chunks (list): List of string chunks 
    """

    # include "end of sentence" tag after punctuation marks so they're not lost in split.
    text = text.replace(".", ".<eos>")
    text = text.replace("?", "?<eos>")
    text = text.replace("!", "!<eos>")

    sentences = text.split("<eos>")

    steps = math.ceil(len(sentences) / 5)  # divide into 5 so we get 5 insight points

    chunks = []  # list of strings

    for i in range(0, len(sentences), steps):
        try:
            sub_chunk = sentences[i:i+steps]
            sub_chunk = ("").join(sub_chunk)
            chunks.append(sub_chunk)
        except IndexError:
            sub_chunk = sentences[i:]
            sub_chunk = ("").join(sub_chunk)
            chunks.append(sub_chunk)

    return chunks

def api_call(chunks, url=BASE_URL, headers=HEADERS):
    """Function responsible for making the api call for text summarization.

    Args:
        chunks (list): List of string chunks
        url (web link, optional): Base URL to TheTextAPI. Defaults to BASE_URL.
        headers (JSON, optional): JSON object containing necessary headers for API call. Defaults to HEADERS.

    Returns:
        output, chunk_summaries: Tuple of output string and list of summaries.
    """

    # Concatenate required endpoint to base url
    summarize_url = url+"summarize"
    
    chunk_summaries = []

    # Summarize each chunk and append to the initialized empty list 
    for chunk in chunks:
        body = {
            "text": chunk
            # proportion defaults to 0.3
        }

        response = requests.post(url=summarize_url, headers=headers, json=body)

        summary = json.loads(response.text)["summary"]
        chunk_summaries.append("* " + summary)

    output = "\n \n ".join(chunk_summaries)

    return output, chunk_summaries


def summarizer(format, texts):
    """Function responsible for cleaning text and making summary.

    Args:
        format (str): String indicating the format in which the transcripts are laid out.
        texts (list): List of strings to be summarized
        
    Returns:
        feedbacks: Dictionary of dictionaries containing transcript summaries and outputs.
    """

    feedbacks = {}  # dictionary of dictionaries with transcript summaries and outputs
    
    if format == "dialogue":  # dialogue format
        for i, text in enumerate(texts):
            # Initiailize an empty string for customer feedback
            customer_feedback = ""

            # Split the input text into lines
            lines = text.split("\n")

            # Select lines starting with "Customer" into a list
            customer_response_lines = [line for line in lines if line.startswith("Customer")]
            
            # Loop through the list, pick out the responses and attach them to the customer feedback string
            for response in customer_response_lines:
                customer_feedback += response.split(":")[1] + ""

            chunks = chunker(customer_feedback)  # 5 chunks

            output, chunk_summaries = api_call(chunks)

            feedbacks["transcript_" + str(i)] = {"summaries" : chunk_summaries,
                                                 "output" : output}

    elif format == "non-dialogue":  # non-dialogue format
        for i, text in enumerate(texts):
            customer_feedback = " "

            lines = text.split("\n")

            needed_lines = [line for line in lines if line != " "]  # ensure the lines used are only those with
                                                                    # actual content
            
            for line in needed_lines:
                # clean texts
                line = re.sub("\t", ".", line)  # remove tabs
                line = re.sub("-", " ", line)  # remove dashes used in numbering
                clean_line = re.sub(r"\(\d+\)\s?", " ", line)  # remove digits used in numbering

                customer_feedback += clean_line

            chunks = chunker(customer_feedback)  # 5 chunks

            output, chunk_summaries = api_call(chunks)
        
            feedbacks["transcript_" + str(i)] = {"summaries" : chunk_summaries,
                                                 "output" : output}

    return feedbacks


def derive_themes(feedbacks, url=BASE_URL, headers=HEADERS):
    """Function to derive themes from texts.

    Args:
        feedbacks (dict): Dictionary of dictionaries containing transcript summaries and outputs.
        url (web link, optional): Base URL to TheTextAPI. Defaults to BASE_URL.
        headers (JSON, optional): JSON object containing necessary headers for API call. Defaults to HEADERS.

    Returns:
        outputs: List of strings.
    """

    # Concatenate endpoint to base URL:
    most_common_phrases_url = url+"most_common_phrases"

    insights = []

    for key in feedbacks.keys():
    # for _, v in feedbacks.items():
        # Clean text
        v = re.sub("\*", "", feedbacks[key]["output"])
        v = re.sub("\n \n", " ", v)
        insights.append(v)

    insights_block = " ".join(insights)

    body = {
        "text": insights_block
        # num_phrases defaults to 3
    }

    response = requests.post(url=most_common_phrases_url, headers=headers, json=body)
    most_common_phrases = json.loads(response.text)["most common phrases"]  # list of strings

    locations = {}  # Dictionary of lists of strings.

    outputs = []  # List of strings.

    for phrase in most_common_phrases:
        locations[phrase] = [phrase]
        # transcript_count = 1  # Keep track ofthe transcript being checked.
        # for _, v in summaries.items():
        for key in feedbacks.keys():
            summaries = feedbacks[key]["summaries"]
            for i, string in enumerate(summaries):
                if phrase in string:
                    transcript_id = key.split("_")[1]
                    locations[phrase].append(f"\n \n  * Transcript {transcript_id},\
                                             insight {i+1}")  # Plus one because Python 
                                                              # indexing starts from 0
            # transcript_count += 1
                
        
        outputs.append(" ".join(locations[phrase]))

    return outputs 


if __name__ == "__main__":  # For debugging purposes.

    text = """ 
Interviewer: Can you tell us about your experience with our product?

Customer 1: Yes, I've been using your product for a few weeks now and I have to say I'm really impressed. \
    The user interface is very intuitive and easy to use, and I appreciate the customization options that are \
    available. The product does exactly what it's supposed to do, and I've seen a noticeable improvement in the \
    quality of my work since I started using it. Overall, I'm very happy with the product.

Interviewer: That's great to hear. Is there anything you think we could improve upon?

Customer 1: One thing that would be nice is if there were more video tutorials available to help users get \
    started with the product. While the user interface is intuitive, having more resources available would be \
        helpful. Other than that, I don't have any major complaints.

Interviewer: Thank you for your feedback. We'll definitely take that into consideration.
"""
    print("From __main__ : \n")
    feedbacks, summaries = summarizer(text=[text])

    print(feedbacks)

    print(summaries)

    outputs = derive_themes(feedbacks, summaries)

    print(outputs)
