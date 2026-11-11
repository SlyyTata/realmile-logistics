"use client";

import React from 'react'; // FIXED: Explicitly import React
import Link from 'next/link';
import { Truck, ArrowRight, ShieldCheck, Zap, Package } from 'lucide-react';
import { motion } from 'framer-motion';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-12 py-8 bg-white/50 backdrop-blur-md sticky top-0 z-50 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="bg-primary p-2 rounded-lg shadow-[0_0_15px_rgba(250,204,21,0.5)]">
            <Truck className="h-6 w-6 text-black" />
          </div>
          <span className="text-2xl font-black tracking-tighter">REALMILE</span>
        </div>
        <Link href="/login">
          <button className="font-black text-[10px] uppercase tracking-[0.2em] px-6 py-3 bg-slate-50 rounded-full hover:bg-primary hover:text-black transition-all duration-300">
            Staff Portal
          </button>
        </Link>
      </nav>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center px-4 pt-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-primary/10 text-primary-dark text-[10px] font-black px-5 py-2.5 rounded-full mb-8 tracking-[0.3em] uppercase border border-primary/20 shadow-sm"
        >
          Premium Last-Mile Solutions
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-8xl font-black tracking-tighter text-slate-900 max-w-5xl leading-[0.8] mb-10"
        >
          The <span className="text-primary italic drop-shadow-sm">Gold Standard</span> of <br />
          logistics management.
        </motion.h1>

        <p className="text-slate-400 max-w-xl font-bold text-lg leading-relaxed">
          Consolidate Speedaf, GIG, and Sharp franchise data into one <br />
          high-performance command center.
        </p>

        <div className="mt-14 flex flex-col sm:flex-row gap-6">
          <Link href="/login">
            <button className="bg-brand-black text-white px-12 py-6 rounded-2xl font-black text-lg flex items-center gap-3 hover:bg-black transition-all shadow-[0_20px_50px_rgba(0,0,0,0.2)] hover:scale-105 active:scale-95 group">
              Start Building <ArrowRight size={22} className="text-primary group-hover:translate-x-1 transition-transform" />
            </button>
          </Link>
          <Link href="/login">
            <button className="bg-white border-2 border-slate-100 px-12 py-6 rounded-2xl font-black text-lg hover:bg-slate-50 transition-all hover:border-primary/50">
              Operations Login
            </button>
          </Link>
        </div>
      </section>

      {/* Feature Badges */}
      <div className="mt-40 grid md:grid-cols-3 gap-12 px-12 pb-32">
        <FeatureCard
          icon={<Zap />}
          title="Auto-Scan"
          desc="Automatic partner detection and data fetching from Speedaf and GIG."
        />
        <FeatureCard
          icon={<ShieldCheck />}
          title="SLA Guard"
          desc="Real-time monitoring of 5-day delivery and return deadlines."
        />
        <FeatureCard
          icon={<Package />}
          title="Full Audit"
          desc="Every scan and status change is logged in a permanent tracking history."
        />
      </div>
    </div>
  );
}

// Sub-component for features
function FeatureCard({ icon, title, desc }: { icon: React.ReactElement<any>, title: string, desc: string }) {
  return (
    <motion.div
      whileHover={{ y: -10 }}
      className="p-12 rounded-4xl bg-slate-50/50 border border-slate-100 hover:border-primary/20 hover:bg-white hover:shadow-2xl transition-all duration-500 group"
    >
      <div className="mb-6 p-4 bg-white rounded-2xl w-fit shadow-sm group-hover:bg-primary transition-colors">
        {/* FIXED: Using React.cloneElement correctly now that React is imported */}
        {React.cloneElement(icon, {
          size: 24,
          className: "text-primary group-hover:text-black transition-colors"
        })}
      </div>
      <h3 className="text-2xl font-black mb-3 tracking-tight">{title}</h3>
      <p className="text-slate-500 text-sm font-bold leading-relaxed opacity-70">{desc}</p>
    </motion.div>
  )
}