from typing import Callable
from dotenv import load_dotenv
from os import getenv
from abc import ABC, abstractmethod
from os.path import exists
from pathlib import Path
# from time import sleep

from prompt import Prompt, get_prompt_dict
import google.generativeai as genai
from huggingface_hub import InferenceClient
from openai import OpenAI
from anthropic import Anthropic


def _get_responses_helper(write_str: str, prompt: Prompt, get_response: Callable[[str], str]) -> str:
    """
    Helper function that loops through the prompts and gets the responses from the LLM.
    @param write_str: The string to write to the file.
    @param prompt: The Prompt object to get the responses for.
    @param get_response: The function to get the response from the LLM.
    @return: The modified string to write to the file.
    """
    # Get the prompts
    prompts: dict[str, str] = prompt.get_prompts()

    # Loop through the prompts
    for name, prompt in prompts.items():
        prompt = f"\n{prompt}"

        # Print the name of the prompt
        print(f"Querying prompt {name}...")
        # Add prompt to the string in a dropdown
        write_str += f"\n<details><summary>{name}</summary>{prompt}\n</details>\n\n"

        # Get the response
        response: str = get_response(prompt).rstrip()

        # Add the response to the string
        response = response.replace("\n", "")
        response = response.replace("#", "")
        # To adhere with punctuations, replace the first letter with 'p' of `name`
        name = 'p' + name[1:]
        write_str += (f"<details><summary>Response for {name}</summary>"
                      f"\n\n\t{response}\n\n</details>\n\n")

    return write_str


class LLM(ABC):
    def __init__(self, name: str, token: str, output_path: str,
                 plan_dict: dict[int, tuple[Prompt, Prompt]]):
        """
        Initialize the LLM.
        @param name: The name of the LLM.
        @param token: The token for the API.
        @param output_path: The path to write the responses to.
        @param plan_dict: The dictionary of plans to their respective Prompts with or without the ontology.
            The keys are integers representing the plan number.
            The values are a two-tuple consisting of the Prompt objects representing the questions for the plan
            with and without the ontology (in that order).
        """
        self.name: str = name
        self.token: str = token
        self.output_path: str = output_path
        self.plan_dict: dict[int, tuple[Prompt, Prompt]] = plan_dict

        # Example of a plan_dict:
        # {
        #     1: (
        #           Prompt("this is the problem", "this is the solution", prompt_action, False),
        #           Prompt("this is the problem", "this is the solution", prompt_action, True)
        #        ),
        # }

        # Example of prompt_action:
        # {
        #     "Prompt 2": "this is prompt 2",
        #     "Prompt 3": "this is prompt 3",
        #     "Prompt 4a": "this is prompt 4a",
        #     "Prompt 4b": "this is prompt 4b",
        #     "Prompt 4c-1": "this is prompt 4c-1",
        #     "Prompt 4c-2": "this is prompt 4c-2",
        #     "Prompt 5": "this is prompt 5"
        # }

    @abstractmethod
    def get_response(self, prompt: str) -> str:
        pass

    def get_responses(self):
        """
        Get the responses from the LLM for the given prompts and write them to the file.
        """
        print(f"\nGetting responses for {self.name}...")

        # Initialize the string to write to the file
        write_str: str = f"# {self.name}\n\n"
        write_str += "---\n\n"  # Add a horizontal rule

        # For each plan, get the responses for the prompts
        for plan_num, prompts in self.plan_dict.items():
            prompts_without_onto, prompts_with_onto = prompts

            print(f"\nGetting responses for plan {plan_num}")
            write_str += f"## Plan {plan_num}\n\n"

            # Get the responses for the prompts without ontology
            print("\nQuerying prompts without the ontology.")
            write_str += "### Prompts Without Ontology\n\n"
            write_str = _get_responses_helper(write_str, prompts_without_onto, self.get_response)

            # Get the responses for the prompts with ontology
            print("\nQuerying prompts with the ontology.")
            write_str += "### Prompts With Ontology\n\n"
            write_str = _get_responses_helper(write_str, prompts_with_onto, self.get_response)

            # print("\nWaiting for a minute before querying the next plan...")
            # sleep(60)

        # Write the response from the LLM to the file
        print(f"Writing to file {self.output_path}...")
        with open(self.output_path, "w") as f:
            f.write(write_str)


class gemini_flash(LLM):
    def __init__(self, plan_dict):
        """
        Initialize the Gemini 1.5 Flash LLM.
        @param plan_dict: The dictionary of plans to their respective Prompts
            with or without the ontology (in that order).
        """
        super().__init__("Gemini 1.5 Flash", getenv('GOOGLE_API_KEY'),
                         "outputs/gemini_output.md", plan_dict)

    def get_response(self, prompt: str) -> str:
        """
        Get response from the Gemini API given a prompt.
        @param prompt: The prompt to send to the API.
        @return: The response from the API.
        """
        genai.configure(api_key=getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')

        return model.generate_content(prompt).text


class llama_3_8b(LLM):
    def __init__(self, plan_dict):
        """
        Initialize the Meta Llama 3 8B LLM.
        @param plan_dict: The dictionary of plans to their respective Prompts
            with or without the ontology (in that order).
        """
        super().__init__("Meta Llama 3 8B", getenv("HF_API_KEY"),
                         "outputs/llama_3_8b_output.md", plan_dict)

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


class mixtral_8x7b(LLM):
    def __init__(self, plan_dict):
        """
        Initialize the Mixtral 8x7B LLM.
        @param plan_dict: The dictionary of plans to their respective Prompts
            with or without the ontology (in that order).
        """
        super().__init__("Mixtral-8x7B Instruct", getenv("HF_API_KEY"),
                         "outputs/mixtral_8x7b_output.md", plan_dict)

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


class gpt_4o(LLM):
    def __init__(self, plan_dict):
        """
        Initialize the OpenAI GPT-4o LLM.
        @param plan_dict: The dictionary of plans to their respective Prompts
            with or without the ontology (in that order).
        """
        super().__init__("GPT 4o", getenv("OPENAI_API_KEY"),
                         "outputs/gpt_4o_output.md", plan_dict)

    def get_response(self, prompt: str) -> str:
        """

        @param prompt: The prompt to send to the API.
        @return: The response from the API.
        """
        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt}
            ]
        )

        return completion.choices[0].message.content


class claude_sonnet(LLM):
    def __init__(self, plan_dict):
        """
        Initialize the Claude 3.5 Sonnet LLM.
        @param plan_dict: The dictionary of plans to their respective Prompts
            with or without the ontology (in that order).
        """
        super().__init__("Claude 3.5 Sonnet", getenv("ANTHROPIC_API_KEY"),
                         "outputs/claude_sonnet.md", plan_dict)

    def get_response(self, prompt: str) -> str:
        """

        @param prompt: The prompt to send to the API.
        @return: The response from the API.
        """
        client = Anthropic()

        message = client.messages.create(
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="claude-3-5-sonnet-20240620",
        )

        return message.content[0].text


def main():
    load_dotenv()

    Path("./outputs").mkdir(parents=True, exist_ok=True)
    Path("./plots").mkdir(parents=True, exist_ok=True)

    # Remove the `time_output_path` if it exists
    time_output_path: str = "outputs/time.csv"
    if exists(time_output_path):
        print("Initializing the time output file...")
        Path.unlink(Path(time_output_path))

    plan_dict: dict[int, tuple[Prompt, Prompt]] = get_prompt_dict()

    # Debugging
    # plan_dict = {1: plan_dict.get(1)}
    # from pprint import pprint
    # pprint(plan_dict.get(1))
    # for a, plan in plan_dict.items():
    #     pprint(plan[0].prompt_1())

    # gemini_flash(plan_dict).get_responses()
    # llama_3_8b(plan_dict).get_responses()
    # mixtral_8x7b(plan_dict).get_responses()
    # gpt_4o(plan_dict).get_responses()
    # claude_sonnet(plan_dict).get_responses()


if __name__ == "__main__":
    main()
