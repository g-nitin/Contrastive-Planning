from time import time
from typing import Callable
from dotenv import load_dotenv
from os import getenv
import google.generativeai as genai
from huggingface_hub import InferenceClient
from pandas import read_csv
from plotly.express import histogram

from abc import ABC, abstractmethod
from os.path import exists
from pathlib import Path
from sokoban_prompt import *


def _get_responses_helper(write_str: str, prompts: dict[str, str], model_name: str,
                          get_response: Callable[[str], str], time_output_path: str, has_ontology: bool) -> str:
    """
    Helper function that loops through the prompts and gets the responses from the LLM.
    @param write_str: The string to write to the file.
    @param prompts: The list of prompts to get responses from the LLM.
    @param model_name: The name of the model.
    @param get_response: The function to get the response from the LLM.
    @param time_output_path: The path to write the time taken to get the responses.
    @param has_ontology: Whether the prompts have the ontology.
    @return: The modified string to write to the file.
    """
    # Loop through the prompts
    for prompt_name, prompt in prompts.items():
        prompt = f"\n{prompt}"

        # Print the name of the prompt
        print(f"Querying {prompt_name}...")
        write_str += f"### {prompt_name}\n\n"

        # Add prompt to the string in a dropdown
        write_str += f"<details><summary>Prompt</summary>{prompt}\n</details>\n\n"

        # Get the response
        init_time: float = time()
        response: str = get_response(prompt).rstrip()

        # Write the time taken to the time_output_path
        # Is the prompts have ontology, then add ` + ontology` to the prompt name in the time entry
        if has_ontology:
            time_entry: str = f"{model_name},{prompt_name} + ontology,{time() - init_time}"
        else:
            time_entry: str = f"{model_name},{prompt_name},{time() - init_time}"

        # Add the response to the string
        response = response.replace("\n", "")
        response = response.replace("#", "")
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

    return write_str


def _get_responses(model_name: str,
                   prompts_without_onto: dict[str, str],
                   prompts_with_onto: dict[str, str],
                   get_response: Callable[[str], str],
                   llm_output_path: str,
                   time_output_path: str) -> None:
    """
    Get the responses from the LLM for the given prompts and write them to the file.
    @param model_name: The name of the model.
    @param prompts_without_onto: The prompts without the ontology.
    @param prompts_with_onto: The prompts with the ontology.
    @param get_response: The function to get the response from the LLM.
    @param llm_output_path: The path to write the responses to.
    @param time_output_path: The path to write the time taken to get the responses.
    """
    print(f"\nGetting responses for {model_name}...")

    # Initialize the string to write to the file
    write_str: str = f"# {model_name}\n\n"

    # Get the responses for the prompts without ontology
    print("\nQuerying prompts without the ontology.\n")
    write_str += "## Prompts Without Ontology\n\n"
    write_str = _get_responses_helper(write_str, prompts_without_onto, model_name, get_response, time_output_path, False)

    # Get the responses for the prompts with ontology
    print("\nQuerying prompts with the ontology.\n")
    write_str += "## Prompts With Ontology\n\n"
    write_str = _get_responses_helper(write_str, prompts_with_onto, model_name, get_response, time_output_path, True)

    # Write the response from the LLM to the file
    print(f"Writing to file {llm_output_path}...")
    with open(llm_output_path, "w") as f:
        f.write(write_str)


def plot_time():
    """
    Plot the time taken by each LLM.
    """
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


class llm(ABC):
    def __init__(self, name: str, token: str, output_path: str):
        self.name: str = name
        self.token: str = token
        self.output_path: str = output_path
        self.time_output_path: str = "outputs/time.csv"

        # Initialize the prompts
        prompts_dict: dict[str, str] = dict.fromkeys(["Prompt 1", "Prompt 2", "Prompt 3",
                                                      "Prompt 4a", "Prompt 4b", "Prompt 4c", "Prompt 5"])

        # Function to generate the prompts list
        # @param boolean: Whether to include the ontology in the prompts
        # @return: The list of prompts
        generate_prompts_list: Callable[[bool], list[str]] = lambda boolean: \
            [prompt(boolean) for prompt in [prompt_1, prompt_2, prompt_3, prompt_4a, prompt_4b, prompt_4c, prompt_5]]

        # Generate the prompts with and without the ontology
        self.prompts_without_onto: dict[str, str] = dict(zip(prompts_dict.keys(), generate_prompts_list(False)))
        self.prompts_with_onto: dict[str, str] = dict(zip(prompts_dict.keys(), generate_prompts_list(True)))

    @abstractmethod
    def get_response(self, prompt: str) -> str:
        pass

    def get_responses(self):
        _get_responses(self.name, self.prompts_without_onto, self.prompts_with_onto,
                       self.get_response, self.output_path, self.time_output_path)


class gemini_flash(llm):
    def __init__(self):
        super().__init__("Gemini 1.5 Flash", getenv('GOOGLE_API_KEY'), "outputs/gemini_output.md")

    def get_response(self, prompt: str) -> str:
        """
        Get response from the Gemini API given a prompt.
        @param prompt: The prompt to send to the API.
        @return: The response from the API.
        """
        genai.configure(api_key=getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')

        return model.generate_content(prompt).text


class llama_3_8b(llm):
    def __init__(self):
        super().__init__("Meta Llama 3 8B", getenv("HF_API_KEY"), "outputs/llama_3_8b_output.md")

    def get_response(self, prompt: str) -> str:
        """
        Get response from the HuggingFace serverless API given a prompt.
        @param prompt: The prompt to send to the API.
        @return: The response from the API.
        """
        client = InferenceClient(
            "meta-llama/Meta-Llama-3-8B-Instruct",
            token=getenv("HF_API_KEY"),
        )

        return_str: str = ""

        for message in client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                stream=True,
        ):
            return_str += message.choices[0].delta.content

        return return_str


class mixtral_8x7b(llm):
    def __init__(self):
        super().__init__("Mixtral-8x7B Instruct", getenv("HF_API_KEY"), "outputs/mixtral_8x7b_output.md")

    def get_response(self, prompt: str) -> str:
        """
        Get response from the HuggingFace serverless API given a prompt.
        @param prompt: The prompt to send to the API.
        @return: The response from the API.
        """
        client = InferenceClient(
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            token=getenv("HF_API_KEY"),
        )

        return_str: str = ""

        for message in client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                stream=True,
        ):
            return_str += message.choices[0].delta.content

        return return_str


def main():
    load_dotenv()

    Path("./outputs").mkdir(parents=True, exist_ok=True)
    Path("./plots").mkdir(parents=True, exist_ok=True)

    # Remove the `time_output_path` if it exists
    time_output_path: str = "outputs/time.csv"
    if exists(time_output_path):
        print("Initializing the time output file...")
        Path.unlink(Path(time_output_path))

    gemini_flash().get_responses()
    llama_3_8b().get_responses()
    mixtral_8x7b().get_responses()

    plot_time()


if __name__ == "__main__":
    main()
