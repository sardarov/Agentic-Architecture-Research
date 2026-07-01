from typing import TypedDict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    domain: str
    difficulty: str
    input_data: str
    execution_plan: Optional[str]
    current_response: str
    critique: Optional[str]
    loop_count: int
    tokens_used: int

llm = ChatOpenAI(model="gpt-5.1",  reasoning_effort="none", temperature=0)

# Helper function to keep token counting uniform
def track_tokens(state: AgentState, response) -> int:
    tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
    return state.get("tokens_used", 0) + tokens


# ==========================================
# Nodes for Level 1 (Baseline)
# ==========================================
def call_baseline_agent(state: AgentState):
    if state['domain'] == "ARC-AGI":
        prompt = f"""
You are participating in a puzzle solving competition. You are an expert at solving puzzles.

{state['input_data']}

Respond in the format of the training output examples.

Your response:
"""
    else:
        prompt = f"""
You are an expert Scheduling Agent. Your task is to solve a multi-person coordination problem based on a provided description and set of constraints.

{state['input_data']}

Return only the final answer, with no additional text.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "current_response": response.content, 
        "tokens_used": track_tokens(state, response)
    }


# ==========================================
# Nodes for Level 2A (Planner-Executor)
# ==========================================
def planner_node(state: AgentState):
    if state['domain'] == "ARC-AGI":
        prompt = f"""
You are an elite mathematical and spatial logic strategist participating in a puzzle solving competition.

-- Objective --
Your job is to analyze the Training Examples, discover the exact underlying transformation rule, and write a strict, step-by-step execution plan that a separate execution agent can use to solve the Test Input. 

You must NOT attempt to generate the final output grid yourself. 

{state['input_data']}

-- Output Format --
Write a highly detailed, numbered algorithm. Your plan must explicitly define:
1. How to calculate the exact dimensions of the output grid.
2. The specific color integers to use.
3. The exact spatial rules for mapping shapes, blocks, or pixels from the input to the output.

Your response:
"""
    else:
        prompt = f"""
You are the Planner Node. Your job is to take a complex multi-timezone scheduling problem and break it down into a linear, step-by-step execution plan. Do not solve the problem yourself.

{state['input_data']}

To ensure strict mathematical accuracy, your plan MUST force the Executor to follow this specific logical sequence:
1. Identify all individual participants and their local availability windows.
2. Calculate the exact UTC offset for every local timezone mentioned.
3. Convert every participant's local availability window into a standardized UTC format.
4. Apply any global or conditional constraints (e.g., lunch hours, manager dependencies) to the UTC windows.
5. Compute the mathematical intersection of the remaining valid UTC blocks.
6. Isolate the earliest valid 1-hour UTC slot from the intersection.

Output a structured, numbered list of these steps for the Executor.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "execution_plan": response.content, 
        "tokens_used": track_tokens(state, response)
    }

def executor_node(state: AgentState):
    if state['domain'] == "ARC-AGI":
        prompt = f"""
You are a precision matrix manipulation engine participating in a puzzle solving competition. 

-- Objective --
You have been provided with a puzzle and a strict Execution Plan created by the master Planner agent. Your ONLY job is to execute the Planner's algorithm step-by-step on the Test Input to generate the final output grid. Do not invent your own rules.

-- Original Puzzle --
{state['input_data']}

-- Planner's Execution Plan --
{state['execution_plan']}

-- Instructions --
1. Read the Test Input carefully.
2. Walk through the Planner's Execution Plan step-by-step, applying the math and spatial transformations to the Test Input grid.
3. Generate the final predicted output grid.

Respond ONLY with the final predicted grid array.

Your response:
"""
    else:
        prompt = f"""
You are the Executor Node. Your task is to execute the provided execution plan line-by-line using the raw constraints provided. 

-- Raw Constraints --
{state['input_data']}

-- Execution Plan --
{state['execution_plan']}

Instructions:
1. You MUST execute the plan step-by-step.
2. For each step, explicitly write out your intermediate calculations, especially when converting local timezones to UTC. Do not skip steps or do math silently.
4. You must wrap your final answer only with no additional text in strict XML tags exactly like this: <FINAL_ANSWER>your_answer</FINAL_ANSWER>.

Begin your step-by-step execution below:
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "current_response": response.content, 
        "tokens_used": track_tokens(state, response)
    }


# ==========================================
# Nodes for Level 2B (Solver-Critic)
# ==========================================
def solver_node(state: AgentState):
    # If the critic sent it back, inject the feedback
    if state.get("critique"):
        # prompt = f"Fix this error based on the feedback.\nProblem: {state['input_data']}\nFeedback: {state['critique']}"
        if state['domain'] == "ARC-AGI":
            prompt = f"""
You are participating in a puzzle solving competition. You are an expert at solving puzzles.
Your previous attempt to solve the puzzle was audited and rejected by the Critic node due to logical or spatial errors.

-- Original Puzzle --
{state['input_data']}

-- Your Previous Failed Attempt --
{state['current_response']}

-- Critic's Feedback --
{state['critique']}

-- Instructions --
1. Analyze the Critic's feedback carefully to understand your geometric, spatial, or color miscalculation.
2. Formulate a corrected, explicit transformation rule.
3. Apply the corrected rule to the Test Input to generate a new final output grid.

Your response must include your corrected step-by-step inferred rule followed by the final predicted grid array.

Your response:
"""
        else:
            prompt = f"""
You are the Solver Node. Your previous solution was reviewed by a Critic and found to contain errors. 

Here is the context:
{state['input_data']}

-- Previous Proposed Slot --
{state['current_response']}

-- Critic Feedback --
{state['critique']}

Your task:
1. Carefully review the Critic's feedback.
2. Re-evaluate the initial constraints.
3. Correct your timezone math or overlap logic.
4. Output a revised candidate slot.

Return only the final answer, with no additional text.
"""
    else:
        if state['domain'] == "ARC-AGI":
            prompt = f"""
You are participating in a puzzle solving competition. You are an expert at solving puzzles.

{state['input_data']}

Your response must include your step-by-step inferred rule followed by the final predicted grid array. 

Your response:
"""
        else:
            prompt = f"""
You are the Solver Node in a multi-agent scheduling system. Your role is to analyze scheduling constraints and propose a valid solution.

{state['input_data']}

Return only the final answer, with no additional text.
"""
        
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "current_response": response.content, 
        "tokens_used": track_tokens(state, response),
        "loop_count": state.get("loop_count", 0) + 1
    }

def critic_node(state: AgentState):
    if state['domain'] == "ARC-AGI":
        prompt = f"""
You are an elite mathematical and spatial logic auditor validating a candidate solution for a puzzle solving competition.

-- Objective --
Review the Candidate's inferred transformation rule and their predicted output grid against the provided Training Examples. Your job is to find any logical, geometric, or color contradictions.

-- Original Puzzle --
{state['input_data']}

-- Candidate's Attempt (Rule + Predicted Grid) --
{state['current_response']}

-- Your Audit Checklist --
1. Protocol Compliance: Is the predicted output a valid 2D matrix of integers (0-9) without violating the max 30x30 size limit?
2. Dimension Check: Does the predicted grid size scale correctly based on the input-to-output grid size patterns seen in the training examples?
3. Color/Palette Check: Does the predicted grid introduce any unauthorized colors, or miss a newly introduced background/foreground color rule?
4. Shape/Topological Check: Does the count, positioning, rotation, or scaling of shapes match the core logic of the training transformations?

-- Output Format --
If the candidate's inferred rule and final predicted grid are perfectly accurate and free of errors, respond exactly with: PASSED
If there is an error in either the logic or the generated grid, provide a concise, step-by-step critique explaining exactly where the grid matrix layout or color usage violates the puzzle's implicit rules.
"""
    else:
        prompt = f"""
You are the Critic Node. Your sole purpose is to audit the Solver's proposed schedule for absolute accuracy. Do not solve the problem from scratch; instead, rigorously stress-test the Solver's math.

Inputs to evaluate:
{state['input_data']}

-- Solver's Proposal --
{state['current_response']}

Checklist:
1. Did the Solver convert the timezones correctly? (Double-check UTC offsets).
2. Does the proposed UTC slot *actually* fall within every single participant's local availability? 
3. Is the proposed slot exactly 1 hour long?
4. Is it the *earliest* possible slot?

-- Output format --
If the solver's proposed UTC slot is accurate, respond exactly with: PASSED
If there is an error, provide a precise, step-by-step explanation of exactly where the math or logic failed.
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "critique": response.content if "PASSED" not in response.content else None,
        "tokens_used": track_tokens(state, response)
    }


def route_after_critique(state: AgentState):
    MAX_RETRIES = 10  # The hard brake
    
    # 1. Success Condition
    if state.get("critique") is None:
        return END
        
    # 2. Safety Brake Condition
    if state.get("loop_count", 0) >= MAX_RETRIES:
        print(f"⚠️ Max retries ({MAX_RETRIES}) reached. Terminating graph to save tokens.")
        return END
        
    # 3. Continue Loop
    return "solver"


# ==========================================
# STEP 5: Graph Compilations
# ==========================================

# 1. Compile Baseline Graph
b_builder = StateGraph(AgentState)
b_builder.add_node("agent", call_baseline_agent)
b_builder.set_entry_point("agent")
b_builder.add_edge("agent", END)
baseline_graph = b_builder.compile()

# 2. Compile Planner-Executor Graph
pe_builder = StateGraph(AgentState)
pe_builder.add_node("planner", planner_node)
pe_builder.add_node("executor", executor_node)
pe_builder.set_entry_point("planner")
pe_builder.add_edge("planner", "executor")
pe_builder.add_edge("executor", END)
pe_graph = pe_builder.compile()

# 3. Compile Solver-Critic Graph
sc_builder = StateGraph(AgentState)
sc_builder.add_node("solver", solver_node)
sc_builder.add_node("critic", critic_node)
sc_builder.set_entry_point("solver")
sc_builder.add_edge("solver", "critic")
sc_builder.add_conditional_edges("critic", route_after_critique)
sc_graph = sc_builder.compile()