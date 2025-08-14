import re
import os
import sys
import json
from tqdm import tqdm
import pandas
import pyarrow.parquet as pq
import pyarrow as pa

_GLOBAL_PLAN_SELECTION_PROMPT = {
    "alfworld": """
Interact with a household to solve a task. Imagine you are an intelligent agent in a household environment and your target is to perform actions to complete the task goal. At the beginning of your interactions, you will be given the detailed description of the current environment and your goal to accomplish.
For each of your turn, you will be given the observation of the last turn. You should choose from two actions: "Thought" or "Action". If you choose "Thought", you should first think about the current condition and plan for your future actions, and then output your action in this turn. Your output must strictly follow this format: "Thought: your thoughts.\n Action: your next action"; If you choose "Action", you should directly output the action in this turn. Your output must strictly follow this format: "Action: your next action".
You are given several global plans serving as high-level, natural guidance to assist in planning. 
Please select the most suitable global plan from all available global plans to accomplish the task, and take action according to its instructions.

The available actions are:
1. go to recep
2. take obj from recep
3. put obj in/on recep
4. open recep
5. close recep
6. toggle obj recep
7. clean obj with recep
8. heat obj with recep
9. cool obj with recep
where obj and recep correspond to objects and receptacles.

After your each turn, the environment will give you immediate feedback based on which you plan your next few steps. if the environment output "Nothing happened", that means the previous action is invalid and you should try more options.

Reminder:
1. The action must be chosen from the given available actions. Any actions except provided available actions will be regarded as illegal.
2. Think when necessary, try to act directly more in the process.

---
Here is an example.
{example}
---

Now, it's your turn and here is the instruction.
<instruction>
{instruction}
</instruction>
""",

"iqa": """
Imagine you are an intelligent agent in a dynamic visual environment and your target is to perform actions to complete the task goal. At the beginning of your interactions, you will be given the detailed description of the current environment and your goal to accomplish. 
For each of your turn, you will be given the observation of the last turn. You should choose from two actions: "Thought" or "Action". If you choose "Thought", you should first think about the current condition and plan for your future actions, and then output your action in this turn. Your output must strictly follow this format: "Thought: your thoughts.\n Action: your next action"; If you choose "Action", you should directly output the action in this turn. Your output must strictly follow this format: "Action: your next action".
You are given several global plans serving as high-level, natural guidance to assist in planning. 
Please select the most suitable global plan from all available global plans to accomplish the task, and take action according to its instructions.

The available actions are:
1. move ahead
2. turn left
3. turn right
4. open obj
5. answer [True]/[False]
where obj correspond to objects. 

After your each turn, the environment will give you immediate feedback based on which you plan your next few steps. if the environment output "Nothing happened", that means the previous action is invalid and you should try more options.

Reminder:
1. The action must be chosen from the given available actions. Any actions except provided available actions will be regarded as illegal.
2. Think when necessary, try to act directly more in the process.

---
Here is an example.
{example}
---

Now, it's your turn and here is the instruction.
<instruction>
{instruction}
</instruction>
""",

"textcraft": """
You are given a few useful crafting recipes to craft items in Minecraft. Crafting commands are of the format ``craft [target object] using [input ingredients]''. Every round I will give you an observation, you have to respond to an action based on the state and instruction. 
For each of your turn, you will be given the observation of the last turn. You should choose from two actions: "Thought" or "Action". If you choose "Thought", you should first think about the current condition and plan for your future actions, and then output your action in this turn. Your output must strictly follow this format: "Thought: your thoughts.\n Action: your next action"; If you choose "Action", you should directly output the action in this turn. Your output must strictly follow this format: "Action: your next action".
You are given several global plans serving as high-level, natural guidance to assist in planning. 
Please select the most suitable global plan from all available global plans to accomplish the task, and take action according to its instructions.

The available actions are:
1. move ahead
2. turn left
3. turn right
4. open obj
5. answer [True]/[False]
where obj correspond to objects. 

After your each turn, the environment will give you immediate feedback based on which you plan your next few steps. if the environment output "Nothing happened", that means the previous action is invalid and you should try more options.

Reminder:
1. The action must be chosen from the given available actions. Any actions except provided available actions will be regarded as illegal.
2. Think when necessary, try to act directly more in the process.

---
Here is an example.
{example}
---

Now, it's your turn and here is the instruction.
<instruction>
{instruction}
</instruction>
""",

"wordle": """
You are an expert wordle player. Welcome to the game of Wordle. Your objective is to guess a hidden 5 letter word. You have 6 attempts to guess it correctly and you should try to guess it in as few attempts as possible. When guessing the word, you should format your word as a space separated sequence of letters, like ``s h i r e'' for example. After guessing the word, you will receive feedback from the game environment in the form of a sequence of 5 space separated letters like ``b y g g b'', where each letter indicates some information about the hidden word. The environment will return one of three letters - ``b'', ``g'', or ``y'' – for each letter in the word you guessed. Here is the meaning of each letter: 

1. "b": If the environment returns a “b”, it means that the letter at that position in your guessed word is not in the hidden word.
2. "y": If the environment returns a “y”, it means that the letter at that position in your guessed word is in the hidden word but is not in the correct position.
3. "g": If the environment returns a “g”, it means that the letter at that position in your guessed word is in the hidden word and is in the correct position.

You are given several global plans serving as high-level, natural guidance to assist in planning. 
Please select the most suitable global plan from all available global plans to accomplish the task, and take action according to its instructions.

The available actions are:
1. move ahead
2. turn left
3. turn right
4. open obj
5. answer [True]/[False]
where obj correspond to objects. 

After your each turn, the environment will give you immediate feedback based on which you plan your next few steps. if the environment output "Nothing happened", that means the previous action is invalid and you should try more options.

Reminder:
1. The action must be chosen from the given available actions. Any actions except provided available actions will be regarded as illegal.
2. Think when necessary, try to act directly more in the process.

---
Here is an example.
{example}
---

Now, it's your turn and here is the instruction.
<instruction>
{instruction}
</instruction>
""",
}

_SYSTEM_INITIAL_DYNAMIC_GLOBAL_PLAN_PROMPT="""
You are a helpful assistant that generates global plans for the following tasks. Your task is to generate all possible step-by-step global plans for the task, which serve as high-level, natural guidance to assist in planning.
"""

_INITIAL_DYNAMIC_GLOBAL_PLAN_PROMPT="""
Please generate all possible step-by-step global plans for the agent task, which serve as high-level, natural guidance to assist in planning.
The generated global plans should be written in the following format:
```json
["
Step 1: ...
Step 2: ...
...
", ...]
```

All possible global plans:
"""

import time
from typing import List, Dict
import json_repair
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt import *
from agent_api import oneapi_post_by_langchain

request_params = {
    "url": "xxx",
    "model": "",
    "key": "EMPTY", 
    "max_tokens": 4096,
    "temperature": 0.9, 
    "top_p": 1.0, 
    "max_concurrency": 8, 
    "base_model": None,
}

def initialize_data_global_plans(
    instruction_text: str, 
    params: Dict = None
):
    
    user_global_plans_prompt = instruction_text + _INITIAL_DYNAMIC_GLOBAL_PLAN_PROMPT
    system_global_plans_prompt = _SYSTEM_INITIAL_DYNAMIC_GLOBAL_PLAN_PROMPT

    stt = time.time()
    global_plan_result = oneapi_post_by_langchain(
        prompt=user_global_plans_prompt,
        system_prompt=system_global_plans_prompt,
        # base_model=Score,
        **params
    )
    edt = time.time()
    print("edt - stt:", edt - stt)
    print(f"global_plan_result: {global_plan_result}")
    return global_plan_result

def initialize_data_global_plans_batch(
    instruction_text_list: List[str], 
    params: Dict = None
):
    
    user_global_plans_prompt = [instruction_text + _INITIAL_DYNAMIC_GLOBAL_PLAN_PROMPT for instruction_text in instruction_text_list]
    system_global_plans_prompt = _SYSTEM_INITIAL_DYNAMIC_GLOBAL_PLAN_PROMPT

    global_plan_result_list = []
    batch_size = 256
    stt = time.time()
    for i in range(0, len(user_global_plans_prompt), batch_size):
        global_plan_result_list += oneapi_post_by_langchain(
            prompt=user_global_plans_prompt[i:i+batch_size],
            system_prompt=system_global_plans_prompt,
            **params
        )
    edt = time.time()
    print("edt - stt:", edt - stt)
    return global_plan_result_list

if __name__ == '__main__':

    data_source_list = ["alfworld", "iqa", "textcraft", "wordle"] # for training
    output_path = f"/global_data/data/agent/code/myverl/data/train/agent_data_add_plan.parquet"
    for data_source in data_source_list:
        choose_path = ""
        path = f"/global_data/data/agent/data_construction/output/{data_source}.jsonl"
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        choose_questions = []
        if os.path.exists(choose_path):
            for line in open(choose_path, "r", encoding="utf-8").readlines():
                line = line.strip()
                item = json.loads(line)
                choose_questions.append(item["question"])
        choose_questions = set(choose_questions)
        print(f"choose_questions: {len(choose_questions)}")
        
        new_data = []
        line_idx = 0
        example_str = ""
        for line in tqdm(open(path, "r", encoding="utf-8").readlines()):
            line = line.strip()
            item = json.loads(line)
            if choose_questions and (item["question"] not in choose_questions and item["reformat_question"] not in choose_questions):
                continue
            
            # process "example"
            if line_idx == 0:
                for conversation in item["conversations"]:
                    if conversation["from"] == "human":
                        example_str += f"Human: {conversation['value']}\n"
                    elif conversation["from"] == "gpt":
                        example_str += f"GPT: {conversation['value']}\n"
                example_str = example_str.strip()
            else:
                pass
            
            conversations = ""
            for idx, conversation in enumerate(item["conversations"]):
                if idx >= 1:
                    if conversation["from"] == "human":
                        conversations += f"Human: {conversation['value']}\n"
                    elif conversation["from"] == "gpt":
                        conversations += f"GPT: {conversation['value']}\n"
            conversations = conversations.strip()

            new_item = {
                "data_source": data_source,
                "reward_actor": "RewardActorAgentStage1", # "RewardActorAgentStage1", "RewardActorAgentStage2", "RewardActorAgentStage3"
                "prompt": _GLOBAL_PLAN_SELECTION_PROMPT[data_source].format(
                    example=example_str,
                    instruction=item["conversations"][0]["value"],
                    # observation="", # previous observation
                    # global_plans="", # global plans
                ),
                "reward_model": {
                    "style": "rule",
                    "ground_truth": item["conversations"][-1]["value"],
                },
                "extra_info": {
                    "example": example_str, 
                    "instruction": item["conversations"][0]["value"],
                    "observation": "", # previous observation
                    "global_plans": "", # global plans
                    "agent_action": "", # agent action
                    "execution_step_index": 0, # int
                    "conversations": conversations, 
                    "index": len(new_data),
                }
            }
            # 串行太慢了
            # new_item["extra_info"]["global_plans"] = initialize_data_global_plans(
            #     instruction_text=new_item["prompt"],
            #     params=request_params
            # )
            
            new_data.append(new_item)
            
            line_idx += 1
    
    # 并行
    instruction_text_list = []
    for idx, new_item in tqdm(enumerate(new_data)):
        instruction_text_list.append(new_item["prompt"])
    global_plan_result_list = initialize_data_global_plans_batch(
        instruction_text_list=instruction_text_list,
        params=request_params
    )
    for idx, new_item in tqdm(enumerate(new_data)):
        new_data[idx]["extra_info"]["global_plans"] = global_plan_result_list[idx]
     
    # to parquet
    df = pandas.DataFrame(new_data)
    print(df)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_path)
