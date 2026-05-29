"use client";

import Link from "next/link";
import { ArrowRight, Brain, Database, Shield, Zap, FileText, Layers, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Animated Gradient Background */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <motion.div 
          animate={{ scale: [1, 1.2, 1], rotate: [0, 90, 0] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute -top-[20%] -left-[10%] w-[70vw] h-[70vw] rounded-full bg-primary/5 blur-[120px]"
        />
        <motion.div 
          animate={{ scale: [1, 1.3, 1], rotate: [0, -90, 0] }}
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
          className="absolute -bottom-[20%] -right-[10%] w-[60vw] h-[60vw] rounded-full bg-purple-500/5 blur-[100px]"
        />
      </div>

      {/* Navbar */}
      <motion.nav 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="fixed top-0 w-full z-50 glass border-b border-white/5"
      >
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="font-bold text-xl flex items-center gap-2 text-primary">
            <Brain className="w-6 h-6" />
            BankRAG
          </div>
          <Link href="/dashboard">
            <Button className="bg-primary/20 text-primary hover:bg-primary/30 border border-primary/50">
              Launch Dashboard <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </motion.nav>

      {/* Hero */}
      <section className="pt-32 pb-12 px-6 relative z-10">
        <div className="container mx-auto text-center max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
              Next-Gen Adaptive RAG for Banking
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-10 leading-relaxed max-w-2xl mx-auto">
              Experience an intelligent retrieval-augmented generation system capable of dynamic query decomposition, fallback strategies, and domain-aware routing.
            </p>
            <div className="flex justify-center gap-4 mb-16">
              <Link href="/dashboard">
                <Button size="lg" className="h-14 px-8 text-lg shadow-xl shadow-primary/20">
                  Try the Demo <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Stats Section */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
          >
            <StatCard icon={<FileText />} value="50" label="Documents" />
            <StatCard icon={<Layers />} value="102" label="Chunks" />
            <StatCard icon={<Database />} value="5" label="Banking Domains" />
            <StatCard icon={<CheckCircle />} value="100%" label="OOD Detection" />
          </motion.div>
        </div>
      </section>

      {/* Features / Architecture */}
      <section className="py-20 px-6 border-t border-white/5 bg-secondary/10 relative z-10">
        <div className="container mx-auto">
          <motion.div 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold">Advanced RAG Architecture</h2>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard 
              delay={0.1}
              icon={<Database />}
              title="Vector + BM25"
              desc="Hybrid search combining semantic meaning with exact keyword matching."
            />
            <FeatureCard 
              delay={0.2}
              icon={<Brain />}
              title="Query Routing"
              desc="Dynamically routes queries based on complexity and banking domain."
            />
            <FeatureCard 
              delay={0.3}
              icon={<Zap />}
              title="Self-Correction"
              desc="Automatic fallback strategies when retrieval confidence is low."
            />
            <FeatureCard 
              delay={0.4}
              icon={<Shield />}
              title="Domain Guard"
              desc="Detects out-of-domain queries to maintain professional banking scope."
            />
          </div>
        </div>
      </section>

      {/* Example Queries */}
      <section className="py-20 px-6 relative z-10">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl font-bold mb-10"
          >
            Test with real banking scenarios
          </motion.h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
            <QueryCard 
              type="Factual Query" 
              query='"What is the current Repo Rate set by the RBI?"' 
              delay={0.1} 
            />
            <QueryCard 
              type="Comparison" 
              query='"How does NEFT differ from RTGS in terms of settlement?"' 
              delay={0.2} 
            />
            <QueryCard 
              type="Multi-part" 
              query='"Explain CRR and how it impacts bank lending capabilities."' 
              delay={0.3} 
            />
          </div>
        </div>
      </section>

      <footer className="py-8 border-t border-white/5 text-center text-muted-foreground text-sm relative z-10">
        <p>Built with Next.js 15, FastAPI, and ChromaDB.</p>
      </footer>
    </div>
  );
}

function StatCard({ icon, value, label }: any) {
  return (
    <div className="glass p-4 rounded-xl border-white/5 flex flex-col items-center justify-center">
      <div className="text-primary mb-2 opacity-80">{icon}</div>
      <div className="text-3xl font-bold text-foreground mb-1">{value}</div>
      <div className="text-xs text-muted-foreground uppercase tracking-wider">{label}</div>
    </div>
  );
}

function FeatureCard({ icon, title, desc, delay }: any) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay }}
      className="glass p-6 rounded-2xl border-white/5 hover:border-primary/30 transition-colors"
    >
      <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center text-primary mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-muted-foreground text-sm leading-relaxed">{desc}</p>
    </motion.div>
  );
}

function QueryCard({ type, query, delay }: any) {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ delay }}
      className="glass p-6 rounded-xl border-white/5 hover:bg-secondary/20 transition-colors"
    >
      <div className="text-sm text-primary mb-2 font-medium">{type}</div>
      <p className="text-sm text-foreground/90">{query}</p>
    </motion.div>
  );
}
