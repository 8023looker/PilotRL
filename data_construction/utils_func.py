import ujson
import json
from typing import Optional, Sequence, Union, Dict, List
import io
import subprocess
import os
import re
import json_repair

def _make_r_io_base(f, mode: str):
    if not isinstance(f, io.IOBase):
        f = open(f, mode=mode)
    return f

def jload_agent_jsonl(f, dataset_name, mode="r"):
    f = _make_r_io_base(f, mode)
    jdict = []
    for line in f:
        cur_data_dict = json.loads(line)
        jdict.append(cur_data_dict)
    return jdict

def judge_true_false_by_score(result):
    if isinstance(result, dict):
        if "score" in result:
            if isinstance(result["score"], int):
                score = result["score"]
                if score >= 5:
                    return True
    return False

def judge_true_false_by_score_agent(result, ref_trajectory=False):
    if isinstance(result, dict):
        if "correctness_score" in result and "followability_score" in result and "standardization_score" in result:
            if isinstance(result["correctness_score"], int) and isinstance(result["followability_score"], int) and isinstance(result["standardization_score"], int):
                score = (result["correctness_score"] + result["followability_score"] + result["standardization_score"]) / 3
                if ref_trajectory: # ref_trajectory=True
                    if score >= 4.5 and result["correctness_score"] >= 4 and result["followability_score"] >= 5 and result["standardization_score"] >= 5:
                        return True
                else:
                    if score >= 5 and result["correctness_score"] >= 5 and result["followability_score"] >= 5 and result["standardization_score"] >= 5:
                        return True
    return False


def count_lines_number(file_path):
    if os.path.exists(file_path):
        try:
            result = subprocess.run(['wc', '-l', file_path], stdout=subprocess.PIPE, text=True, check=True)
            output = result.stdout.strip()
            line_count = int(output.split()[0])
            return line_count
        except subprocess.CalledProcessError as e:
            print(f"执行命令时发生错误: {e}")
            return None
        except FileNotFoundError:
            print(f"未找到 wc 命令或文件 {file_path} 未找到。")
            return None
        except Exception as e:
            print(f"读取文件时发生错误: {e}")
            return None
    else:
        return 0
    
    
def read_res_json(sample, default=Dict):
    if default == List:
        result = []
    else:
        result = {}
    if not sample:
        return result
    # 取最后一个 json
    if "```json" in sample:
        content = sample.split("```json")[-1].split("```")[0].strip()
    # 列表
    elif default == List:
        content = "[]"
        regex = re.search(r"\[.*\]", sample, re.S)
        if regex:
            content = regex.group()
    # 字典
    else:
        content = "{}"
        regex = re.search(r"\{.*\}", sample, re.S)
        if regex:
            content = regex.group()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        try:
            result = json_repair.loads(content)
            # result = commentjson.loads(content)
        except:
            if "“" in content or "”" in content:
                content = content.replace("“", "\"").replace("”", "\"")
                try:
                    result = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"parse json error: {content}")
            else:
                print(f"parse json error: {content}")
    return result