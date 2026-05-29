"use client";

import { AnalyticsModel } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Zap, Layers, ServerCog, Target, FileText } from "lucide-react";
import { motion } from "framer-motion";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Props {
  analytics?: AnalyticsModel;
}

export const AnalyticsPanel = ({ analytics }: Props) => {
  if (!analytics) {
    return (
      <Card className="glass h-full flex items-center justify-center text-muted-foreground">
        No analytics data available yet.
      </Card>
    );
  }

  const {
    categories,
    complexity,
    confidence,
    strategy,
    latencyMs,
    subQueries,
    chunksRetrieved,
    chunksSentToLLM,
    fallbackTriggered,
    domainDetected,
    outOfDomain
  } = analytics;

  return (
    <div className="space-y-4 pb-4">
      {/* Main Stats Row */}
      <div className="grid grid-cols-2 gap-2">
        <Card className="bg-secondary/20 border-white/5">
          <CardContent className="p-3">
            <div className="text-xs text-muted-foreground flex items-center gap-1 mb-1">
              <Target className="w-3 h-3" /> Confidence
            </div>
            <div className="text-lg font-semibold text-primary">{(confidence * 100).toFixed(1)}%</div>
          </CardContent>
        </Card>
        <Card className="bg-secondary/20 border-white/5">
          <CardContent className="p-3">
            <div className="text-xs text-muted-foreground flex items-center gap-1 mb-1">
              <Zap className="w-3 h-3" /> Latency
            </div>
            <div className="text-lg font-semibold text-primary">{latencyMs}ms</div>
          </CardContent>
        </Card>
      </div>

      {/* Details Card */}
      <Card className="bg-secondary/10 border-white/5">
        <CardHeader className="p-4 pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Activity className="w-4 h-4" /> Processing Details
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 space-y-4">
          
          <div>
            <div className="text-xs text-muted-foreground mb-1">Strategy</div>
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
              {strategy}
            </Badge>
          </div>

          <Separator className="bg-white/5" />

          <div>
            <div className="text-xs text-muted-foreground mb-1">Complexity</div>
            <span className="text-sm">{complexity}</span>
          </div>

          <Separator className="bg-white/5" />

          <div>
            <div className="text-xs text-muted-foreground mb-2">Detected Categories</div>
            <div className="flex flex-wrap gap-1">
              {categories.length > 0 ? categories.map((cat, i) => (
                <Badge key={i} variant="secondary" className="bg-white/10 text-xs font-normal">
                  {cat}
                </Badge>
              )) : <span className="text-sm italic text-muted-foreground">None</span>}
            </div>
          </div>

        </CardContent>
      </Card>

      {/* SubQueries & Chunks */}
      <Card className="bg-secondary/10 border-white/5">
        <CardHeader className="p-4 pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Layers className="w-4 h-4" /> Decomposition
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 space-y-4">
          <div>
            <div className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
              <FileText className="w-4 h-4 text-primary" /> Chunks Retrieved ({chunksRetrieved}) {"->"} LLM ({chunksSentToLLM})
            </div>
          </div>

          {subQueries && subQueries.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs text-muted-foreground">Generated Sub-Queries</div>
              {subQueries.map((sq, i) => (
                <div key={i} className="text-xs p-2 rounded bg-black/20 border border-white/5 text-muted-foreground">
                  <span className="text-foreground">{sq.text}</span>
                  <div className="flex items-center justify-between mt-1 pt-1 border-t border-white/5">
                    <span className="text-[10px] text-primary/70">{sq.category}</span>
                    <span className="text-[10px]">Conf: {(sq.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Flags */}
      <div className="flex flex-wrap gap-2">
        {fallbackTriggered && <Badge variant="destructive" className="text-[10px]">Fallback Triggered</Badge>}
        {outOfDomain && <Badge variant="destructive" className="text-[10px]">Out of Domain</Badge>}
        {domainDetected && !outOfDomain && <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-500/30 text-[10px]">Domain Match</Badge>}
      </div>

    </div>
  );
};
