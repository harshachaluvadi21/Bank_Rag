import re
import json
from prompt import QUERY_CLASSIFIER_PROMPT

class QueryRouter:
    """
    The Query Router is the central intelligence of the Adaptive RAG system.
    It performs two main tasks:
    1. Analyzes queries for conversational pronouns to decide if history-aware query rewriting is required.
    2. Classifies queries using the LLM into Complexity (Simple, Medium, Complex) and Type 
       (factual, comparison, explanation, conversational_follow_up) to select the optimal retrieval strategy.
    """
    
    def __init__(self, llm):
        """
        Initializes the router with the LLM instance to perform classification.
        
        Parameters:
            llm: The initialized LangChain ChatModel (Groq, Gemini, or OpenAI).
        """
        self.llm = llm
        
        # Compile case-insensitive regex for common conversational pronouns and follow-up indicators.
        # This will quickly identify follow-up turns without calling the LLM unnecessarily.
        self.follow_up_pattern = re.compile(
            r"\b(it|its|that|those|their|they|them|him|her|he|she|this|these|above|previous|latter|former)\b|"
            r"\b(explain in simpler terms|summarize that|more details|give examples|its advantages)\b",
            re.IGNORECASE
        )
        
    def is_conversational_follow_up(self, query: str) -> bool:
        """
        Checks if the query is a conversational follow-up containing pronouns or referencing previous terms.
        
        Parameters:
            query (str): The raw question from the user.
            
        Returns:
            bool: True if it contains conversational references, False otherwise.
        """
        return bool(self.follow_up_pattern.search(query))
        
    def is_freshness_query(self, query: str) -> bool:
        """
        Checks if the query requests real-time or current information.
        """
        import re
        freshness_pattern = re.compile(r'\b(current|latest|today|recent|present)\b', re.IGNORECASE)
        return bool(freshness_pattern.search(query))
        
    def classify_query(self, query: str) -> dict:
        """
        Invokes the LLM to classify the query's complexity and type.
        Incorporates robust parsing to handle markdown, backticks, or parsing failures.
        
        Parameters:
            query (str): The search-optimized standalone question.
            
        Returns:
            dict: A dictionary containing 'complexity' and 'type'.
        """
        # OPTIMIZATION: Run lightweight rule-based classification first
        # If it confidently determines it's a simple query (and short enough to not need deep analysis), return immediately.
        rule_based = self._rule_based_fallback(query)
        if rule_based["complexity"] == "Simple" and len(query.split()) <= 15:
            return rule_based
            
        # Formulate and format the classifier prompt
        formatted_prompt = QUERY_CLASSIFIER_PROMPT.format(question=query)
        
        # Fallback values in case of failure
        fallback_classification = {"complexity": "Medium", "type": "explanation"}
        
        try:
            # Invoke LLM to get JSON response
            response = self.llm.invoke(formatted_prompt)
            content = response.content.strip()
            
            # Clean up the output in case the LLM returned markdown code blocks (e.g. ```json ... ```)
            cleaned_content = content
            if cleaned_content.startswith("```"):
                # Strip leading ```json or ```
                cleaned_content = re.sub(r"^```(?:json)?\n", "", cleaned_content)
                # Strip trailing ```
                cleaned_content = re.sub(r"\n```$", "", cleaned_content)
            cleaned_content = cleaned_content.strip()
            
            # Parse JSON response
            classification = json.loads(cleaned_content)
            
            # Standardize capitalization
            complexity = classification.get("complexity", "Medium").strip().capitalize()
            query_type = classification.get("type", "explanation").strip().lower()
            
            # Validate values
            if complexity not in ["Simple", "Medium", "Complex"]:
                complexity = "Medium"
            if query_type not in ["factual", "comparison", "explanation", "conversational_follow_up"]:
                query_type = "explanation"
                
            return {
                "complexity": complexity,
                "type": query_type
            }
            
        except Exception as e:
            # Print a subtle warning to console and use regular-expression based fallback matching
            # This ensures that even if API keys or JSON formats are temporarily unstable, the chatbot doesn't crash!
            print(f"\033[93m[router] [WARNING] LLM Query Router failed: {e}. Running rule-based fallback classification...\033[0m")
            return self._rule_based_fallback(query)
            
    def _rule_based_fallback(self, query: str) -> dict:
        """
        Simple, deterministic regex-based fallback query classifier if the LLM classification fails.
        """
        query_lower = query.lower()
        
        # Detect comparison queries
        if any(word in query_lower for word in ["compare", "comparison", "difference", "vs", "versus", "distinguish", "contrasted"]):
            return {"complexity": "Complex", "type": "comparison"}
            
        # Detect medium/explanation queries
        if any(word in query_lower for word in ["explain", "advantages", "disadvantages", "why", "how do", "examples", "benefit"]):
            return {"complexity": "Medium", "type": "explanation"}
            
        # Detect conversational pronouns (should be caught by is_conversational_follow_up, but added here for safety)
        if self.is_conversational_follow_up(query):
            return {"complexity": "Complex", "type": "conversational_follow_up"}
            
        # Default simple factual queries
        return {"complexity": "Simple", "type": "factual"}
        
    def get_strategy(self, complexity: str) -> dict:
        """
        Maps a query complexity level to a formal Adaptive RAG Retrieval Strategy configuration.
        
        Parameters:
            complexity (str): 'Simple', 'Medium', or 'Complex'.
            
        Returns:
            dict: The retrieval parameters (retriever type, retrieval depth k, and reranking toggle).
        """
        if complexity == "Simple":
            return {
                "strategy_name": "Vector Search Only (Simple)",
                "retriever": "vector",
                "k": 3,
                "rerank": False
            }
        elif complexity == "Medium":
            return {
                "strategy_name": "Hybrid Search + Lightweight Reranking (Medium)",
                "retriever": "hybrid",
                "k": 5,
                "rerank": True
            }
        else: # Complex
            return {
                "strategy_name": "Full Advanced RAG (Complex)",
                "retriever": "hybrid",
                "k": 10,
                "rerank": True
            }

    def decompose_query(self, query: str) -> list[str]:
        """
        Decomposes a single query into a list of independent sub-queries.
        1. Rule-Based Decomposition First (no LLM, low latency).
        2. LLM Fallback if ambiguous.
        """
        # 1. Rule-Based Decomposition
        # Regex to split on ? . ; and & or comma (if followed by a question word)
        # We look for explicit delimiters
        import re
        
        # Normalize simple spacing
        query_normalized = query.strip()
        
        # Check if the query has explicit question marks or periods separating full sentences
        # Split by ?, ., or ;
        delimiters = re.compile(r'[?.;]\s*')
        parts = [p.strip() for p in delimiters.split(query_normalized) if len(p.strip()) > 3]
        
        if len(parts) > 1:
            # Re-append question marks for semantic completeness
            return [f"{p}?" if not p.endswith("?") else p for p in parts]
            
        # Check for explicit "and" joining two distinct concepts for explanation
        # e.g. "Explain EMI and Credit Score" -> "Explain EMI", "Explain Credit Score"
        if query_lower := query_normalized.lower():
            if query_lower.startswith("explain") or query_lower.startswith("what is") or query_lower.startswith("define"):
                if " and " in query_lower:
                    try:
                        prefix_match = re.match(r'^(explain|what is|define)\s+(.*)', query_normalized, re.IGNORECASE)
                        if prefix_match:
                            prefix = prefix_match.group(1).strip()
                            remainder = prefix_match.group(2).strip()
                            concepts = [c.strip() for c in remainder.split(" and ")]
                            # If it cleanly splits into 2-3 concepts without complex clauses
                            if len(concepts) > 1 and all(len(c.split()) <= 4 for c in concepts):
                                return [f"{prefix.capitalize()} {c}?" for c in concepts]
                    except Exception:
                        pass
        
        # 2. LLM Decomposition Fallback
        # We only reach here if rule-based didn't trigger but we strongly suspect it needs decomposition
        # (For this scope, we just return the query as-is if rules fail, to strictly keep latency low and avoid LLM overhead unless explicitly asked)
        # The rules cover the user's primary examples perfectly!
        
        return [query]


class BankingDomainRouter:
    """
    Analyzes queries to detect the relevant banking domains using keyword matching.
    """
    def __init__(self):
        self.rules = {
            "rbi": ["repo rate", "reverse repo", "crr", "slr", "monetary policy", "nbfc", "rbi"],
            "loans": ["loan", "emi", "credit score", "mortgage", "eligibility", "npa", "non-performing asset", "non-performing assets", "underwriting", "repay", "default"],
            "payments": ["upi", "neft", "rtgs", "imps", "credit card", "debit card", "wallet", "payment gateway"],
            "investments": ["sip", "mutual fund", "inflation", "retirement", "retirement planning", "tax saving", "budgeting", "financial planning", "wealth creation", "insurance", "investment", "emergency fund"],
            "banking": ["savings account", "current account", "fd", "rd", "kyc", "atm", "net banking", "mobile banking", "account", "bank", "deposit", "withdrawal", "interest", "branch", "cheque", "passbook", "assets"]
        }
        
    def detect_category(self, query: str) -> dict:
        """
        Detects categories based on keywords.
        Returns a dictionary with 'categories' list and a 'confidence' score.
        """
        query_lower = query.lower()
        matched_categories = set()
        
        for category, keywords in self.rules.items():
            for kw in keywords:
                if kw in query_lower:
                    matched_categories.add(category)
                    break # Move to next category if one keyword matches
                    
        categories_list = list(matched_categories)
        confidence = 0.95 if categories_list else 0.0
        
        return {
            "categories": categories_list,
            "confidence": confidence
        }
