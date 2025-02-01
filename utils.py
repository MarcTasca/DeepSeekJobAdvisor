import json, re
import numpy as np
from bs4 import BeautifulSoup

# process the json files
def process_json_files(json_files):
    """This function takes a list of json files and print their content.

    Parameters:
    json_files (list): A list of json files.

    Raises:
    ValueError: If the json files do not match the expected files.
    """

    expected_files = [
        'Application.json',
        'Conversation.json',
        'Job_data.json',
        'Job_views.json',
        'Jobseeker.json',
        'Match.json'
    ]

    json_file_names = [json_file.name for json_file in json_files]

    if set(json_file_names) != set(expected_files):
        raise ValueError("Received JSON files do not match the expected files.")

    for json_file in json_files:
        data = json.load(json_file)
        print(json_file.name)
        print(data)
        print("\n")


def parse_html(content_html: str) -> str:
    """
    This function takes a job description with html stuff and clean it.

    Parameters:
    content_html (str): The job description with html tags.

    Returns:
    str: The cleaned job description.
    """
    # Parse the HTML content
    soup = BeautifulSoup(content_html, 'html.parser')
    text = soup.get_text(separator=' ')  # Use separator to handle spaces between tags

    # Clean up the text
    text = text.replace('\xa0', ' ')

    # Print the cleaned text
    return text

def parse_email(body):
    """
    This function takes an email body and clean it.
    It removes any previous messages, empty lines, and lines starting with >.
    It also removes the lines with the date and time of the previous messages.
    
    Parameters:
    body (str): The email body.
    
    Returns:
    str: The cleaned email body."""
     # remove the lines with > at the beginnning (may be useless)
    body = re.sub(r'^>.*', '', body, flags=re.MULTILINE)

    # remove all the previous messages
    body = re.sub(r'^Il giorno .* alle ore.*<.*>.*scritto:.*', '', body, flags=re.MULTILINE | re.DOTALL)
    
    # remove the empty lines
    body = re.sub(r'^\s*$', '', body, flags=re.MULTILINE)

    return body


def extract_context(body):
    """
    Extract the context from the email body.
    The context is what happened before the first message.
    
    Parameters:
    body (str): The email body.
    
    Returns:
    dict: A dictionary with the context."""

    lines = body.split('\n')
    context = {}

    for line in lines:
        if line.startswith('>'):
            n = len(line) - len(line.lstrip('>'))
            context.setdefault(n, '')
            context[n] += line.lstrip('>') + '\n'

    return context

def go_get_jason(client, prompt, model, stream, temperature, max_tokens):
    """
    This function sends a prompt to the OpenAI API and retrieves the answer.
    - The prompt is sent to the model.
    - The answer is split in two parts: the thinking part and the info part.
    - The info part is a json string that is loaded and returned as a dictionary.
    
    Parameters:
    client (OpenAI): The OpenAI client, which in reality is pointing to a localhost.
    prompt (str): The prompt to send to the model.
    model (str): The model to use.
    stream (bool): Whether to stream the response.
    
    Returns:
    tuple: A tuple with the thinking part and the info part."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        stream=stream,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # retrieve the answer
    answer = response.choices[0].message.content

    # split the part in the <think> text </think>
    thinking = answer.split("<think>")[1].split("</think>")[0]
    info = answer.split("</think>")[1]
    info = info.split("```")[1]

    # find the first { and the last } to get the json
    start = info.find("{")
    end = info.rfind("}")
    info = info[start:end+1]
    info = json.loads(info)

    return thinking, info

def email_response(client, prompt, model, stream, temperature, max_tokens):
    """
    This function generates an email response.
    It uses the OpenAI API to generate the response.
    
    Returns:
    str: The email response."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        stream=stream,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    answer = response.choices[0].message.content
    return answer

def get_embedding(client, model_name, text):
    """This function sends a text to the OpenAI API and retrieves the embedding.

    Parameters:
    client (OpenAI): The OpenAI client, which in reality is pointing to a localhost.
    model_name (str): The model to use.
    text (str): The text to embed.

    Returns:
    np.array: The embedding of the text.
    """
    response = client.embeddings.create(
        model=model_name,
        input=text
    )
    return np.array(response.data[0].embedding).reshape(1, -1)


