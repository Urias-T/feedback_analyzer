import requests
import config
import math
import json
import re

api_key = config.APIKEY

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


def summarizer(texts, url=BASE_URL, headers=HEADERS):
    """Function to summarize texts by sending to TheTextAPI

    Args:
        texts (list): List of strings to be summarized
        url (web link, optional): Base URL to TheTextAPI. Defaults to BASE_URL.
        headers (JSON, optional): JSON object containing necessary headers for API call. Defaults to HEADERS.

    Returns:
        feedbacks, summaries: List of dictionaries.
    """

    # Concatenate required endpoint to base url
    summarize_url = url+"summarize"

    summaries = {}  # dictionary of lists of strings

    feedbacks = {}  # dictionary of strings
    
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
       
        chunk_summaries = []

        # Summarize each chunk and append to the initialized empty list 
        for chunk in chunks:
            body = {
                "text": chunk
            }

            response = requests.post(url=summarize_url, headers=headers, json=body)

            summary = json.loads(response.text)["summary"]
            chunk_summaries.append("* " + summary)

        output = "\n \n ".join(chunk_summaries)

        summaries["transcript_" + str(i)] = chunk_summaries

        feedbacks["transcript_" + str(i)] = output

    return feedbacks, summaries


def derive_themes(feedbacks, summaries, url=BASE_URL, headers=HEADERS):
    """Function to derive themes from texts.

    Args:
        feedbacks (dict): Dictionary of lists.
        summaries (dict): Dictionary of lists of strings.
        url (web link, optional): Base URL to TheTextAPI. Defaults to BASE_URL.
        headers (JSON, optional): JSON object containing necessary headers for API call. Defaults to HEADERS.

    Returns:
        outputs: List of strings.
    """

    # Concatenate endpoint to base URL:
    most_common_phrases_url = url+"most_common_phrases"

    insights = []

    for _, v in feedbacks.items():
        # Clean text
        v = re.sub("\*", "", v)
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
        transcript_count = 1  # Keep track ofthe transcript being checked.
        for _, v in summaries.items():
            for i, string in enumerate(v):
                if phrase in string:
                    locations[phrase].append(f"\n \n  * Transcript {transcript_count}, \
                                                insight {i+1}")  # Plus one because Python 
                                                                 # indexing starts from 0
            transcript_count += 1
                
        
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