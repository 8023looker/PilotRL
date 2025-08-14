""" generate traj plans based on deepseek-v3 model """
""" parallel processing """
""" Agent Dataset """
""" All possible global plans """

import os
import json
import ujson
import openai
from tqdm import tqdm
import sys
import re
import concurrent.futures
import copy
import time
import requests
import subprocess
from typing import List, Dict

import prompts
import utils_func

# API setting constants
API_MAX_RETRY = 10
API_RETRY_SLEEP = 1
API_ERROR_OUTPUT = "$ERROR$"
PARALLELISM = 10 # 100

MAX_ATTEMPT = 10

MAX_TOKEN = {
    "deepseek-r1": 7400,
    "deepseek-v3": 8192,
}


class DeepSeekPlanningTemplate: # retrieval-augmented reasoning
    def __init__(self, infer_model_name, verify_model_name, api_source, dataset_name, hit_size=20, timeout=2000):
        self.dataset_name = dataset_name
        self.api_source = api_source
        if self.api_source == "xxx":
            self.client = openai.OpenAI(
                base_url="xxx",
                api_key="sk-xxx")
        elif self.api_source == "xxx":
            self.client = openai.OpenAI(
                base_url="xxx",
                api_key="sk-xxx")
        self.infer_model = infer_model_name
        self.verify_model = verify_model_name
        
        # query
        self.url = "xxx"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'xxx',
        }
        
        
    def verify_quality(self, global_plan, query_dict, temperature=0.9, require_json=True): # verify the correctness of the generated answer (output: score[int])
        # verification based on deepseek-v3
        print("------ Start to verify ------")
        # global_plan = utils_func.read_res_json(global_plan, default=List)
        print("global_plan", global_plan)
        verify_prompt = prompts._GOLDEN_GLOBAL_PLAN_EVALUATION_PROMPT.format(
            task=query_dict["conversations"][0]["value"],
            global_plan=global_plan,
            conversation="\n".join([f"{item['from']}: {item['value']}" for item in query_dict["conversations"][1:]]),
        )
        verify_resp = ""
        verify_succeed = False
        while not verify_succeed:
            try:
                verify_response = self.client.chat.completions.create(
                    model=self.verify_model, # deepseek-v3
                    messages=[
                        {"role": "user", "content": verify_prompt}
                    ], 
                    temperature=temperature,
                    max_tokens=MAX_TOKEN[self.verify_model], 
                    stream=False, # True, 
                    **({"response_format": {"type": "json_object"}} if require_json else {})
                )
                verify_resp = verify_response.choices[0].message
                verify_succeed = True
            except Exception as e:
                print(f"Unexpected error: {e}. Retrying in {API_RETRY_SLEEP} seconds...")
                time.sleep(API_RETRY_SLEEP)
        
        if require_json:
            try:
                return utils_func.read_res_json(verify_resp.content, default=Dict) # {"score": int, "reason": str}
            except json.JSONDecodeError:
                # return {"score": 0, "reason": "JSONDecodeError"}
                return {
                        "correctness_score": 0,
                        "correctness_reason": "JSONDecodeError",
                        "followability_score": 0,
                        "followability_reason": "JSONDecodeError",
                        "standardization_score": 0,
                        "standardization_reason": "JSONDecodeError"
                    }
        else:
            return verify_resp
        
        
    def get_global_plan(self, query_dict, total_template_num=1, temperature=0.9, require_json=True):
        qualified_plan_list, model_plan_verify_list = [], []
        gen_succeed = False
        
        while not gen_succeed:
            global_plan_list = self.gen_infer_response(query_dict=query_dict, require_json=True) # for each chain of the template [List]
            print("global_plan_list", global_plan_list)
            qualified_plan_list = []
            for plan_idx, cur_global_plan in enumerate(global_plan_list):
                verify_content = self.verify_quality(cur_global_plan, query_dict)
                print("VERIFY_CONTENT", verify_content)
                if utils_func.judge_true_false_by_score_agent(verify_content, ref_trajectory=True): # valid response
                    qualified_plan_list.append(cur_global_plan)
                    model_plan_verify_list.append(verify_content) # {"score": int, "reason": str}
                    print(f"{plan_idx}------PASS!")
                else:
                    print(f"{plan_idx}------FAIL!")
            if len(qualified_plan_list) >= max(total_template_num, len(global_plan_list) * 0.5): # 50% valid response
                gen_succeed = True
            else:
                print("Retrying to generate global plans...")
                qualified_plan_list, model_plan_verify_list = [], []
                time.sleep(1)

        return {
            "global_plan_templates": qualified_plan_list, 
            "template_verify": model_plan_verify_list
        }
      
    
    def gen_infer_response(self, query_dict, temperature=0.9, require_json=True): # think → search → think ...
        infer_prompt = prompts._GOLBAL_PLANNING_PROMPT[self.dataset_name].format(
            task=query_dict["conversations"][0]["value"],
        )
        infer_response = ""
        while True:
            try:
                infer_response = self.client.chat.completions.create(
                    model=self.infer_model, # deepseek-v3
                    messages=[
                        {"role": "user", "content": infer_prompt}
                    ], 
                    temperature=temperature,
                    max_tokens=MAX_TOKEN[self.infer_model], 
                    stream=False, # True, 
                    **({"response_format": {"type": "json_object"}} if require_json else {})
                )
                infer_resp = infer_response.choices[0].message
                if require_json:
                    infer_response = utils_func.read_res_json(infer_resp.content, default=List) # .strip("```json`")
                else:
                    infer_response = infer_resp.content
                break
            except Exception as e:
                print(f"Unexpected error: {e}. Retrying in {API_RETRY_SLEEP} seconds...")
                time.sleep(API_RETRY_SLEEP)
        return infer_response
        
    
    def handle_file(self, file_path, dataset_name, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        jdict = utils_func.jload_agent_jsonl(file_path, dataset_name) # return: List
        
        output_file_line_num = utils_func.count_lines_number(os.path.join(output_dir, os.path.basename(file_path)))
        print(f"{os.path.join(output_dir, os.path.basename(file_path))}: {output_file_line_num}")
        
        if output_file_line_num != None:
            with open(os.path.join(output_dir, os.path.basename(file_path)), "a", encoding="utf-8") as fout:
                for index, item in enumerate(tqdm(jdict, desc=f"Processing {dataset_name}", total=len(jdict))):
                    if index < output_file_line_num: # 断点重启
                        continue
                    
                    query_dict = {
                        "conversations": item["conversations"],
                    }
                    response = self.get_global_plan(query_dict, total_template_num=1, temperature=0.9, require_json=False)
                    output_instance_dict = {**item, **response}
                    fout.write(ujson.dumps(output_instance_dict, ensure_ascii=False) + "\n")         


if __name__ == "__main__":
    root_folder = "/data/agent/code/data_construction/raw_dataset/"
    dataset_name = sys.argv[1] if len(sys.argv) > 1 else None
    if dataset_name is None:
        print("Please provide the dataset_name as a command-line argument.")
        sys.exit(1)
        
    infer_model = "deepseek-v3" # "deepseek-v3" # 'deepseek-r1'
    verify_model = "deepseek-v3" # "deepseek-v3"
    api_source = "xxx" # fill in your api source
    deepseek_instance = DeepSeekPlanningTemplate(infer_model, verify_model, api_source, dataset_name)
    
    print("dataset_name", dataset_name)
    
    output_root_folder = "/data/agent/code/data_construction/output/"
    output_folder = os.path.join(output_root_folder, dataset_name)
    os.makedirs(output_folder, exist_ok=True)
    
    args_list = []
    raw_data_folder = os.path.join(root_folder, dataset_name)
    for dirpath, dirnames, filenames in os.walk(raw_data_folder):
        for i, filename in enumerate(tqdm(filenames, total=len(filenames))):
            file_path = os.path.join(dirpath, filename)
            args_list.append((file_path, dataset_name, output_folder))
            
    with concurrent.futures.ThreadPoolExecutor(max_workers=PARALLELISM) as executor:
        futures = [executor.submit(deepseek_instance.handle_file, item[0], item[1], item[2]) for item in args_list]
        results = [future.result() for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures))]