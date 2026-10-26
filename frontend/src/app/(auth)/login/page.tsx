"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, Lock, Stethoscope, User, ArrowRight, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { UserRole } from "@/types";

export default function LoginPage() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim() || !password) {
      setError("Please enter your email/mobile and password.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const response = await apiClient.post("/auth/login", {
      identifier: identifier.trim(),
      password,
    });

    setIsLoading(false);

    if (response.success) {
      // Password correct, OTP sent
      router.push(
        `/verify-otp?identifier=${encodeURIComponent(identifier.trim())}&purpose=login`
      );
    } else {
      setError(response.errors?.[0]?.message || "Invalid credentials. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        {/* DoctorIn Branding Header */}
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-extrabold text-lg shadow-sm">
              <Stethoscope className="w-5 h-5" />
            </div>
            <span className="text-2xl font-black text-slate-900 tracking-tight">
              Doctor<span className="text-blue-600">In</span>
            </span>
          </Link>

          <div className="space-y-1">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Welcome back</h1>
            <p className="text-xs text-slate-500 font-medium">Login to DoctorIn</p>
          </div>
        </div>

        {/* Card Container */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs space-y-6">


          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-medium">
              {error}
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Email or Mobile Number
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="user@example.com"
                  className="w-full pl-10 pr-4 py-3 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all"
                />
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-slate-700">Password</label>
                <Link href="#" className="text-[11px] font-semibold text-blue-600 hover:underline">
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-3 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all"
                />
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold"
              isLoading={isLoading}
            >
              Continue <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center pt-2 space-y-3">
          <p className="text-xs text-slate-500 font-medium">
            Don't have an account?{" "}
            <Link href="/register" className="font-bold text-blue-600 hover:underline">
              Create account
            </Link>
          </p>
          <div className="inline-flex items-center gap-1.5 text-[11px] text-slate-400 bg-slate-50 px-3 py-1 rounded-full border border-slate-200">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Secure SSL Encrypted Session</span>
          </div>
        </div>
      </div>
    </div>
  );
}
