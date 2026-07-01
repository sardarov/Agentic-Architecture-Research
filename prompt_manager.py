import json
from pathlib import Path


def convert_task_json_to_prompt(task_path: str) -> str:
    """
    Load an ARC task from disk and convert its training pairs and test input into a prompt.
    """

    task_file = Path(f"tasks/ARC-AGI-1/{task_path}")
    task = json.loads(task_file.read_text())

    training_examples = ""
    for i, pair in enumerate(task["train"]):
        training_examples += f"--Example {i}-- \n\nINPUT:\n\n"
        training_examples += json.dumps(pair["input"]) + "\n\n"
        training_examples += "OUTPUT:\n\n"
        training_examples += json.dumps(pair["output"]) + "\n\n"

    test_input = json.dumps(task["test"][0]["input"]) + "\n\n"

    prompt = f"""
Below is a list of input and output grids with a pattern. Your goal is to identify the pattern or transformation in the training examples that maps the input to the output, then apply that pattern to the test input to give a final output.

-- Grid Protocol Specification --
- A "grid" is a rectangular matrix (list of lists) of integers.
- Each nested list represents a single horizontal row, ordered from top to bottom.
- Integers between 0 and 9 (inclusive) represent 10 distinct colors, not numerical values.
- The smallest possible grid size is 1x1 and the largest is 30x30.

--Training Examples--
{training_examples}
--End of Training Examples--

--Test Input--
{test_input}
--End of Test Input--
"""
    return prompt