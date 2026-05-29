from langchain_core.prompts import PromptTemplate

# =========================================================================
# PROMPT 1: QUERY REWRITER PROMPT
# =========================================================================
# Converts conversational history and follow-up questions into search-optimized standalone queries.
QUERY_REWRITE_TEMPLATE = """You are an intelligent search assistant. Your task is to rewrite the user's latest follow-up question into a complete, standalone search query that can be used to search a vector database or document index.

Instructions:
1. Analyze the Conversation History and the Latest Question.
2. If the Latest Question contains pronouns (e.g., "it", "they", "its", "she", "he", "that", "those") or contextually refers to previous topics, rewrite it to be fully self-contained.
3. Keep the query concise, direct, and search-optimized (focus on keyword nouns and conceptual terms).
4. Do NOT answer the question. Only output the rewritten standalone query.
5. If the Latest Question is already a standalone question and does not need rewriting, output it exactly as-is.

Conversation History:
{chat_history}

Latest Question: {latest_question}

Standalone Search Query:"""

QUERY_REWRITE_PROMPT = PromptTemplate(
    input_variables=["chat_history", "latest_question"],
    template=QUERY_REWRITE_TEMPLATE
)


# =========================================================================
# PROMPT 2: QUERY CLASSIFIER PROMPT (Adaptive RAG Routing)
# =========================================================================
# Classifies incoming queries into complexity (Simple, Medium, Complex) and type.
QUERY_CLASSIFIER_TEMPLATE = """You are an expert query analyzer. Your task is to classify a user's question into a complexity level and a query type.

Complexity Levels:
- "Simple": Single-fact lookup, simple definition, or basic question (e.g., "What is inheritance?", "What are library timings?", "What is Article 14?").
- "Medium": Conceptual explanations, advantages/disadvantages, or descriptive answers (e.g., "Explain polymorphism with examples.", "What are advantages of Java?", "How does a vector search work?").
- "Complex": Multi-concept comparison, detailed scenarios, multi-step logical reasoning, or complex rule applications (e.g., "Compare inheritance and polymorphism with examples.", "Explain how attendance rules affect exam eligibility.").

Query Types:
- "factual": Seeking direct definitions, facts, or short rules.
- "comparison": Comparing or contrasting two or more concepts.
- "explanation": Requesting detailed step-by-step explanation, examples, or structural walk-throughs.
- "conversational_follow_up": Follow-up question containing pronouns (e.g., "its", "that", "those", "their", "he", "she", "it") or referring to previous parts of the chat.

Analyze the question carefully. Return your response ONLY as a valid JSON object with keys "complexity" and "type". Do NOT include any markdown formatting, backticks, or extra text.

Examples:
1. Question: "What is inheritance?"
   JSON Response: {{"complexity": "Simple", "type": "factual"}}

2. Question: "What are the advantages of Java?"
   JSON Response: {{"complexity": "Medium", "type": "explanation"}}

3. Question: "Compare inheritance and polymorphism with examples."
   JSON Response: {{"complexity": "Complex", "type": "comparison"}}

4. Question: "What are its advantages?"
   JSON Response: {{"complexity": "Complex", "type": "conversational_follow_up"}}

Question: "{question}"
JSON Response:"""

QUERY_CLASSIFIER_PROMPT = PromptTemplate(
    input_variables=["question"],
    template=QUERY_CLASSIFIER_TEMPLATE
)


# =========================================================================
# PROMPT 3: FACTUAL QA PROMPT (Simple Queries)
# =========================================================================
# Tailored for fast, direct, fact-focused answers with minimal elaboration.
FACTUAL_QA_TEMPLATE = """You are a highly precise and direct academic assistant.

Your goal is to answer the student's question directly, clearly, and concisely, using ONLY the facts explicitly mentioned in the Retrieved Context.

Instructions:
1. Provide a direct and concise answer (max 2-3 sentences if possible). No unnecessary preamble or conversational filler.
2. Rely strictly and ONLY on the facts explicitly mentioned in the Retrieved Context. Do NOT use external knowledge.
3. If the context does not contain the complete information to answer the question, respond EXACTLY with this sentence and absolutely nothing else:
"I could not find relevant information in the documents."

Retrieved Context (from local documents):
{context}

Student Question: {question}

Answer:"""

FACTUAL_QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=FACTUAL_QA_TEMPLATE
)


# =========================================================================
# PROMPT 4: EXPLANATION QA PROMPT (Medium Queries)
# =========================================================================
# Tailored for conceptual explanations, step-by-step reasoning, and examples.
EXPLANATION_QA_TEMPLATE = """You are a supportive and clear academic tutor.

Your goal is to provide a comprehensive, step-by-step explanation of the concept based strictly on the retrieved document context.

Instructions:
1. Break down the explanation into logical steps or bullet points.
2. Use clear, easy-to-understand examples based strictly on the retrieved context.
3. Keep the tone academic, helpful, and descriptive.
4. If the context does not contain sufficient information to explain the concept, respond EXACTLY with this sentence and absolutely nothing else:
"I could not find relevant information in the documents."

Retrieved Context (from local documents):
{context}

Student Question: {question}

Answer:"""

EXPLANATION_QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=EXPLANATION_QA_TEMPLATE
)


# =========================================================================
# PROMPT 5: COMPARISON QA PROMPT (Complex Queries)
# =========================================================================
# Tailored for multi-concept comparison, analytical reviews, or side-by-side tables.
COMPARISON_QA_TEMPLATE = """You are an analytical academic researcher.

Your goal is to compare and contrast the concepts queried by the student using strictly the retrieved document context.

Instructions:
1. Provide a highly structured response comparing the concepts.
2. When applicable, use a structured Markdown table or clear bullet points to show similarities and differences side-by-side.
3. Focus on key dimensions of comparison (e.g., definition, use case, advantages) based ONLY on the provided context.
4. If the context does not contain enough detailed information to compare the concepts, respond EXACTLY with this sentence and absolutely nothing else:
"I could not find relevant information in the documents."

Retrieved Context (from local documents):
{context}

Student Question: {question}

Answer:"""

COMPARISON_QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=COMPARISON_QA_TEMPLATE
)


# =========================================================================
# PROMPT 6: CONVERSATIONAL QA PROMPT (Follow-ups & Memory-Aware)
# =========================================================================
# Tailored for fluid, context-aware conversations using dialogue history.
CONVERSATIONAL_QA_TEMPLATE = """You are a friendly, engaging academic mentor.

Your goal is to answer the student's follow-up question while maintaining a natural, context-aware conversation, strictly based on the retrieved context and history.

Instructions:
1. Acknowledge the context of the dialogue naturally. Keep the conversation flowing smoothly.
2. Answer factually, clearly, and concisely, using ONLY the facts explicitly mentioned in the Retrieved Context.
3. Incorporate key references from the Conversation History where appropriate to keep the dialogue cohesive.
4. If the context does not contain sufficient details to answer, respond EXACTLY with this sentence and absolutely nothing else:
"I could not find relevant information in the documents."

Retrieved Context (from local documents):
{context}

Conversation History (for context):
{chat_history}

Student Question: {question}

Answer:"""

CONVERSATIONAL_QA_PROMPT = PromptTemplate(
    input_variables=["context", "chat_history", "question"],
    template=CONVERSATIONAL_QA_TEMPLATE
)


# =========================================================================
# BACKWARD COMPATIBILITY FALLBACK
# =========================================================================
ADVANCED_RAG_QA_PROMPT = CONVERSATIONAL_QA_PROMPT
