"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
    Lock,
    Mail,
    ArrowRight,
    ShieldCheck,
    Globe,
    Loader2
} from 'lucide-react';
import api from '@/lib/api';

export default function LoginPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [formData, setFormData] = useState({
        username: '', // FastAPI OAuth2 uses 'username' field for email
        password: ''
    });

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            // FastAPI OAuth2 requires x-www-form-urlencoded
            const params = new URLSearchParams();
            params.append('username', formData.username);
            params.append('password', formData.password);

            const response = await api.post(
                '/auth/login',
                params,
                { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
            );

            localStorage.setItem('token', response.data.access_token);
            router.push('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.detail || "Authorization failed. Check credentials.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen bg-white font-sans">

            {/* LEFT SIDE: BRANDING & VISUAL */}
            <div className="relative hidden w-1/2 overflow-hidden bg-[#0f172a] lg:flex flex-col p-16 justify-between">
                {/* Background Pattern */}
                <div className="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]" />
                <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-[#facc15] rounded-full blur-[120px] opacity-10" />

                <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-8">
                        <div className="bg-[#facc15] p-2 rounded-lg">
                            <Globe className="text-black h-6 w-6" />
                        </div>
                        <span className="text-white font-black tracking-[0.3em] text-sm uppercase">Realmile Network</span>
                    </div>

                    <h1 className="text-7xl font-[1000] tracking-[ -0.04em] text-white leading-[0.9]">
                        Fleet <br />
                        <span className="text-[#facc15] italic">Intelligence.</span>
                    </h1>
                    <p className="mt-8 text-slate-400 font-bold text-lg max-w-md leading-relaxed uppercase tracking-widest opacity-60">
                        Enterprise Logistics & Last-Mile Terminal Control.
                    </p>
                </div>

                <div className="relative z-10">
                    <div className="flex gap-4 items-center bg-white/5 border border-white/10 p-6 rounded-[2rem] backdrop-blur-md">
                        <div className="h-12 w-12 rounded-full bg-[#facc15] flex items-center justify-center shadow-lg shadow-[#facc15]/20">
                            <ShieldCheck className="text-black h-6 w-6" />
                        </div>
                        <div>
                            <p className="text-white font-black text-sm uppercase tracking-wider">Secure Terminal</p>
                            <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">End-to-End Encrypted Access</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* RIGHT SIDE: LOGIN FORM */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50/50">
                <div className="w-full max-w-md space-y-10">

                    <div className="space-y-2">
                        <Badge variant="outline" className="border-slate-200 text-slate-500 font-black text-[10px] px-3 py-1 uppercase tracking-widest">
                            Authentication Required
                        </Badge>
                        <h2 className="text-5xl font-[1000] tracking-tighter text-slate-900">Login</h2>
                        <p className="text-slate-500 font-bold text-sm uppercase tracking-widest opacity-60">Enter your credentials to access the hub</p>
                    </div>

                    {error && (
                        <div className="p-4 bg-red-50 border-2 border-red-100 rounded-2xl flex items-center gap-3 text-red-700 text-xs font-black uppercase tracking-wider animate-shake">
                            <AlertTriangle className="h-4 w-4" />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleLogin} className="space-y-6">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 ml-1">Work Email</Label>
                                <div className="relative group">
                                    <Mail className="absolute left-4 top-4 h-4 w-4 text-slate-400 group-focus-within:text-[#0f172a] transition-colors" />
                                    <Input
                                        type="email"
                                        placeholder="name@realmile.com"
                                        required
                                        className="h-14 pl-12 bg-white border-2 border-slate-100 rounded-2xl focus:border-[#0f172a] transition-all font-bold"
                                        value={formData.username}
                                        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 ml-1">Access Key</Label>
                                <div className="relative group">
                                    <Lock className="absolute left-4 top-4 h-4 w-4 text-slate-400 group-focus-within:text-[#0f172a] transition-colors" />
                                    <Input
                                        type="password"
                                        placeholder="••••••••"
                                        required
                                        className="h-14 pl-12 bg-white border-2 border-slate-100 rounded-2xl focus:border-[#0f172a] transition-all font-bold"
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    />
                                </div>
                            </div>
                        </div>

                        <Button
                            type="submit"
                            disabled={loading}
                            className="w-full h-16 bg-[#0f172a] hover:bg-black text-white rounded-[1.5rem] text-sm font-black uppercase tracking-[0.2em] shadow-xl shadow-slate-200 transition-all active:scale-95 group"
                        >
                            {loading ? (
                                <Loader2 className="h-5 w-5 animate-spin" />
                            ) : (
                                <>
                                    Authorize Access
                                    <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </Button>
                    </form>

                    <p className="text-center text-[10px] font-black text-slate-400 uppercase tracking-widest pt-10">
                        Authorized Personnel Only <br />
                        <span className="opacity-40">Realmile Logistics ERP v2.0.4</span>
                    </p>
                </div>
            </div>
        </div>
    );
}

function AlertTriangle(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
            <path d="M12 9v4" />
            <path d="M12 17h.01" />
        </svg>
    )
}