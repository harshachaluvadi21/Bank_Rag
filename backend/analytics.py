import sys
import time

# Ensure Windows console supports UTF-8 character encoding for premium box-drawing characters
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

class RAGAnalytics:
    """
    RAGAnalytics handles latency tracking and metadata monitoring for the Adaptive RAG pipeline.
    It provides a highly professional, color-coded, and detailed terminal dashboard showcasing
    every decision, retrieval statistic, and stage-by-stage latency of the execution.
    """
    
    def __init__(self):
        # Dictionary storing latencies in seconds
        self.latencies = {
            "routing": 0.0,
            "rewriting": 0.0,
            "retrieval": 0.0,
            "reranking": 0.0,
            "generation": 0.0,
            "total": 0.0
        }
        
        # State variables
        self.query_complexity = "Unknown"
        self.query_type = "Unknown"
        self.strategy_name = "Unknown"
        self.reranking_enabled = False
        self.confidence_score = 0.0
        self.retry_triggered = False
        self.chunks_retrieved = 0
        self.chunks_sent_to_llm = 0
        self.retry_count = 0
        
        # Timing start references
        self._start_times = {}

    def start_stage(self, stage_name: str):
        """Starts timing a specific stage."""
        self._start_times[stage_name] = time.perf_counter()

    def end_stage(self, stage_name: str):
        """Ends timing a specific stage and registers the duration in self.latencies."""
        if stage_name in self._start_times:
            duration = time.perf_counter() - self._start_times[stage_name]
            self.latencies[stage_name] = duration
            
    def record_metric(self, name: str, value):
        """Records a general pipeline metric."""
        if hasattr(self, name):
            setattr(self, name, value)

    def display_dashboard(self):
        """
        Renders a stunning, premium ASCII console dashboard detailing 
        every decision and performance metric. Highly engaging and informative!
        """
        # Terminal colors
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        CYAN = "\033[96m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
        
        # Determine qualitative confidence level
        conf = self.confidence_score * 100
        if conf >= 70:
            conf_color = GREEN
            conf_level = "High Confidence (Highly Relevant Documents)"
        elif conf >= 45:
            conf_color = YELLOW
            conf_level = "Medium Confidence (Weak/Partial Matches)"
        else:
            conf_color = RED
            conf_level = "Low Confidence (Irrelevant matches, triggered fallback retry!)"
            
        # Format complexity labels with specific colors
        complexity_colors = {
            "Simple": GREEN,
            "Medium": YELLOW,
            "Complex": RED
        }
        comp_color = complexity_colors.get(self.query_complexity, CYAN)
        
        # Rerank status string
        rerank_str = f"{GREEN}Enabled{RESET}" if self.reranking_enabled else f"{YELLOW}Disabled (Skipped for speed){RESET}"
        
        # Retry status string
        retry_str = f"{RED}{BOLD}YES (Attempted {self.retry_count} times){RESET}" if self.retry_triggered else f"{GREEN}No (First-pass Success){RESET}"
        
        # Sum active stage latencies as total in case total wasn't timed directly
        total_sec = self.latencies.get("total", 0.0)
        if total_sec == 0.0:
            total_sec = sum(self.latencies[s] for s in ["routing", "rewriting", "retrieval", "reranking", "generation"])
            
        print(f"\n{CYAN}{BOLD}┌────────────────────────────────────────────────────────────────────────┐")
        print(f"│                   🎯 ADAPTIVE RAG PERFORMANCE ANALYTICS                │")
        print(f"└────────────────────────────────────────────────────────────────────────┘{RESET}")
        
        # Print routing and retrieval decisions
        print(f"  {BOLD}Query Complexity:{RESET}  {comp_color}{BOLD}[{self.query_complexity}]{RESET}")
        print(f"  {BOLD}Query Type:{RESET}        {CYAN}[{self.query_type}]{RESET}")
        print(f"  {BOLD}Routing Strategy:{RESET}  {BLUE}{self.strategy_name}{RESET}")
        print(f"  {BOLD}Reranking Status:{RESET}  {rerank_str}")
        print(f"  {BOLD}Retrieval Confidence:{RESET} {conf_color}{BOLD}{conf:.1f}%{RESET} — {conf_color}{conf_level}{RESET}")
        print(f"  {BOLD}Low-Confidence Retry:{RESET} {retry_str}")
        print(f"  {BOLD}Chunks Retrieved:{RESET}  {YELLOW}{self.chunks_retrieved} candidate chunks{RESET}")
        print(f"  {BOLD}Chunks to LLM:{RESET}     {GREEN}{self.chunks_sent_to_llm} optimized chunks{RESET}")
        
        print(f"{CYAN}{BOLD}┌────────────────────────────────────────────────────────────────────────┐")
        print(f"│  ⚡ STAGE LATENCY BREAKDOWN                                             │")
        print(f"├───────────────────────────────────────┬────────────────────────────────┤{RESET}")
        
        # Helper to print rows cleanly
        def print_row(label, duration_sec):
            ms = duration_sec * 1000
            # Highlight with yellow/red if slow, green if fast
            val_color = GREEN if ms < 200 else (YELLOW if ms < 1000 else RED)
            print(f"  {BLUE}│{RESET}  {label:<35} {BLUE}│{RESET}  {val_color}{ms:>8.2f} ms{RESET}                    {BLUE}│{RESET}")
            
        print_row("Query Classification & Routing", self.latencies.get("routing", 0.0))
        print_row("Query Rewriting (Memory Search)", self.latencies.get("rewriting", 0.0))
        print_row("Document Retrieval (Dynamic)", self.latencies.get("retrieval", 0.0))
        print_row("Cross-Encoder Reranking & Compression", self.latencies.get("reranking", 0.0))
        print_row("LLM Answer Generation", self.latencies.get("generation", 0.0))
        
        print(f"{CYAN}{BOLD}├───────────────────────────────────────┼────────────────────────────────┤{RESET}")
        
        # Total latency row
        total_val_color = GREEN if total_sec < 1.0 else (YELLOW if total_sec < 2.5 else RED)
        print(f"  {BLUE}│{RESET}  {BOLD}{'TOTAL ADAPTIVE LATENCY':<35}{RESET} {BLUE}│{RESET}  {total_val_color}{BOLD}{total_sec * 1000:>8.2f} ms ({total_sec:.2f}s){RESET}             {BLUE}│{RESET}")
        
        print(f"{CYAN}{BOLD}└───────────────────────────────────────┴────────────────────────────────┘{RESET}\n")
