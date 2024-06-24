from time import time
from typing import Callable
from os.path import exists


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

    # Initialize the string to write to the file
    write_str: str = f"# {model_name}\n\n"

    # Loop through the prompts
    for i, prompt in enumerate(prompts):
        prompt = f"```\n{prompt}```"

        write_str += f"## Question {i+1}\n\n"

        # Add prompt to the string in a dropdown
        write_str += f"<details><summary>Prompt</summary>{prompt}</details>\n\n"

        # Get the response
        init_time: float = time()
        response: str = get_response(prompt)

        time_entry: str = f"{model_name},Question {i+1},{time() - init_time}"

        # Add the response to the string
        # write_str += f"## Prompt\n{prompt}\n\n## Response\n{response}\n\n"
        write_str += f"<details><summary>Response</summary>{response}</details>\n\n"

        # Write the time taken to the time_output_path
        # First need to check whether the file exists
        # If it does not, then write the header + the time entry
        # Else, just write the time entry
        if exists(time_output_path):
            with open(time_output_path, "a") as f:
                f.write(time_entry)
        else:
            with open(time_output_path, "w") as f:
                f.write("Model,Question,Time")
                f.write(time_entry)

    # Write the response from the LLM to the file
    with open(llm_output_path, "w") as f:
        f.write(write_str)
