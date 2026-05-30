"use client";

import Link from "next/link";
import { ArrowRight, Brain, Database, Shield, Zap, FileText, Layers, CheckCircle, TrendingUp, Search, ChevronRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef, useEffect, useState } from "react";

// Floating particle component
function Particle({ x, y, delay, size }: { x: string; y: string; delay: number; size: number }) {
  return (
    <motion.div
      className="absolute rounded-full bg-blue-400/20 pointer-events-none"
      style={{ left: x, top: y, width: size, height: size }}
      animate={{
        y: [0, -30, 0],
        opacity: [0.2, 0.6, 0.2],
        scale: [1, 1.2, 1],
      }}
      transition={{
        duration: 4 + delay,
        repeat: Infinity,
        delay,
        ease: "easeInOut",
      }}
    />
  );
}

// Animated counter component
function AnimatedCounter({ value }: { value: string }) {
  return (
    <motion.span
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      {value}
    </motion.span>
  );
}

const particles = [
  { x: "10%", y: "20%", delay: 0, size: 6 },
  { x: "80%", y: "10%", delay: 1, size: 4 },
  { x: "60%", y: "70%", delay: 2, size: 8 },
  { x: "25%", y: "65%", delay: 0.5, size: 5 },
  { x: "90%", y: "50%", delay: 1.5, size: 6 },
  { x: "45%", y: "15%", delay: 2.5, size: 4 },
  { x: "70%", y: "85%", delay: 3, size: 7 },
  { x: "5%", y: "80%", delay: 0.8, size: 5 },
  { x: "50%", y: "45%", delay: 1.2, size: 3 },
  { x: "15%", y: "45%", delay: 3.5, size: 6 },
];

export default function LandingPage() {
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ["start start", "end start"] });
  const heroY = useTransform(scrollYProgress, [0, 1], ["0%", "30%"]);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);

  return (
    <div className="min-h-screen bg-[#040814] relative overflow-hidden text-white">

      {/* ── Rich Background ── */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
        {/* Deep mesh gradient */}
        <div className="absolute inset-0" style={{
          background: "radial-gradient(ellipse 80% 60% at 50% -10%, rgba(59,130,246,0.15) 0%, transparent 60%), radial-gradient(ellipse 60% 50% at 90% 80%, rgba(139,92,246,0.12) 0%, transparent 60%), radial-gradient(ellipse 50% 40% at 10% 90%, rgba(16,185,129,0.08) 0%, transparent 50%)"
        }} />
        {/* Grid overlay */}
        <div className="absolute inset-0 opacity-[0.04]" style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }} />
        {/* Floating orbs */}
        <motion.div
          animate={{ scale: [1, 1.15, 1], x: [0, 20, 0] }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-32 -left-32 w-[600px] h-[600px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(59,130,246,0.10) 0%, transparent 70%)" }}
        />
        <motion.div
          animate={{ scale: [1, 1.2, 1], x: [0, -20, 0] }}
          transition={{ duration: 22, repeat: Infinity, ease: "easeInOut", delay: 5 }}
          className="absolute -bottom-32 -right-32 w-[700px] h-[700px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(139,92,246,0.10) 0%, transparent 70%)" }}
        />
        {/* Particles */}
        {particles.map((p, i) => <Particle key={i} {...p} />)}
      </div>

      {/* ── Navbar ── */}
      <motion.nav
        initial={{ y: -24, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="fixed top-0 w-full z-50"
        style={{ background: "rgba(4,8,20,0.7)", backdropFilter: "blur(20px)", borderBottom: "1px solid rgba(255,255,255,0.06)" }}
      >
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6)" }}>
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">Bank<span className="text-blue-400">RAG</span></span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-white/50">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
            <a href="#demo" className="hover:text-white transition-colors">Demo</a>
          </div>
          <Link href="/dashboard">
            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.97 }}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white transition-all"
              style={{ background: "linear-gradient(135deg, rgba(59,130,246,0.3), rgba(139,92,246,0.3))", border: "1px solid rgba(99,179,237,0.3)" }}
            >
              Launch Dashboard <ArrowRight className="w-4 h-4" />
            </motion.button>
          </Link>
        </div>
      </motion.nav>

      {/* ── Hero ── */}
      <section ref={heroRef} className="relative z-10 pt-36 pb-20 px-6 min-h-screen flex flex-col justify-center">
        <motion.div style={{ y: heroY, opacity: heroOpacity }} className="container mx-auto text-center max-w-5xl">

          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold mb-8 tracking-widest uppercase"
            style={{ background: "rgba(59,130,246,0.12)", border: "1px solid rgba(59,130,246,0.3)", color: "#93c5fd" }}
          >
            <Sparkles className="w-3 h-3" />
            Powered by Adaptive RAG + LLM Routing
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="font-extrabold tracking-tight mb-6 leading-[1.1]"
            style={{ fontSize: "clamp(3rem, 8vw, 5.5rem)" }}
          >
            <span className="block text-white">Intelligent Banking</span>
            <span className="block" style={{ background: "linear-gradient(90deg, #60a5fa, #a78bfa, #34d399)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              Knowledge Assistant
            </span>
          </motion.h1>

          {/* Sub-headline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="text-lg md:text-xl mb-10 max-w-2xl mx-auto leading-relaxed"
            style={{ color: "rgba(255,255,255,0.5)" }}
          >
            A state-of-the-art Adaptive RAG system that understands complex banking queries, routes them intelligently, and delivers precise answers grounded in your document corpus.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex flex-col sm:flex-row justify-center items-center gap-4 mb-20"
          >
            <Link href="/dashboard">
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: "0 0 40px rgba(59,130,246,0.4)" }}
                whileTap={{ scale: 0.97 }}
                className="flex items-center gap-3 px-8 py-4 rounded-xl text-base font-semibold text-white transition-all"
                style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6)", boxShadow: "0 0 24px rgba(59,130,246,0.3)" }}
              >
                Try the Demo <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
            <a href="#features">
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="flex items-center gap-2 px-8 py-4 rounded-xl text-base font-medium text-white/70 hover:text-white transition-all"
                style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)" }}
              >
                Explore Architecture <ChevronRight className="w-4 h-4" />
              </motion.button>
            </a>
          </motion.div>

          {/* Stats Row */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.55 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
          >
            {[
              { icon: <FileText className="w-5 h-5" />, value: "50", label: "Banking Documents", color: "#60a5fa" },
              { icon: <Layers className="w-5 h-5" />, value: "102", label: "Indexed Chunks", color: "#a78bfa" },
              { icon: <Database className="w-5 h-5" />, value: "5", label: "Domain Categories", color: "#34d399" },
              { icon: <CheckCircle className="w-5 h-5" />, value: "100%", label: "OOD Detection", color: "#f59e0b" },
            ].map((s, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -4, scale: 1.02 }}
                className="p-5 rounded-2xl flex flex-col items-center gap-2 transition-all"
                style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", backdropFilter: "blur(10px)" }}
              >
                <div style={{ color: s.color }}>{s.icon}</div>
                <div className="text-3xl font-black text-white"><AnimatedCounter value={s.value} /></div>
                <div className="text-xs text-white/40 uppercase tracking-widest">{s.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="relative z-10 py-28 px-6">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <p className="text-xs font-semibold tracking-[0.3em] uppercase mb-3" style={{ color: "#60a5fa" }}>What Makes It Special</p>
            <h2 className="text-4xl md:text-5xl font-extrabold text-white">Advanced RAG Architecture</h2>
            <p className="mt-4 text-white/40 max-w-xl mx-auto">Every component is engineered to deliver precision, speed, and reliability at scale.</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                icon: <Database className="w-6 h-6" />,
                title: "Hybrid Vector + BM25 Search",
                desc: "Combines dense semantic vector embeddings with sparse BM25 keyword retrieval to maximize recall and precision simultaneously. The best of both worlds.",
                color: "#3b82f6",
                tag: "Retrieval"
              },
              {
                icon: <Brain className="w-6 h-6" />,
                title: "Intelligent Query Routing",
                desc: "Dynamically classifies queries by complexity (simple/moderate/complex) and routes them through the optimal retrieval strategy — no manual configuration needed.",
                color: "#8b5cf6",
                tag: "Routing"
              },
              {
                icon: <Zap className="w-6 h-6" />,
                title: "Self-Correcting Fallback",
                desc: "When confidence falls below threshold, the system automatically reformulates the query with LLM-driven expansion and retries with broader search scope.",
                color: "#34d399",
                tag: "Reliability"
              },
              {
                icon: <Shield className="w-6 h-6" />,
                title: "Domain Guard & OOD Detection",
                desc: "A banking-domain classifier ensures the system only answers relevant financial questions, gracefully declining out-of-scope queries to maintain professional scope.",
                color: "#f59e0b",
                tag: "Safety"
              },
              {
                icon: <Search className="w-6 h-6" />,
                title: "Cross-Encoder Reranking",
                desc: "After retrieval, a local MS-Marco Cross-Encoder model re-scores all candidate chunks for semantic relevance, ensuring only the most pertinent context reaches the LLM.",
                color: "#f87171",
                tag: "Precision"
              },
              {
                icon: <TrendingUp className="w-6 h-6" />,
                title: "Real-Time Analytics",
                desc: "Every response includes full observability: confidence scores, retrieval strategy used, latency, chunks retrieved, domain categories, and source citations.",
                color: "#38bdf8",
                tag: "Observability"
              },
            ].map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                whileHover={{ y: -6 }}
                className="group p-7 rounded-2xl transition-all duration-300 cursor-default"
                style={{
                  background: "rgba(255,255,255,0.02)",
                  border: "1px solid rgba(255,255,255,0.07)",
                  backdropFilter: "blur(10px)"
                }}
              >
                <div className="flex items-start gap-5">
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-all group-hover:scale-110"
                    style={{ background: `${f.color}18`, color: f.color, border: `1px solid ${f.color}30` }}
                  >
                    {f.icon}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-base font-bold text-white">{f.title}</h3>
                      <span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: `${f.color}18`, color: f.color }}>{f.tag}</span>
                    </div>
                    <p className="text-sm leading-relaxed" style={{ color: "rgba(255,255,255,0.45)" }}>{f.desc}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section id="architecture" className="relative z-10 py-28 px-6" style={{ background: "rgba(255,255,255,0.015)", borderTop: "1px solid rgba(255,255,255,0.05)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
        <div className="container mx-auto max-w-5xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-16"
          >
            <p className="text-xs font-semibold tracking-[0.3em] uppercase mb-3" style={{ color: "#a78bfa" }}>Under the Hood</p>
            <h2 className="text-4xl md:text-5xl font-extrabold text-white">How It Works</h2>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
            {[
              { step: "01", label: "Query\nInput", color: "#3b82f6" },
              { step: "→", label: "", color: "transparent", isArrow: true },
              { step: "02", label: "Route &\nDecompose", color: "#8b5cf6" },
              { step: "→", label: "", color: "transparent", isArrow: true },
              { step: "03", label: "Hybrid\nRetrieval", color: "#34d399" },
            ].map((s, i) =>
              s.isArrow ? (
                <motion.div key={i} initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: i * 0.15 }}
                  className="text-white/20 text-3xl font-thin hidden md:block text-center">→</motion.div>
              ) : (
                <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.15 }}
                  className="p-6 rounded-2xl"
                  style={{ background: `${s.color}12`, border: `1px solid ${s.color}25` }}>
                  <div className="text-3xl font-black mb-2" style={{ color: s.color }}>{s.step}</div>
                  <div className="text-sm font-medium text-white/70 whitespace-pre-line">{s.label}</div>
                </motion.div>
              )
            )}
          </div>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
            {[
              { step: "06", label: "Stream\nResponse", color: "#f59e0b" },
              { step: "←", label: "", color: "transparent", isArrow: true },
              { step: "05", label: "Generate\nAnswer", color: "#f87171" },
              { step: "←", label: "", color: "transparent", isArrow: true },
              { step: "04", label: "Rerank &\nCompress", color: "#38bdf8" },
            ].map((s, i) =>
              s.isArrow ? (
                <motion.div key={i} initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: i * 0.15 }}
                  className="text-white/20 text-3xl font-thin hidden md:block text-center">←</motion.div>
              ) : (
                <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.15 }}
                  className="p-6 rounded-2xl"
                  style={{ background: `${s.color}12`, border: `1px solid ${s.color}25` }}>
                  <div className="text-3xl font-black mb-2" style={{ color: s.color }}>{s.step}</div>
                  <div className="text-sm font-medium text-white/70 whitespace-pre-line">{s.label}</div>
                </motion.div>
              )
            )}
          </div>
        </div>
      </section>

      {/* ── Sample Queries ── */}
      <section id="demo" className="relative z-10 py-28 px-6">
        <div className="container mx-auto max-w-5xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-14"
          >
            <p className="text-xs font-semibold tracking-[0.3em] uppercase mb-3" style={{ color: "#34d399" }}>Real Banking Scenarios</p>
            <h2 className="text-4xl md:text-5xl font-extrabold text-white">Test It Live</h2>
            <p className="mt-4 text-white/40">Try these exact queries on the live dashboard to see the system in action.</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 text-left">
            {[
              { type: "Factual", query: "What is the current Repo Rate set by the RBI?", color: "#60a5fa", icon: "📊" },
              { type: "Comparison", query: "How does NEFT differ from RTGS in settlement?", color: "#a78bfa", icon: "⚖️" },
              { type: "Multi-Part", query: "Explain CRR and how it impacts bank lending.", color: "#34d399", icon: "🔗" },
            ].map((q, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                whileHover={{ y: -6, scale: 1.02 }}
                className="p-6 rounded-2xl transition-all cursor-default"
                style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)" }}
              >
                <div className="text-2xl mb-3">{q.icon}</div>
                <div className="text-xs font-bold uppercase tracking-widest mb-3 px-2 py-1 rounded-full inline-block" style={{ background: `${q.color}18`, color: q.color }}>
                  {q.type} Query
                </div>
                <p className="text-sm text-white/70 leading-relaxed italic">"{q.query}"</p>
              </motion.div>
            ))}
          </div>

          {/* Big CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mt-16"
          >
            <Link href="/dashboard">
              <motion.button
                whileHover={{ scale: 1.06, boxShadow: "0 0 60px rgba(59,130,246,0.5)" }}
                whileTap={{ scale: 0.97 }}
                className="inline-flex items-center gap-3 px-10 py-5 rounded-2xl text-lg font-bold text-white transition-all"
                style={{ background: "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #34d399 100%)", boxShadow: "0 0 30px rgba(59,130,246,0.3)" }}
              >
                <Sparkles className="w-5 h-5" />
                Launch BankRAG Dashboard
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative z-10 py-10 px-6" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6)" }}>
              <Brain className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold text-sm">Bank<span className="text-blue-400">RAG</span></span>
          </div>
          <p className="text-xs" style={{ color: "rgba(255,255,255,0.3)" }}>
            Built with Next.js 15, FastAPI, ChromaDB, Groq & FastEmbed
          </p>
          <div className="flex items-center gap-2 text-xs" style={{ color: "rgba(255,255,255,0.3)" }}>
            <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            All Systems Operational
          </div>
        </div>
      </footer>
    </div>
  );
}
