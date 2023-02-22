# feedback_analyzer



This web app is built to draw insight and themes from three  related customer feedback transcripts.

The transcripts are expected to be in dialogue format with only the lines with customer response beginning with "Customer:" (*Check "sample_transcripts" folder for examples.*)

```
Interviewer: Can you tell us about your experience with our product?

Customer 1: Yes, I've been using your product for a few weeks now and I have to say I'm really impressed. The user interface is very intuitive and easy to use, and I appreciate the customization options that are available. The product does exactly what it's supposed to do, and I've seen a noticeable improvement in the quality of my work since I started using it. Overall, I'm very happy with the product.

Interviewer: That's great to hear. Is there anything you think we could improve upon?

Customer 1: One thing that would be nice is if there were more video tutorials available to help users get started with the product. While the user interface is intuitive, having more resources available would be helpful. Other than that, I don't have any major complaints.

Interviewer: Thank you for your feedback. We'll definitely take that into consideration.
```


## How To Use: 

(*only been tested on Windows:*)

- You would need to get an API key from [TheTextAPI](www.thetextapi.com)
- Paste API key in the config file and assign it to the "APIKEY" variable.
- Install dependencies from "requirements.txt" file.

```
pip install -r requirements.txt
```

- Run "app.py" file. (*app would run on your local host*)

```
python app.py
```

## How it works:

feedback_analyzer is built with Dash frontend and Python 3.10.9 on the backend. On a high level, it works by taking the texts, chunking them up to five portions and sending each portion to TheTextAPI summarize endpoint to draw insights. This chunking process allows for quicker and more accurate analysis by the models used by the API endpoint.

These insights are then stored in the browser cache and transferred to another callback function through which they are transferred to another function where they are bunched into a full text paragraph and sent to another API endpoint by TheTextAPI where the three (default) most common phrases are returned.

These phrases are then used to search through the initially saved insights and identify which transcripts and which insights specifically have those phrases.

