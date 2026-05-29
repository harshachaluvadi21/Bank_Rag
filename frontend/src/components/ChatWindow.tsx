"use client";

import { useState, useRef, useEffect } from "react";
import { MessageModel, ChatResponse } from "@/types";
import { sendChatMessage } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  onUpdateAnalytics: (resp: ChatResponse | null) => void;
}

export const ChatWindow = ({ onUpdateAnalytics }: Props) => {
  const [messages, setMessages] = useState<MessageModel[]>([
    { role: "assistant", content: "Hello! I am BankRAG, your specialized banking assistant. How can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: MessageModel = { role: "user", content: input };
    const history = [...messages];
    
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    onUpdateAnalytics(null);

    try {
      const response = await sendChatMessage({
        query: userMessage.content,
        history: history,
        conversation_id: "demo-session-1"
      });

      const assistantMessage: MessageModel = { role: "assistant", content: response.content };
      setMessages((prev) => [...prev, assistantMessage]);
      onUpdateAnalytics(response);

    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error while processing your request." }]);
    } finally {
      setLoading(false);
    }
  };

  const suggestedPrompts = [
    "What is the Repo Rate?",
    "Compare Savings and Current accounts",
    "What does KYC stand for?",
    "Explain the home loan process"
  ];

  return (
    <div className="flex flex-col h-full bg-background/50 backdrop-blur-md rounded-2xl border border-white/10 overflow-hidden shadow-2xl">
      <div className="flex-1 overflow-y-auto p-4 scroll-smooth">
        <div className="space-y-6 pb-4">
          <AnimatePresence initial={false}>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 max-w-[85%] ${msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"}`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"
                }`}>
                  {msg.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                
                <div className={`p-4 rounded-2xl text-sm leading-relaxed overflow-x-auto ${
                  msg.role === "user" 
                    ? "bg-primary text-primary-foreground rounded-tr-none" 
                    : "glass rounded-tl-none border-white/5"
                }`}>
                  {msg.role === "user" ? (
                    msg.content
                  ) : (
                    <div className="prose prose-sm prose-invert text-foreground max-w-none prose-p:leading-relaxed prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3 max-w-[85%] mr-auto"
            >
               <div className="w-8 h-8 rounded-full bg-secondary text-secondary-foreground flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="p-4 rounded-2xl glass rounded-tl-none border-white/5 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  <span className="text-sm text-muted-foreground">Thinking...</span>
                </div>
            </motion.div>
          )}
          <div ref={scrollRef} />
        </div>
      </div>

      <div className="p-4 bg-background/80 backdrop-blur-lg border-t border-white/5 flex flex-col gap-3">
        {messages.length <= 1 && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-wrap gap-2"
          >
            {suggestedPrompts.map((p, i) => (
              <button 
                key={i} 
                onClick={() => setInput(p)}
                className="text-xs px-3 py-1.5 rounded-full bg-secondary/30 text-muted-foreground border border-white/5 hover:bg-primary/20 hover:text-primary hover:border-primary/30 transition-all text-left cursor-pointer"
              >
                {p}
              </button>
            ))}
          </motion.div>
        )}
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="relative flex items-center"
        >
          <Input 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about banking rates, policies..."
            className="w-full pr-12 bg-secondary/30 border-white/10 h-12 rounded-xl focus-visible:ring-primary/50"
            disabled={loading}
          />
          <Button 
            type="submit" 
            size="icon"
            disabled={!input.trim() || loading}
            className="absolute right-1 top-1 bottom-1 h-10 w-10 rounded-lg hover:bg-primary transition-colors"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
};
