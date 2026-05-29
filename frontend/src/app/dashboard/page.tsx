"use client";

import { useState } from "react";
import Link from "next/link";
import { Brain, ArrowLeft, MessageSquare, Plus, Trash2 } from "lucide-react";
import { ChatWindow } from "@/components/ChatWindow";
import { AnalyticsPanel } from "@/components/AnalyticsPanel";
import { Citations } from "@/components/Citations";
import { StatusWidget } from "@/components/StatusWidget";
import { ChatResponse } from "@/types";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

export default function Dashboard() {
  const [latestResponse, setLatestResponse] = useState<ChatResponse | null>(null);

  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden">
      
      {/* Top Bar */}
      <header className="h-14 glass border-b border-white/5 flex items-center px-4 shrink-0 z-10">
        <Link href="/" className="flex items-center text-muted-foreground hover:text-foreground transition-colors mr-6">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back
        </Link>
        <div className="flex items-center gap-2 font-bold text-primary">
          <Brain className="w-5 h-5" /> BankRAG Dashboard
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Sidebar - Conversations & Status */}
        <div className="w-64 p-4 border-r border-white/5 hidden lg:flex flex-col gap-4 bg-secondary/5">
          <Button variant="outline" className="w-full justify-start border-primary/20 hover:bg-primary/10 text-primary">
            <Plus className="w-4 h-4 mr-2" /> New Chat
          </Button>
          
          <div className="flex-1 overflow-y-auto">
            <div className="text-xs font-semibold text-muted-foreground mb-2 px-2 uppercase tracking-wider">
              Conversations
            </div>
            <div className="space-y-1">
              <Button variant="ghost" className="w-full justify-start text-sm bg-secondary/20">
                <MessageSquare className="w-4 h-4 mr-2" />
                Current Session
              </Button>
              {/* Future conversations would map here */}
            </div>
          </div>

          <Button variant="ghost" className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-red-950/30">
            <Trash2 className="w-4 h-4 mr-2" /> Clear Chat
          </Button>

          <StatusWidget />
        </div>

        {/* Center - Chat */}
        <div className="flex-1 p-4 md:p-6 lg:p-8">
          <motion.div 
            initial={{ opacity: 0, scale: 0.98 }} 
            animate={{ opacity: 1, scale: 1 }} 
            className="h-full w-full max-w-4xl mx-auto"
          >
            <ChatWindow onUpdateAnalytics={setLatestResponse} />
          </motion.div>
        </div>

        {/* Right Sidebar - Analytics */}
        <div className="w-[320px] xl:w-[400px] border-l border-white/5 bg-secondary/5 hidden md:flex flex-col relative">
          <div className="p-4 font-semibold border-b border-white/5 shadow-sm text-sm flex items-center justify-between">
            Analytical Metadata
            {latestResponse && (
              <motion.span 
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-[10px] font-normal text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 px-2 py-1 rounded-full flex items-center gap-1"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live
              </motion.span>
            )}
          </div>
          <div className="flex-1 p-4 overflow-y-auto flex flex-col">
             <AnalyticsPanel analytics={latestResponse?.analytics} />
             {latestResponse?.citations && latestResponse.citations.length > 0 && (
               <Citations citations={latestResponse.citations} />
             )}
          </div>
        </div>

      </div>
    </div>
  );
}
