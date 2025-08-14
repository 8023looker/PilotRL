R1_ORIGIN_PROMPT = """
A conversation between User and Assistant. The User asks a question, and the Assistant solves it. The Assistant first thinks about the reasoning process in the mind and then provides the User with the answer. \
The reasoning process is enclosed within <think> </think> and answer is enclosed within <answer> </answer> tags, respectively, i.e., <think> reasoning process here </think> <answer> answer here </answer>. User: {prompt}
Assistant: <think>
""".strip()

R1_INSTRUCT_SYSTEM_PROMPT = """
A conversation between User and Assistant. The User asks a question, and the Assistant solves it. The Assistant first thinks about the reasoning process in the mind and then provides the User with the answer. \
The reasoning process is enclosed within <think> </think> and answer is enclosed within <answer> </answer> tags, respectively, i.e., <think> reasoning process here </think> <answer> answer here </answer>.
""".strip()

R1_ORIGIN_PROMPT_ADD_LANGUAGE = """
A conversation between User and Assistant. The User asks a question, and the Assistant solves it. The Assistant first thinks about the reasoning process in the mind and then provides the User with the answer. \
The reasoning process is enclosed within <think> </think> and answer is enclosed within <answer> </answer> tags, respectively, i.e., <think> reasoning process here </think> <answer> answer here </answer>. \
Please answer with the same language as the question.
User: {prompt}
Assistant: <think>
""".strip()

R1_INSTRUCT_SYSTEM_PROMPT_ADD_LANGUAGE = """
A conversation between User and Assistant. The User asks a question, and the Assistant solves it. The Assistant first thinks about the reasoning process in the mind and then provides the User with the answer. \
The reasoning process is enclosed within <think> </think> and answer is enclosed within <answer> </answer> tags, respectively, i.e., <think> reasoning process here </think> <answer> answer here </answer>. \
Please answer with the same language as the question.
""".strip()

R1_ORIGIN_PROMPT_ADD_LANGUAGE_V2 = """
A conversation between User and Assistant. The User asks a question, and the Assistant solves it. The Assistant first thinks about the reasoning process in the mind (invisible to the User) and then provides the User with the answer. \
The step-by-step reasoning process is enclosed within <think> </think> and followed by the wrap-up answer, i.e., <think> reasoning process here </think> answer here. \
Think and answer with the same language as the question.
User: {prompt}
Assistant: <think>
""".strip()

# For the medical domain, we need to add the search function
R1_ORIGIN_PROMPT_ADD_LANGUAGE_AND_SEARCH = """You are a medical expert.  
Given a question, you should answer it by first thinking about the reasoning process in the mind and then providing the final answer. 
Please answer the question in the format of <think>...</think><answer>...</answer>. 
That is, <think>Here is the reasoning process</think><answer>Here is the answer</answer>. 
You should perform thinking with decomposing, reflecting, brainstorming, verifying, refining, and revising. 
Besides, you can perform searching for uncertain knowledge if necessary with the format of <search> search query </search> during your thinking process.
Then, the search system will provide you with the retrieval information with the format of <document> search results </document>.
Think and answer with the same language as the question.

Quesion: {prompt}
Response: <think>
""".strip()


R1_INSTRUCT_SYSTEM_PROMPT_ADD_LANGUAGE_V2 = """
A conversation between User and Assistant. The User asks a question, and the Assistant solves it. The Assistant first thinks about the reasoning process in the mind (invisible to the User) and then provides the User with the answer. \
The step-by-step reasoning process is enclosed within <think> </think> and followed by the wrap-up answer, i.e., <think> reasoning process here </think> answer here. \
Think and answer with the same language as the question.
""".strip()

R1_INSTRUCT_USER_PROMPT = """
{prompt}
""".strip()

MCQA_PROMPT = """
answer the following multiple choice question.
## question: 
{question}
## options: 
{options}
The last line of your response should be of the following format: 'ANSWER: $LETTER' (without quotes) where LETTER is one of {letter}.
"""