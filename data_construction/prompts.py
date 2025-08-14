import ujson
import json

_GOLBAL_PLANNING_PROMPT = {
    "alfworld_old": """
Please generate a step-by-step global plan for a house holding task, which serves as high-level, natural guidance to assist in planning.
The action list you can take:
1. go to recep
2. task obj from recep
3. put obj in/on recep
4. open recep
5. close recep
6. toggle obj recep
7. clean obj with recep
8. heat obj with recep
9. cool obj with recep
where obj and recep correspond to objects and receptacles.

The generated global plan should be written in the following format:
<global_plan>
Step 1: ...
Step 2: ...
...
</global_plan>

---
For instance, given the instruction "look at the CD under the desklamp", the global plan could be:
<global_plan>
Step 1: Go to where the CD may be placed.
Step 2: Take the CD from where you found it.
Step 3: Go to where the desklamp is located.
Step 4: Use the CD to look at the desklamp.
</global_plan> 
---

<task>
{task}
</task>

Global plan:
""",

"alfworld": """
Please generate all possible step-by-step global plans for the house holding task, which serve as high-level, natural guidance to assist in planning.
The action list you can take:
1. go to recep
2. task obj from recep
3. put obj in/on recep
4. open recep
5. close recep
6. toggle obj recep
7. clean obj with recep
8. heat obj with recep
9. cool obj with recep
where obj and recep correspond to objects and receptacles.

The generated global plans should be written in the following format:
```json
["
Step 1: ...
Step 2: ...
...
", ...]
```

---
For instance, given the instruction "look at the CD under the desklamp", the possible global plans could be:
```json
["
Step 1: Go to where the CD may be placed.
Step 2: Take the CD from where you found it.
Step 3: Go to where the desklamp is located.
Step 4: Use the CD to look at the desklamp.
", ...]
```
---

<task>
{task}
</task>

All possible global plans:
""",

"webshop": """
Please generate all possible step-by-step global plans for the web shopping task, which serve as high-level, natural guidance to assist in planning.
The action list you can take:
1. click something
2. search something
Below are the meanings of the actions:
click something: Engage with specific buttons or links.
search something: Seek specific data on the website. Use this only if a [Search] button appears in the observation.

The generated global plans should be written in the following format:
```json
["
Step 1: ...
Step 2: ...
...
", ...]
```

---
For instance, given the instruction "find a red dress under $100", the possible global plans could be:
```json
["
Step 1: Search[red dress under $100].
Step 2: Click an item that matches the criteria.
Step 3: Click to add it to the shopping cart.
Step 4: Click[Buy Now] to complete the purchase.
", ...]
```
---

<task>
{task}
</task>

All possible global plans:
""",

"webarena": """
Please generate all possible step-by-step global plans for the web-based task, which serve as high-level, natural guidance to assist in planning.

The action list you can take:

1. Page Operation Actions:
(1) 'click [id]': This action clicks on an element with a specific id on the webpage.
(2) 'type [id] [content] [press_enter_after = 0 |1]': Use this to type the content into the field with id. By default, the "Enter" key is pressed after typing unless press_enter_after is set to 0.
(3) 'hover [id]': Hover over an element with id.
(4) 'press [key_comb]': Simulates the pressing of a key combination on the keyboard (e.g., Ctrl+v).
(5) 'scroll [direction n= down lup]': Scroll the page up or down.

2. Tab Management Actions:
(1) 'new_tab': Open a new, empty browser tab.
(2) 'tab_focus [tab_index]': Switch the browser's focus to a specific tab using its index.
(3) 'close_tab': Close the currently active tab.

3. URL Navigation Actions:
(1) 'goto [url]': Navigate to a specific URL.
(2) 'go_back': Navigate to the previously viewed page.
(3) 'go_forward': Navigate to the next page (if a previous 'go_back' action was performed).

4. Completion Action:
'stop [answer]': Apply this action when you believe the task is complete. If it is a operation-type task, use 'stop [Done]' when finished. If the objective is to give a text-based answer, provide the answer in the bracket.

The generated global plans should be written in the following format:
```json
["
Step 1: ...
Step 2: ...
...
", ...]
```

---
For instance, given the instruction "add a white desk to my wish list", the possible global plans could be:
```json
["
Step 1: Navigate to the website's homepage using 'goto [url]'.
Step 2: Locate the search bar and input 'white desk' using 'type [id] [content] [press_enter_after=1]'.
Step 3: Browse through the search results to identify the desired white desk.
Step 4: Click on the desired white desk item from the search results using 'click [id]'.
Step 5: On the product page, locate and click the 'Add to Wish List' button using 'click [id]'.
Step 6: Confirm that the item has been successfully added to the wish list.
Step 7: End the task using 'stop [Done]'.
", ...]
```
---

<task>
{task}
</task>

All possible global plans:
""",

"textcraft": """
Please generate all possible step-by-step global plans for the item crafting task, which serve as high-level, natural guidance to assist in planning. 
You are given a few useful crafting recipes to craft items in Minecraft. Craft command can be understood as follows: craft [target] using [ingredients], where target is item/object generated by the craft command as output and ingredient are the inputs. You are given an agent that can "craft" or "fetch" objects. You can take the help of crafting commands below to create new objects. Each global plan can use at most ONE of the provided crafting commands.

The generated global plans should be written in the following format:
```json
["
Step 1: ...
Step 2: ...
...
", ...]
```

---
For instance, given the crafting commands:
craft 3 dark oak sign using 6 dark oak planks, 1 stick
craft 4 dark oak planks using 1 dark oak log
craft 1 stick using 1 planks
craft 4 stick using 2 bamboo
craft 4 oak planks using 1 oak log
craft 1 dark oak fence using 2 stick, 4 dark oak planks
craft 1 warped stairs using 6 warped planks
craft 3 oak sign using 6 oak planks, 1 stick
Goal: craft dark oak sign.

The possible global plans could be:
```json
["
Step 1: Fetch 6 dark oak planks.
Step 2: Fetch 1 stick.
Step 3: Craft dark oak sign using 6 dark oak planks, 1 stick.
", ...]
```
---

<crafting_commands>
{task}
</crafting_commands>

All possible global plans:
""",

"maze": """
Please generate all possible step-by-step global plans for the maze solving task, which serve as high-level, natural guidance to assist in planning.
Your objective is to reach the goal in as few steps as possible. When you move right you increase your y position by 1, when you move down you increase your x position by 1.

The action list you can take:
1. move up
2. move down
3. move left
4. move right

The generated global plans should be written in the following format:
```json
["
Step 1: ...
Step 2: ...
...
", ...]
```

---
For instance, given the current environment state:
The goal is at position 8, 6. Your current position is at position 1, 1. There are walls to your left, above you, below you. The possible global plans could be:
```json
["
Step 1: move right (from 1, 1 to 1, 2)
Step 2: move right (from 1, 2 to 1, 3)
Step 3: move right (from 1, 3 to 1, 4)
Step 4: move down (from 1, 4 to 2, 4)
Step 5: move down (from 2, 4 to 3, 4)
Step 6: move down (from 3, 4 to 4, 4)
Step 7: move down (from 4, 4 to 5, 4)
Step 8: move down (from 5, 4 to 6, 4)
Step 9: move down (from 6, 4 to 7, 4)
Step 10: move down (from 7, 4 to 8, 4)
Step 11: move right (from 8, 4 to 8, 5)
Step 12: move right (from 8, 5 to 8, 6)
", ...]
```
---

<task>
{task}
</task>

All possible global plans:
""",
# wordle task (不适合 initial global plan, 适合 re-plan)
"wordle": """ 
Please generate all possible step-by-step global plans for the wordle task, which serve as high-level, natural guidance to assist in planning.
Your objective is to guess a hidden 5 letter word. You have 6 attempts to guess it correctly and you should try to guess it in as few attempts as possible. When guessing the word, you should format your word as a space separated sequence of letters, like "s h i r e" for example. After guessing the word, you will receive feedback from the game environment in the form of a sequence of 5 space separated letters like "b y g g b", where each letter indicates some information about the hidden word. The environment will return one of three letters - "b", "g", or "y" – for each letter in the word you guessed. We describe the meaning of each letter below:
"b": If the environment returns a “b”, it means that the letter at that position in your guessed word is not in the hidden word.
"y": If the environment returns a “y”, it means that the letter at that position in your guessed word is in the hidden word but is not in the correct position.
"g": If the environment returns a “g”, it means that the letter at that position in your guessed word is in the hidden word and is in the correct position.
As a note, if you guess an invalid word (e.g. not a 5 letter word or a word not in the vocabulary), the environment will respond with an “invalid word” message. In general though, you should use this information returned by the environment to update your belief about what the hidden word might be and adjust your next guess accordingly.

The generated global plans should be written in the following format:
```json
["
Step 1: ...
Step 2: ...
...
", ...]
```

Now let’s start a new game. Remember, the word you guess should be strictly in the vocabulary. You should return your thought and your word strictly in the format mentioned above.
<task>
{task}
</task>

All possible global plans:
""",
}

# based on Qwen2.5-14B-Instruct (verify global plans generated by ds-R1)
# add original golden traj for reference
_GOLDEN_GLOBAL_PLAN_EVALUATION_PROMPT = """
Please act as a professional instruction evaluator and judge the global plan across the following three dimensions:
1. Correctness - Does the global plan accurately fulfill the task requirements?
2. Followability - Is the global plan clear, easy to understand, and are the steps reasonable?
3. Standardization - Does the global plan follow a consistent and standardized format?

For each dimension, please score the global plan on a scale of 1 to 5, where 1 indicates poor performance and 5 indicates excellent performance, and explain the reason.
Please output the result in JSON format, including the following fields:
```json
{{
    "correctness_score": xxx,
    "correctness_reason": "...",
    "followability_score": xxx,
    "followability_reason": "...",
    "standardization_score": xxx,
    "standardization_reason": "..."
}}

### Task Description: {task}

Below is the standard and detailed procedure for solving this task:
{conversation}

### Global Plan:
{global_plan}

### Judgment Result:
"""

_GOLDEN_GLOBAL_PLAN_EVALUATION_NO_TRAJ_PROMPT = """
Please act as a professional instruction evaluator and judge the global plan across the following three dimensions:
1. Correctness - Does the global plan accurately fulfill the task requirements?
2. Followability - Is the global plan clear, easy to understand, and are the steps reasonable?
3. Standardization - Does the global plan follow a consistent and standardized format?

For each dimension, please score the global plan on a scale of 1 to 5, where 1 indicates poor performance and 5 indicates excellent performance, and explain the reason.
Please output the result in JSON format, including the following fields:
```json
{{
    "correctness_score": xxx,
    "correctness_reason": "...",
    "followability_score": xxx,
    "followability_reason": "...",
    "standardization_score": xxx,
    "standardization_reason": "..."
}}

### Task Description: {task}

### Global Plan:
{global_plan}

### Judgment Result:
"""

_INTERACTION_PROMPT = {
    "alfworld": """
Interact with a household to solve a task. Imagine you are an intelligent agent in a household environment and your target is to perform actions to complete the task goal. At the beginning of your interactions, you will be given the detailed description of the current environment and your goal to accomplish.
For each of your turn, you will be given the observation of the last turn. You should choose from two actions: "Thought" or "Action". If you choose "Thought", you should first think about the current condition and plan for your future actions, and then output your action in this turn. Your output must strictly follow this format: "Thought: your thoughts.\n Action: your next action"; If you choose "Action", you should directly output the action in this turn. Your output must strictly follow this format: "Action: your next action".

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

Now, it's your turn and here is the task.
{task}

This global plan maybe helpful for you to complete the task:
{global_plan}

Previous observation:
{observation}

Your next action:
""",

"webshop": """
You are a helpful virtual webshop assistant that interacts with the simulated website to solve a task, navigating a website to locate and purchase items based on given commands. 
At the beginning of your interactions, you will be given the detailed description of the current environment and your goal to accomplish.
For each of your turn, you will be given the observation of the last turn. You should choose from two actions: "Thought" or "Action". If you choose "Thought", you should first think about the current condition and plan for your future actions, and then output your action in this turn. Your output must strictly follow this format: "Thought: your thoughts.\n Action: your next action"; If you choose "Action", you should directly output the action in this turn. Your output must strictly follow this format: "Action: your next action". Our interaction will follow this structure:

Your Actions: You will preface each of your actions with "Action: ".
Website's Response: The website will provide feedback starting with "Observation: ".

The available actions are:
1. click[something]: Engage with specific buttons or links.
2. search[something]: Seek specific data on the website. Use this only if a [Search] button appears in the observation.
Note: If you wish to search and there's no [Search] button, click the [Back to Search] button instead.

Observation Format: The website will showcase its content. Elements within square brackets (like [Buy Now]) indicate clickable buttons or links.

Reminder:
1. The action must be chosen from the given available actions. Any actions except provided available actions will be regarded as illegal.
2. Think when necessary, try to act directly more in the process.

---
Here is an example:
You should perform actions to accomplish the goal: I would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars

Action: reset[]
Observation: WEB PAGE: {
Let us begin shopping [Search]
}

Action: search[3 ounce bright citrus deodorant sensitive skin]
Observation: WEB PAGE: {
[Back to Search]
Page 1 (Total results: 15)
[Next >]
[B078GWRC1J] Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce $10.99}

Action: click[B078GWRC1J]
Observation: WEB PAGE: {
[Back to Search]
[<Prev>]
scent [assorted scents][bright citrus][calming lavender][ginger fresh][simply non-scents]
size [3 ounce (pack of 1)]}

Action: click[bright citrus]
Observation: You have clicked bright citrus.

Action: click[3 ounce (pack of 1)]
Observation: You have clicked 3 ounce (pack of 1).

Action: click[Buy Now]
Observation: You have bought 3 ounce (pack of 1).
---

Now, it's your turn and here is the task.
{task}

This global plan maybe helpful for you to complete the task:
{global_plan}

Previous observation:
{observation}

Your next action:
""",

"webarena": """
You are an autonomous intelligent agent tasked with navigating a web browser. You will be given web-based tasks. These tasks will be accomplished through the use of specific actions you can issue. At the beginning of your interactions, you will be given the detailed description of the current environment and your goal to accomplish.
For each of your turn, you will be given the observation of the last turn. You should choose from two actions: "Thought" or "Action". If you choose "Thought", you should first think about the current condition and plan for your future actions, and then output your action in this turn. Your output must strictly follow this format: "Thought: your thoughts.\n Action: your next action"; If you choose "Action", you should directly output the action in this turn. Your output must strictly follow this format: "Action: your next action".

The action list you can take:

1. Page Operation Actions:
(1) 'click [id]': This action clicks on an element with a specific id on the webpage.
(2) 'type [id] [content] [press_enter_after = 0 |1]': Use this to type the content into the field with id. By default, the "Enter" key is pressed after typing unless press_enter_after is set to 0.
(3) 'hover [id]': Hover over an element with id.
(4) 'press [key_comb]': Simulates the pressing of a key combination on the keyboard (e.g., Ctrl+v).
(5) 'scroll [direction n= down lup]': Scroll the page up or down.

2. Tab Management Actions:
(1) 'new_tab': Open a new, empty browser tab.
(2) 'tab_focus [tab_index]': Switch the browser's focus to a specific tab using its index.
(3) 'close_tab': Close the currently active tab.

3. URL Navigation Actions:
(1) 'goto [url]': Navigate to a specific URL.
(2) 'go_back': Navigate to the previously viewed page.
(3) 'go_forward': Navigate to the next page (if a previous 'go_back' action was performed).

4. Completion Action:
'stop [answer]': Apply this action when you believe the task is complete. If it is a operation-type task, use 'stop [Done]' when finished. If the objective is to give a text-based answer, provide the answer in the bracket.

To be successful, it is very important to follow the following rules:
1. You should only issue an action that is valid given the current observation
2. You should only issue one action at a time.
3. Generate the action in the correct format and always put the action inside a pair of @. Such as, @click [1234]@.
4. Complete the task by interacting with the starting page, and avoid using 'goto' actions casually.
5. Reasonable inputs will return accurate observations, so do not repeat the same action when unnecessary.

Reminder:
1. The action must be chosen from the given available actions. Any actions except provided available actions will be regarded as illegal.
2. Think when necessary, try to act directly more in the process.

---
Here is an example.
You should perform actions to accomplish the goal: Add a white desk to my wish list

Observation:
WINDOWED PAGE:{
Tab 0 (current): One Stop Market
[1] RootWebArea 'One Stop Market' focused: True
[1254] link 'My Wish List'
[2427] StaticText 'Search'
[1585] combobox 'Search' autocomplete: both hasPopup: listbox required: False expanded: False
[2430] link 'Advanced Search'
[1588] button 'Search' disabled: True
}
URL: http://onestopmarket.com

Action: @type [1585] [white desk] [press_enter_after=1]@

Observation:
WINDOWED PAGE:{
Tab 0 (current): Search results for: 'white desk'
[2635] RootWebArea "Search results for: 'white desk'" focused: True
[3869] link 'My Wish List'
[4827] StaticText 'Search'
[4072] combobox 'Search' autocomplete: both hasPopup: listbox required: False expanded: False
[5027] StaticText 'white desk'
[4830] link 'Advanced Search'
[4075] button 'Search' disabled: True
[3729] main "
[3842] heading "Search results for: 'white desk'"
[3907] StaticText 'Items 1-12 of 38823'
[4781] link 'Image'
[4833] img 'Image'
[4783] link 'Image'
[4849] img 'Image'
}
URL: http://onestopmarket.com/catalogsearch/result/?q=white+desk
...
---

Now, it's your turn and here is the task.
{task}

This global plan maybe helpful for you to complete the task:
{global_plan}

Previous observation:
{observation}

Your next action:
""",

"textcraft": """
You are given a few useful crafting recipes to craft items in Minecraft. Crafting commands are of the format "craft [target object] using [input ingredients]". Every round I will give you an observation, you have to respond to an action based on the state and instruction. You can "get an object (ingredients) from the inventory or the environment, look up the game "inventory" by inventory, or "craft" (target) using any of the crafting commands. You can use ONLY these crafting commands provided, do not use your own crafting commands. However, if the crafting command uses a generic ingredient like "planks", you can use special types of the same ingredient e.g. dark oak "planks" in the command instead. For any other natural language or thoughts, use prefix 'think:'.
For each of your turn, you will be given the observation of the last turn.

---
Here is a demo of how to fetch and craft objects.
Crafting commands:
craft 3 dark oak sign using 6 dark oak planks, 1 stick
craft 4 dark oak planks using 1 dark oak log
craft 1 stick using 1 planks
craft 4 stick using 2 bamboo
craft 4 oak planks using 1 oak log
craft 1 dark oak fence using 2 stick, 4 dark oak planks
craft 1 warped stairs using 6 warped planks
craft 3 oak sign using 6 oak planks, 1 stick

Goal: craft dark oak sign
> think: I should check if I can fetch dark oak sign directly from the environment or the inventory.
OK.
> inventory
Inventory: [stick] (1) [dark oak planks] (8)
> get dark oak sign
Could not find dark oak sign
> think: I cannot get dark oak sign directly, I need to craft it. From the crafting commands, I can use: craft dark oak sign using 6 dark oak planks, 1 stick. Ingredients needed: 6 dark oak planks, 1 stick. Input assumption: I have all the necessary ingredients in my inventory. Let me verify this first.
OK.
> inventory
Inventory: [stick] (1) [dark oak planks] (8)
> think: I found my ingredients: 6 dark oak planks, 1 stick in my inventory. My assumption is true, I can proceed. I will use the crafting command: craft dark oak sign using 6 dark oak planks
OK.
> craft 1 dark oak sign using 6 dark oak planks, 1 stick
Crafted 1 minecraft:dark_oak_sign
> inventory
Inventory: [dark oak sign] (1)
> think: I now have dark oak sign in my inventory. Task Completed!
OK.
---

You can use the provided crafting commands to accomplish the goal. When you the desired item in your inventory, think: Task Completed! If you have tried your best but cannot proceed, think: task failed!
Now, it's your turn and here are the crafting commands and the goal.
{task}

This global plan maybe helpful for you to complete the task:
{global_plan}

Previous observation:
{observation}

Your next action:
""",

"maze": """
You are an expert maze solver. Your objective is to reach the goal in as few steps as possible. At each step you will be given information about where the goal is, your current position, and the walls that surround you. When you move right you increase your y position by 1, when you move down you increase your x position by 1. Your possible actions are "move up", “move down”, “move left”, “move right”. Formally, your return should be in this format:

Thought: <Your Thought>
Action: <Your Action>

The available actions are:
1. move up
2. move down
3. move left
4. move right

Reminder:
1. The action must be chosen from the given available actions. Any actions except provided available actions will be regarded as illegal.
2. Think when necessary, try to act directly more in the process.

---
Here is an example.
environment: Your current position is at position 5, 6. There is a wall above you.
action: move left
environment: Your current position is at position 5, 5. There are walls above you, below you.
action: move left
environment: Your current position is at position 5, 4. There are walls above you, below you.
action: move up
environment: Your current position is at position 5, 4. There are walls above you, below you.
action: move left
environment: Your current position is at position 5, 3. There are walls to your left, below you.
action: move down
environment: Your current position is at position 5, 3. There are walls to your left, below you.
action: move left
environment: Your current position is at position 5, 3. There are walls to your left, below you.
action: move down
environment: Your current position is at position 5, 3. There are walls to your left, below you.
action: move left
environment: Your current position is at position 5, 3. There are walls to your left, below you.
action: move right
environment: Your current position is at position 5, 4. There are walls above you, below you.
action: move down
environment: Your current position is at position 5, 4. There are walls above you, below you.
action: move right
environment: Your current position is at position 5, 5. There are walls above you, below you.
action: move right
environment: Your current position is at position 5, 6. There is a wall above you.
action: move down
environment: Your current position is at position 6, 6. There are walls to your right, to your left.
action: move down
environment: Your current position is at position 7, 6. There are walls to your right, to your left.
action: move right
environment: Your current position is at position 7, 6. There are walls to your right, to your left.
action: move down
environment: Success.
---

Now, it's your turn and here is the task.
{task}

This global plan maybe helpful for you to complete the task:
{global_plan}

Previous observation:
{observation}

Your next action:
""",
 
"wordle": """
You are an expert wordle player. Welcome to the game of Wordle. Your objective is to guess a hidden 5 letter word. You have 6 attempts to guess it correctly and you should try to guess it in as few attempts as possible. When guessing the word, you should format your word as a space separated sequence of letters, like "s h i r e" for example. After guessing the word, you will receive feedback from the game environment in the form of a sequence of 5 space separated letters like "b y g g b", where each letter indicates some information about the hidden word. The environment will return one of three letters - "b", "g", or "y" – for each letter in the word you guessed. We describe the meaning of each letter below:
"b": If the environment returns a “b”, it means that the letter at that position in your guessed word is not in the hidden word.
"y": If the environment returns a “y”, it means that the letter at that position in your guessed word is in the hidden word but is not in the correct position.
"g": If the environment returns a “g”, it means that the letter at that position in your guessed word is in the hidden word and is in the correct position.
As a note, if you guess an invalid word (e.g. not a 5 letter word or a word not in the vocabulary), the environment will respond with an “invalid word” message. In general though, you should use this information returned by the environment to update your belief about what the hidden word might be and adjust your next guess accordingly.

---
Here is the complete list of valid vocabulary words that are accepted by the game:\n```\nelect\nnymph\nsolar\npence\nglade\nulcer\nsolve\ncoupe\nheath\nchirp\nhunch\nbacon\nbaggy\ntacit\nabled\nfried\nrecut\nretry\nivory\nunity\napart\naltar\nslyly\nfudge\nswine\navian\nstole\nsniff\nblush\nbraid\nalgae\nniece\nswill\nclung\nwrist\nnoble\nnorth\nelder\npolka\nspilt\nmedic\nladen\nblade\ntacky\ntrove\ncamel\nstorm\nhello\nindex\nelbow\nidler\nknead\nchaff\ngenie\ncreak\nmamma\ngavel\ntheft\nswish\nperky\nrodeo\ncacao\nlipid\nskate\nsalty\nhedge\nhyena\nrange\nhumor\nspiny\nruddy\nprime\nbluff\nhouse\namber\nrevel\ndrink\nframe\ngaudy\ninner\nretro\nabide\nplied\ntiger\nidiot\nlunch\ndopey\ntwirl\nseven\nflung\nfella\nsmash\nfence\nflush\nfault\nalloy\ngonad\nboard\nexact\nrumba\naloft\nmince\nwryly\nmodel\nclean\nhappy\nknoll\nvigil\nsmall\nequip\nknelt\nacute\nbroom\nproof\nperil\nhatch\nsaucy\ntough\nmoral\nnoose\nother\nnomad\nboney\nlabel\ngusto\nscoff\nspill\ncrimp\nspice\nworth\nrecur\nblare\nvixen\ncedar\ntopic\ncivil\nfugue\nrhino\nspeak\nspawn\nruder\nfiber\nretch\ngrave\ncider\namong\ncheat\ntrial\npixie\nchase\ngeese\nloyal\nhunky\nquota\ncynic\ntract\nbuggy\nminim\nlogic\nimpel\nshoot\nstomp\novary\nadore\nrinse\nspear\nattic\nguard\nkneed\nannoy\nneedy\nmanly\nbully\nshirk\nprank\nshell\ncough\nspurn\ntorso\nsnort\nmoist\nscrum\nraise\nhoney\ntrope\nlocal\nerupt\nlivid\nshied\nfelon\nmecca\nshake\nreach\nstyle\ncovey\ndelve\nunset\njiffy\ncrash\nbarge\ntoast\nallot\naudio\nprint\nbadly\ntrust\nhabit\nhoard\nshard\nazure\nlucky\nblind\nhefty\nrebel\nethos\nfrown\ngodly\nvalor\nslate\naider\nstoop\nfinch\naback\nwomen\nmaker\ngully\nnasty\nprick\nwrath\nfrisk\nspell\nroyal\nlefty\nslept\npetal\nstunk\nsmack\nfluid\nclear\nlodge\nproxy\npanic\nthorn\nshock\nhotly\ngamma\ngypsy\nfarce\nkoala\nbroth\nstink\nmerit\nexcel\nangst\nslurp\ncould\ncreep\npause\nsalsa\ndandy\ntithe\noptic\natoll\nbrute\nwrung\nchurn\nnatal\nensue\nvying\nbrawl\ncloth\nsoggy\nbough\nglaze\nchock\nteary\njetty\nlight\nadobe\nleant\nbrink\nforgo\nasset\nbawdy\ntaste\ngloat\ngoing\nmorph\nswamp\nrobot\nstalk\nrajah\nultra\nliver\nfizzy\nditch\nsushi\ndusty\nsheep\nlimbo\ngroom\nbiome\ndebug\nslain\nethic\nfoist\nwound\nsloop\ngamer\npoint\npesky\ntwist\nvoter\naisle\ntally\nteeth\ntrail\nminer\ncaulk\nsynod\ntouch\nwhack\nguava\ndutch\njuicy\nyouth\nbayou\ndenim\ndisco\nblurt\nrocky\nfrost\ngooey\ndodge\nforte\nsnowy\nshrug\nrelax\ntiara\ndepth\nstuff\nwince\ncopse\nalive\ndecry\nmania\ngrant\nalter\nelegy\nicily\nblunt\nbasil\nbrush\nvoice\ntotal\nchili\nworry\nseedy\nthose\nsmoky\ncream\nroger\nloose\nshire\nallow\ngroin\nchina\npinky\ngrime\nacorn\nuncut\ndonut\npleat\nglass\nwhere\nliken\nnadir\nflume\ntwang\nsugar\nnavel\nbeing\npushy\nfocal\nhymen\nbaler\ntweet\nvideo\nskill\nsonar\naloud\nmount\nspurt\nanode\nshack\nbreak\nsatyr\nbelly\naroma\nawait\nneigh\nskull\nderby\njerky\nhumph\ninter\nsober\nicing\nsound\ntrace\nblame\nplank\naugur\nrobin\nmadly\ncheck\nmirth\ndelta\ncliff\nfacet\nevoke\nclown\novert\nfuror\nstart\nzonal\nblond\ndoing\ncello\ncreme\nmotto\n```\n\nHere is an example. If the current status of the game is given as:\n```\nguess 1: p a n i c\nfeedback 1: b b y b b\nguess 2: f e l o n\nfeedback 2: g b b y g\n```\nBased on the feedback from the environment, you know that the first letter is \"f\", the last letter is \"n\", and there is an \"o\" somewhere in the word, but it is not in the second to last position. You also know that there is not a \"p\", \"a\", \"i\", \"c\", \"e\", or \"l\" in the word. Knowing this, you might guess the next word to be:\nThought:\nI know that the first letter is \"f\", the last letter is \"n\", and there is an \"o\" somewhere in the word, but it is not in the second to last position. I also know that there is not a \"p\", \"a\", \"i\", \"c\", \"e\", or \"l\" in the word. A good word from the vocabulary to try might therefore be \"f r o w n\", since it is in the vocabulary, meets all known letter constraints, and we get to gain more information about the position of \"o\". Therefore this is a good guess to try next.\n\nAction:\nf r o w n\n\nFormally, your return should be in this format:\nThought:\n<Your Thought>\n\nAction:\n<The Word You Guess>\n\nThe guessed word is in the vocabulary, meets all known letter constraints, and we get to gain more information about the position of \"o\", so it is a good guess to try next.\n\nNow let's start a new game. Remember, the word you guess should be strictly in the vocabulary. You should return your thought and your word strictly in the formation mentioned above.
---

Now, it's your turn and here is the task.
{task}

This global plan maybe helpful for you to complete the task:
{global_plan}

Previous observation:
{observation}

Your next action:
""",
}