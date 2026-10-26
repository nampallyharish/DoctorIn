"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { User, Stethoscope, ArrowRight, ShieldCheck, Mail, Lock } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { UserRole } from "@/types";

export default function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim() || !fullName.trim()) {
      setError("Please fill in your name and contact details.");
      return;
    }

    if (!password || password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (password.length > 128) {
      setError("Password cannot exceed 128 characters.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const isEmail = identifier.includes("@");
    const payload = {
      role: "user",
      full_name: fullName.trim(),
      email: isEmail ? identifier.trim() : undefined,
      phone: !isEmail ? identifier.trim() : undefined,
      password: password,
    };

    const response = await apiClient.post("/auth/register", payload);
    setIsLoading(false);

    if (response.success) {
      router.push(
        `/verify-otp?identifier=${encodeURIComponent(identifier.trim())}&purpose=registration&role=user&name=${encodeURIComponent(fullName.trim())}`
      );
    } else {
      setError(response.errors?.[0]?.message || "Registration failed. Please check your details.");
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-xl space-y-8">
        {/* Branding Header */}
        <div className="text-center space-y-3">
          <Link href="/" className="inline-flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-extrabold text-lg shadow-sm">
              <Stethoscope className="w-5 h-5" />
            </div>
            <span className="text-2xl font-black text-slate-900 tracking-tight">
              Doctor<span className="text-blue-600">In</span>
            </span>
          </Link>

          <div className="space-y-1">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Create your DoctorIn account
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 font-medium">
              Connect. Discover. Verify.
            </p>
          </div>
        </div>

        {/* Registration Form */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
                User Account Setup
              </span>
              <h3 className="text-lg font-bold text-slate-900">
                Enter Account Details
              </h3>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleRegisterSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="John Doe"
                  className="w-full pl-10 pr-4 py-3 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all"
                />
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Email Address or Mobile Number
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
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Create Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  required
                  minLength={8}
                  maxLength={128}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="•••••••• (8-128 characters)"
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
              Proceed to Verification <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center pt-2 space-y-3">
          <p className="text-xs text-slate-500 font-medium">
            Already have an account?{" "}
            <Link href="/login" className="font-bold text-blue-600 hover:underline">
              Sign in
            </Link>
          </p>
          <div className="inline-flex items-center gap-1.5 text-[11px] text-slate-400 bg-slate-50 px-3 py-1 rounded-full border border-slate-200">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>NMC / SMC aligned DoctorIn medical network</span>
          </div>
        </div>
      </div>
    </div>
  );
}
