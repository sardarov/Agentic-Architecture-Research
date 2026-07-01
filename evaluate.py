import json
import time
import re
import ast
from pathlib import Path
from config import ARC_DATASET, SCHEDULING_DATASET
from graphs import baseline_graph, pe_graph, sc_graph, AgentState
from prompt_manager import convert_task_json_to_prompt


architectures = {
    "Level 1: Single-Agent Baseline": baseline_graph,
    "Level 2A: Solver-Critic": sc_graph,
    "Level 2B: Planner-Executor": pe_graph
}

def parse_grid_from_response(raw_text):
    """
    Scans a mixed-text LLM response and extracts the final 2D array.
    """
    # 1. Regex to find anything that looks like a 2D list: [[ ... ]]
    # re.DOTALL allows it to match across multiple newlines
    matches = re.findall(r'\[\s*\[.*?\]\s*\]', raw_text, flags=re.DOTALL)
    
    if not matches:
        print("❌ ERROR: No 2D array found in the response.")
        return None
        
    # 2. Grab the LAST match in the text (the final predicted grid)
    final_array_str = matches[-1]
    
    # 3. Safely parse the string into a Python list
    try:
        # Try strict JSON parsing first
        return json.loads(final_array_str)
    except json.JSONDecodeError:
        # Fallback: LLMs sometimes write Python-style lists with trailing commas 
        # (e.g., [1, 2,],) which breaks strict JSON but is valid Python.
        try:
            return ast.literal_eval(final_array_str)
        except (ValueError, SyntaxError):
            print("❌ ERROR: Array was found but could not be parsed.")
            return None

def extract_scheduling_final_answer(llm_response: str) -> str:
    """
    Scans the LLM's text response and extracts everything explicitly 
    contained within the <FINAL_ANSWER> tags.
    """
    # Use DOTALL to ensure it captures everything even if the LLM adds newlines inside the tag
    # Use IGNORECASE just in case the LLM alters the capitalization of the tag
    pattern = r"<FINAL_ANSWER>(.*?)</FINAL_ANSWER>"
    match = re.search(pattern, llm_response, flags=re.DOTALL | re.IGNORECASE)
    
    if match:
        # Return the captured group, stripped of any leading/trailing whitespace
        return match.group(1).strip()
    else:
        return llm_response

def run_arc_evaluation():

    test_cases = [
        ("ARC-AGI", "EASY", ARC_DATASET["easy"]),
        ("ARC-AGI", "HARD", ARC_DATASET["hard"]),
    ]

    # ==========================================
    # 2. Main Execution Loop
    # ==========================================
    for arch_name, graph in architectures.items():
        print(f"\n\n{'='*70}")
        print(f"TESTING ARCHITECTURE: {arch_name}")
        print(f"{'='*70}")

        for domain, diff, tasks in test_cases:
            print(f"\n▶ Domain: {domain} | Difficulty: {diff}")

            for i, task_path in enumerate(tasks):
                input_data = convert_task_json_to_prompt(task_path)
                correct_answer = json.loads(Path(f"tasks/ARC-AGI-1/{task_path}").read_text())["test"][0]["output"]
                
                print(f"  [Task {i+1}]")

                for attempt in range(3):

                    # Initialize the state dictionary for this specific run
                    initial_state: AgentState = {
                        "domain": domain,
                        "difficulty": diff,
                        "input_data": input_data,
                        "execution_plan": None,
                        "current_response": "",
                        "critique": None,
                        "loop_count": 0,
                        "tokens_used": 0
                    }

                    start_time = time.time()

                    try:                            
                        final_state = graph.invoke(initial_state)
                        elapsed = time.time() - start_time

                        raw_response = final_state['current_response']
                        predicted_grid = parse_grid_from_response(raw_response)

                        if predicted_grid is not None:
                            correct = (predicted_grid == correct_answer)
                        else:
                            correct = False

                        if correct:
                            break # Exit the retry loop if the answer is correct
                        else:
                            print(f"  ❌ Attempt {attempt + 1} failed. Retrying...")

                      
                    except Exception as e:
                        print(f"  ❌ Execution Error: {str(e)}")

                print(f"  🎯 Correct: {correct}")
                print(f"  📊 Tokens: {final_state['tokens_used']} | ⏱️ Time: {elapsed:.2f}s | 🔄 Loops: {final_state.get('loop_count', 1)}")


def run_scheduling_evaluation():

    test_cases = [
        ("Meeting Scheduling", "EASY", SCHEDULING_DATASET["easy"]),
        ("Meeting Scheduling", "HARD", SCHEDULING_DATASET["hard"])
    ]

    # ==========================================
    # 2. Main Execution Loop
    # ==========================================
    for arch_name, graph in architectures.items():
        print(f"\n\n{'='*70}")
        print(f"TESTING ARCHITECTURE: {arch_name}")
        print(f"{'='*70}")

        for domain, diff, tasks in test_cases:
            print(f"\n▶ Domain: {domain} | Difficulty: {diff}")

            for i, task in enumerate(tasks):
                input_data = f"""
-- Description --
{task['description']}

-- Constraints --
{task['constraints']}
"""
                correct_answer = task["expected_output"]

                print(f"  [Task {i+1}]")

                for attempt in range(3):
                    initial_state: AgentState = {
                        "domain": domain,
                        "difficulty": diff,
                        "input_data": input_data,
                        "execution_plan": None,
                        "current_response": "",
                        "critique": None,
                        "loop_count": 0,
                        "tokens_used": 0
                    }

                    start_time = time.time()

                    try:        
                        final_state = graph.invoke(initial_state)
                        elapsed = time.time() - start_time

                        raw_response = final_state['current_response']
                        normalized_response = extract_scheduling_final_answer(raw_response).replace('–', '-').replace('—', '-')                        

                        correct = (normalized_response == correct_answer)
                        if correct:
                            break # Exit the retry loop if the answer is correct
                        else:
                            print(f"  ❌ Attempt {attempt + 1} failed. Retrying...")
                    except Exception as e:
                        print(f"  ❌ Execution Error: {str(e)}")
                
                print(f"    Output:   {normalized_response}")
                print(f"    Expected: {correct_answer}")
                print(f"  🎯 Correct: {correct}")
                print(f"  📊 Tokens: {final_state['tokens_used']} | ⏱️ Time: {elapsed:.2f}s | 🔄 Loops: {final_state.get('loop_count', 1)}")

             

if __name__ == "__main__":
    run_arc_evaluation()
    run_scheduling_evaluation()

