# Prompt Engineering Experiments
**AI Summer Internship 2026 — Week 1, Assignment 4**

> **How to use this file:** Each experiment below has a ready-to-run prompt, an example of the *kind* of output you should expect, and a filled-in explanation. Run each prompt yourself in **AI Workspace** (or the OpenAI Playground), replace the "Example Output" with your **actual** output and screenshot, and adjust the observations if your results differ.

---

## Experiment 1 — Role Prompting

**Idea:** Giving the AI a specific role/persona changes the tone, vocabulary, and depth of its answers — even for the exact same question.

**Prompt A (no role):**
```
Explain what an API is.
```

**Prompt B (role prompting):**
```
You are a senior software engineer mentoring a first-year intern.
Explain what an API is, using a simple real-world analogy.
```

**Example Output (Prompt B):**
> "Think of an API like a restaurant menu. You (the customer) don't need to know how the kitchen works — you just pick an item from the menu, and the waiter (the API) brings your order to the kitchen and returns the result. In software, an API lets one program 'order' data or actions from another program without needing to know its internal code."

**Observations:**
- Prompt A gave a generic, textbook-style dictionary definition.
- Prompt B produced a more relatable, example-driven, teaching-style explanation with an analogy.
- The role ("senior engineer mentoring an intern") changed both **tone** (friendlier) and **structure** (analogy-first).

**Improvement:** Adding a target audience ("...explain it to someone who has never coded before") sharpens the simplicity even further.

---

## Experiment 2 — Chain-of-Thought (CoT) Prompting

**Idea:** Asking the model to "think step-by-step" before answering improves accuracy on multi-step reasoning tasks (math, logic, planning).

**Prompt A (direct answer):**
```
A store had 120 items. It sold 35% on Monday and 20% of the remainder on
Tuesday. How many items are left?
```

**Prompt B (chain-of-thought):**
```
A store had 120 items. It sold 35% on Monday and 20% of the remainder on
Tuesday. How many items are left?

Think step-by-step, showing each calculation, before giving the final answer.
```

**Example Output (Prompt B):**
```
Step 1: Items sold Monday = 35% of 120 = 42
Step 2: Remaining after Monday = 120 - 42 = 78
Step 3: Items sold Tuesday = 20% of 78 = 15.6 ≈ 16
Step 4: Remaining after Tuesday = 78 - 16 = 62

Final Answer: 62 items left
```

**Observations:**
- Prompt A occasionally skipped steps or made small arithmetic slips when tested with harder numbers.
- Prompt B forced the model to show intermediate work, which made errors easier to catch and made the final answer more reliable.

**Improvement:** Adding "double-check your math before giving the final answer" reduces small arithmetic mistakes even further.

---

## Experiment 3 — Few-Shot Prompting

**Idea:** Giving the model 2-3 examples of the input→output pattern you want ("shots") before your real question dramatically improves consistency of format.

**Prompt:**
```
Convert the following product descriptions into a short marketing tagline.

Description: A water bottle that keeps drinks cold for 24 hours.
Tagline: "Stay cold. Stay ready. All day long."

Description: Wireless earbuds with noise cancellation and 30-hour battery.
Tagline: "Silence the noise. Amplify your day."

Description: A backpack made from 100% recycled materials.
Tagline:
```

**Example Output:**
```
"Carry the change you want to see."
```

**Observations:**
- Without the two example pairs ("zero-shot"), the model sometimes returned a full paragraph instead of a short tagline.
- With few-shot examples, the output consistently matched the expected **length, tone, and format** of the examples.

**Improvement:** Adding a 3rd, more different example (e.g., a tech gadget) helps the model generalize the pattern instead of just imitating the two examples' style too closely.

---

## Experiment 4 — Structured Output (JSON Mode)

**Idea:** Forcing the model to reply only in valid JSON makes its output directly usable by code (no manual parsing of free text).

**Prompt:**
```
Extract the name, age, and profession from this sentence, and return ONLY
valid JSON with keys "name", "age", "profession". No extra text.

Sentence: "Sarah is a 29-year-old graphic designer living in Toronto."
```

**Example Output:**
```json
{
  "name": "Sarah",
  "age": 29,
  "profession": "graphic designer"
}
```

**Observations:**
- Without the explicit "return ONLY valid JSON" instruction, the model sometimes added a sentence like "Here is the JSON:" before the object — which breaks automatic parsing with `json.loads()`.
- Using the API's dedicated **JSON mode** (`response_format={"type": "json_object"}` in the OpenAI API) is more reliable than relying on prompt wording alone, since it's enforced by the API itself.

**Improvement:** Combine JSON mode *and* a clear schema description in the prompt for maximum reliability — this is exactly the pattern used for **tool/function calling**.

---

## Experiment 5 — Prompt Optimization

**Idea:** Iteratively refining a prompt based on observed weaknesses in the output.

**Version 1 (vague):**
```
Write about AI agents.
```
*Output:* Long, unfocused, generic essay with no clear structure.

**Version 2 (added structure):**
```
Write a 200-word explanation of AI agents for a beginner audience,
using 3 bullet points to describe their key components.
```
*Output:* Better — has a clear length and bullet points, but bullets were generic.

**Version 3 (added specificity + example):**
```
Write a 200-word explanation of AI agents for a beginner audience with no
technical background. Use 3 bullet points describing: (1) how agents perceive
input, (2) how they decide what to do, (3) how they take action. End with
one real-world example (e.g., a coding assistant).
```
*Example Output:*
> "An AI agent is a program that can act on its own to complete a goal, instead of just answering a single question...
> - **Perceiving:** It reads the task and any relevant data or context.
> - **Deciding:** It reasons about the best next step, sometimes planning several steps ahead.
> - **Acting:** It uses tools — like running code or searching the web — to carry out that step.
> A real-world example is a coding assistant like Claude Code, which reads your codebase, plans a fix, edits files, and runs tests automatically."

**Observations:**
- Each iteration narrowed the *scope* (length, audience, structure) and added *specificity* (naming the exact 3 components wanted).
- The biggest single improvement came from specifying the **structure** (3 bullets with defined topics) rather than leaving organization up to the model.

**Improvement:** Final refinement — adding "avoid jargon like 'inference' or 'tokens'" would push the explanation to be even more beginner-friendly.



