# Google & Kaggle Gen AI Intensive — Full Summary (Day 1–5)

## Overview

This document summarises **all five days** of the Kaggle + Google Gen AI Intensive Course. It includes:

* Key concepts
* Important code patterns
* Functions, APIs, and workflows used
* How each day builds toward the final Capstone

---

# **Day 1 — Prompting Foundations**

Day 1 introduces how LLMs work, how prompting affects outputs, and how to structure high‑quality prompts.

## **Core Concepts**

### **1. Prompt Structure**

* **Instruction** — what the model should do
* **Context** — background or reference info
* **Input data** — what the model needs to process
* **Output format** — structure the model must follow

### **2. Prompting Techniques**

* Zero‑shot
* One‑shot & few‑shot
* Chain‑of‑thought
* Deliberate prompting
* Role prompting ("You are a helpful assistant…")

## **3. Example Prompt Templates**

### **Classification Template**

```text
You are a text classifier. Classify the input into one of the following classes: {labels}.
Input: {text}
Return ONLY the label.
```

### **Extraction Template**

```text
Extract the following fields from the text:
- Name
- Date
- Entities
Return as valid JSON.
```

### **Reasoning Template**

```text
Think step-by-step and clearly explain your reasoning before giving the answer.
```

---

# **Day 2 — Embeddings, Similarity, and RAG**

Day 2 introduces vector embeddings, similarity search, and how to build Retrieval-Augmented Generation systems.

## **A. Embeddings (Text → Vector)**

### **Key Function** (Gemini API)

```python
model = genai.GenerativeModel("text-embedding-004")
emb = model.embed_content("Hello world")
```

Outputs a high‑dimensional vector (~768–3072 dims).

## **B. Similarity Search**

### **Cosine Similarity**

```python
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

Used to compare meaning between texts.

## **C. Embeddings Classifier (Keras)**

You take embeddings → feed them into a ML classifier.

Steps:

1. Generate embeddings
2. Train a neural network
3. Predict using similarity in vector space

## **D. RAG (Retrieval-Augmented Generation)**

RAG pipeline:

1. **Embed documents**
2. **Store in a vector index** (FAISS)
3. On query → embed query
4. Retrieve top‑k relevant chunks
5. Pass retrieved context + question into LLM

### **Basic RAG Code**

```python
retriever = vector_store.as_retriever()
context = retriever.invoke("How do I make tea?")
response = model.generate_content(f"Answer using context: {context}")
```

---

# **Day 3 — Function Calling & Agents with Gemini API**

Day 3 teaches structured tool calling, LangChain, and how to make the LLM execute functions.

## **A. Function Calling Schema**

```python
add_tool = {
   "name": "add_to_order",
   "description": "Add a drink to the order",
   "parameters": {
       "type": "object",
       "properties": {
           "drink": {"type": "string"},
           "modifiers": {"type": "string"}
       },
       "required": ["drink"]
   }
}
```

## **B. Using the Tool in Gemini**

```python
model = genai.GenerativeModel(
    "gemini-1.5-pro",
    tools=[add_tool]
)
resp = model.generate_content("I want a latte with oat milk")
```

Gemini produces:

```json
{
  "tool": "add_to_order",
  "arguments": {
    "drink": "latte",
    "modifiers": "oat milk"
  }
}
```

---

# **Day 4 — Fine‑Tuning a Custom Model**

This day focuses on training a smaller model on custom data.

## **A. What You Fine‑Tune**

Fine‑tuning is applied to smaller Gemini versions (e.g., **Gemma**):

* Improves performance for domain‑specific tasks
* Uses your labelled datasets

## **B. Fine‑Tuning Workflow**

### **1. Load Data**

```python
import pandas as pd
df = pd.read_csv("training_data.csv")
```

### **2. Format for Supervised Learning**

```python
train = [
  {"input_text": row.prompt, "output_text": row.response}
  for _, row in df.iterrows()
]
```

### **3. Start Fine‑Tune Job**

```python
operation = client.fine_tuning.create(
    model="gemma-2b",
    training_data=train
)
```

### **4. Deploy Model**

```python
model = genai.GenerativeModel("projects/.../locations/.../models/my-finetuned-model")
```

---

# **Day 5 — Agents, LangGraph & Capstone**

Final day teaches how to build full agents with state, tools, and multi-step workflows.
This is where **BaristaBot** is built.

## **A. Agent Structure in LangGraph**

### **State Definition**

```python
class AgentState(TypedDict):
    messages: list
    order: list
    finished: bool
```

## **B. Nodes**

### **1. Chatbot Node**

Runs the Gemini model.

```python
def chatbot(state):
    return {"messages": [model.invoke(state["messages"])]}
```

### **2. Tools Node**

Runs tool calls.

```python
async def tool_node(state):
    return {"messages": [await tool_executor(state["messages"][-1])]]
```

### **3. Human Node**

Gets user input in terminal.

```python
def human_node(state):
    print(state["messages"][-1].content)
    user = input("You: ")
    return {"messages": [HumanMessage(user)]}
```

### **4. Order Node**

Handles custom logic.

```python
def ordering(state):
    tool_call = last_message.tool_calls[0]
    if tool_call.name == "add_to_order":
        drink = tool_call.args["drink"]
        state["order"].append(drink)
```

---

## **C. Graph Assembly**

```python
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("chatbot", chatbot)
graph.add_node("tools", tool_node)
graph.add_node("human", human_node)
graph.add_node("ordering", ordering)

# Edges
graph.add_edge("chatbot", "tools")
graph.add_edge("tools", "chatbot")
graph.add_edge("chatbot", "human")
graph.add_edge("human", "chatbot")
```

## **D. Final Runtime**

Run the agent interactively:

```python
app = graph.compile()
app.invoke({"messages": ["Hello"]})
```

The agent:

* Shows menu via tool calls
* Takes orders
* Tracks state
* Confirms order
* Places order

---

# **Final Capstone Skills (All Combined)**

By the end, you can build:

* A prompt‑engineered system (Day 1)
* Using embeddings + RAG (Day 2)
* With structured tool calls (Day 3)
* Fine‑tuned for your data (Day 4)
* Wrapped into a complete agent workflow (Day 5)

---

If you want, I can also produce:

* A PDF version
* A version with diagrams
* A version with all code blocks runnable
* A polished GitHub README version
