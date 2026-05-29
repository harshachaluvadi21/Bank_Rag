"use client";

import { useEffect, useState } from "react";
import { getHealthStatus } from "@/lib/api";
import { HealthResponse } from "@/types";
import { Server, Database, BrainCircuit, CheckCircle2, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";

export const StatusWidget = () => {
  const [status, setStatus] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await getHealthStatus();
        setStatus(data);
        setError(false);
      } catch (err) {
        console.error("Failed to fetch health status", err);
        setError(true);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const StatusItem = ({ label, isReady, icon: Icon }: { label: string; isReady: boolean; icon: any }) => (
    <div className="flex items-center justify-between p-2 rounded-md bg-secondary/30 border border-white/5">
      <div className="flex items-center gap-2">
        <Icon className="w-4 h-4 text-primary" />
        <span className="text-sm font-medium">{label}</span>
      </div>
      {isReady ? (
        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
      ) : (
        <XCircle className="w-4 h-4 text-red-400" />
      )}
    </div>
  );

  if (error) {
    return (
      <Card className="glass w-full border-red-500/30 bg-red-500/5">
        <CardContent className="p-4 flex items-center justify-center text-sm text-red-400">
          Backend Offline
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="glass w-full">
        <CardHeader className="p-4 pb-2">
          <CardTitle className="text-sm flex items-center gap-2 text-foreground/80">
            <Server className="w-4 h-4" /> System Status
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 pt-2 space-y-2">
          <StatusItem label="Backend API" isReady={status?.status === "ok"} icon={Server} />
          <StatusItem label="Vector DB" isReady={status?.vector_db === "connected"} icon={Database} />
          <StatusItem label="BM25 Search" isReady={status?.bm25 === "loaded"} icon={Database} />
          <StatusItem label="LLM Engine" isReady={status?.llm === "ready"} icon={BrainCircuit} />
          {status && (
            <div className="pt-2 mt-2 border-t border-border flex justify-between text-xs text-muted-foreground">
              <span>{status.documents} Documents</span>
              <span>{status.chunks} Chunks</span>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};
