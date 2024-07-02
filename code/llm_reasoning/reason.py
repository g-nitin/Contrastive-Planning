from typing import Callable
from time import time
from os.path import exists
from dotenv import load_dotenv
from os import getenv
from pandas import read_csv
from plotly.express import histogram
from requests import post
from pathlib import Path
from sokoban_prompt import *

import google.generativeai as genai
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage


def get_responses(model_name: str,
                  prompts: list[str],
                  get_response: Callable[[str], str],
                  llm_output_path: str,
                  time_output_path: str) -> None:
    """
    Get the responses from the LLM for the given prompts and write them to the file.
    @param model_name: The name of the model.
    @param prompts: The list of prompts to get responses from the LLM.
    @param get_response: The function to get the response from the LLM.
    @param llm_output_path: The path to write the responses to.
    @param time_output_path: The path to write the time taken to get the responses.
    """
    print(f"\nGetting responses for {model_name}...")

    # Initialize the string to write to the file
    write_str: str = f"# {model_name}\n\n"

    # Loop through the prompts
    for i, prompt in enumerate(prompts):
        prompt = f"\n{prompt}"

        print(f"Querying prompt {i + 1}...")

        write_str += f"## Question {i + 1}\n\n"

        # Add prompt to the string in a dropdown
        write_str += f"<details><summary>Prompt</summary>{prompt}\n</details>\n\n"

        # Get the response
        init_time: float = time()
        response: str = get_response(prompt).rstrip()

        time_entry: str = f"{model_name},Question {i + 1},{time() - init_time}"

        # Add the response to the string
        # write_str += f"## Prompt\n{prompt}\n\n## Response\n{response}\n\n"
        write_str += (f"<details><summary>Response</summary>"
                      f"\n\n\t{response}\n\n</details>\n\n")

        # Write the time taken to the time_output_path
        # First need to check whether the file exists
        # If it does not, then write the header + the time entry
        # Else, just write the time entry
        if exists(time_output_path):
            with open(time_output_path, "a") as f:
                f.write(f"{time_entry}\n")
        else:
            with open(time_output_path, "w") as f:
                f.write("Model,Question,Time\n")
                f.write(f"{time_entry}\n")

    # Write the response from the LLM to the file
    print(f"Writing to file {llm_output_path}...")
    with open(llm_output_path, "w") as f:
        f.write(write_str)


def gemini():
    genai.configure(api_key=getenv('GOOGLE_API_KEY'))

    model = genai.GenerativeModel('gemini-1.5-flash')

    # # Print the models
    # for m in genai.list_models():
    #     if 'generateContent' in m.supported_generation_methods:
    #         print(m.name)

    # Get response from the Gemini API given a prompt.
    # @param prompt: The prompt to send to the API.
    # @return: The response from the API.
    get_response: Callable[[str], str] = lambda prompt: model.generate_content(prompt).text

    get_responses("Gemini 1.5 Flash", [prompt_1(), prompt_2(), prompt_3()], get_response,
                  "outputs/gemini_output.md", "outputs/time.csv")


def mistral():
    client = MistralClient(api_key=getenv('MISTRAL_API_KEY'))

    def get_response(prompt: str) -> str:
        """
        Get response from Mistral API given a prompt.
        @param prompt: The prompt to send to the API.
        @return: The response from the API.
        """
        messages = [ChatMessage(role="user", content=prompt)]

        chat_response = client.chat(
            model="open-mixtral-8x22b",
            messages=messages,
        )
        return chat_response.choices[0].message.content

    get_responses("Mistral 8x22b", [prompt_1(), prompt_2(), prompt_3()], get_response,
                  "outputs/mistral_output.md", "outputs/time.csv")


def gemma():
    API_URL: str = "https://api-inference.huggingface.co/models/google/gemma-1.1-7b-it"
    headers: dict[str, str] = {"Authorization": f"Bearer {getenv('HF_API_KEY')}"}

    # Query the model with the given payload
    # @param payload: The payload to send to the model
    # @return: The response from the model    
    query: Callable[[dict], list[dict]] = lambda payload: post(API_URL, headers=headers, json=payload).json()

    # Get the response from the model
    # @param prompt: The prompt to send to the model
    # @return: The response from the model
    get_response: Callable[[str], str] = lambda prompt: \
        query({"inputs": prompt})[0]['generated_text'].replace(prompt, '')

    get_responses("Gemma 1.1 7b", [prompt_1(), prompt_2(), prompt_3()], get_response,
                  "outputs/gemma_output.md", "outputs/time.csv")


def plot_time():
    df = read_csv("outputs/time.csv")

    fig = histogram(df, x="Question", y="Time", color='Model', barmode='group',
                    labels={
                        "Question": "Question Number",
                        "Time": "Time (s)",
                        "Model": "Model Name"
                    },
                    title="Time Taken by Each LLM", )

    time_output_file: str = "plots/time_llm"
    fig.write_html(f"{time_output_file}.html")
    fig.write_image(f"{time_output_file}.png")

    print(f"\nTime taken by each LLM is plotted in ./{time_output_file.split('/')[0]}")


def main():
    load_dotenv()

    Path("./outputs").mkdir(parents=True, exist_ok=True)
    Path("./plots").mkdir(parents=True, exist_ok=True)

    gemini()
    mistral()
    gemma()

    plot_time()


if __name__ == "__main__":
    main()
