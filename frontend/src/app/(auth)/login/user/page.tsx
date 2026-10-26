"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, Lock, User, ArrowRight, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { APP_NAME } from "@/lib/constants";
import { useAuth } from "@/features/auth/hooks/useAuth";

export default function UserLoginPage() {
  const [authMode, setAuthMode] = useState<"password" | "otp">("password");
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { loginWithTokens } = useAuth();

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim() || !password) {
      setError("Please fill in both Email/Mobile and Password.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const response = await apiClient.post("/auth/login", {
      identifier: identifier.trim(),
      password,
    });

    setIsLoading(false);

    if (response.success && response.data) {
      const data: any = response.data;
      if (data.access_token) {
        await loginWithTokens(data.access_token, data.refresh_token, {
          id: data.user_id,
          email: identifier.includes("@") ? identifier : undefined,
          phone: !identifier.includes("@") ? identifier : undefined,
          role: data.role,
          status: "active",
          email_verified: identifier.includes("@"),
          phone_verified: !identifier.includes("@"),
          full_name: data.full_name || undefined,
        });
      } else {
        router.push(`/verify-otp?identifier=${encodeURIComponent(identifier.trim())}&purpose=login`);
        return;
      }

      if (data.role === "admin") {
        router.push("/admin");
      } else if (data.role === "doctor") {
        if (data.verification_status === "verified") {
          router.push("/feed");
        } else if (data.verification_status === "suspended") {
          router.push("/verification/restricted");
        } else {
          router.push("/verification");
        }
      } else {
        router.push("/feed");
      }
    } else {
      setError(response.errors?.[0]?.message || "Invalid email/phone or password.");
    }
  };

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim()) {
      setError("Please enter your email or mobile number.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const response = await apiClient.post("/auth/send-otp", {
      identifier: identifier.trim(),
      purpose: "login",
    });

    setIsLoading(false);

    if (response.success) {
      router.push(`/verify-otp?identifier=${encodeURIComponent(identifier.trim())}&purpose=login`);
    } else {
      setError(response.errors?.[0]?.message || "Failed to dispatch verification code.");
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12 bg-slate-50">
      <div className="w-full max-w-md bg-white rounded-3xl p-8 border border-slate-200 shadow-xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-sky-600 flex items-center justify-center text-white shadow-md">
            <User className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900">Login as User</h2>
          <p className="text-xs text-slate-500">Discover doctors, search specializations, and read medical articles</p>
        </div>

        {/* Tab Toggle */}
        <div className="flex bg-slate-100 p-1 rounded-xl text-xs font-semibold text-slate-600">
          <button
            type="button"
            onClick={() => { setAuthMode("password"); setError(null); }}
            className={`flex-1 py-2 rounded-lg transition-all ${
              authMode === "password" ? "bg-white text-sky-700 shadow-sm" : "hover:text-slate-900"
            }`}
          >
            Password + OTP
          </button>
          <button
            type="button"
            onClick={() => { setAuthMode("otp"); setError(null); }}
            className={`flex-1 py-2 rounded-lg transition-all ${
              authMode === "otp" ? "bg-white text-sky-700 shadow-sm" : "hover:text-slate-900"
            }`}
          >
            Direct OTP
          </button>
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-medium">
            {error}
          </div>
        )}

        {authMode === "password" ? (
          <form onSubmit={handlePasswordLogin} className="space-y-4">
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
                  placeholder="user@example.com or +91 98765 43210"
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition-all"
                />
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition-all"
                />
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <Button type="submit" variant="primary" size="md" className="w-full bg-sky-600 hover:bg-sky-700" isLoading={isLoading}>
              Continue to OTP Verification <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </form>
        ) : (
          <form onSubmit={handleSendOTP} className="space-y-4">
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
                  className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition-all"
                />
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <Button type="submit" variant="primary" size="md" className="w-full bg-sky-600 hover:bg-sky-700" isLoading={isLoading}>
              Send OTP Code <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </form>
        )}

        <div className="pt-4 border-t border-slate-100 text-center space-y-2 text-xs text-slate-500">
          <p>
            New user?{" "}
            <Link href="/register?role=user" className="font-bold text-sky-600 hover:underline">
              Create User Account
            </Link>
          </p>
          <p>
            Are you a doctor?{" "}
            <Link href="/login/doctor" className="font-bold text-teal-600 hover:underline">
              Login as Doctor
            </Link>
          </p>
          <div className="flex items-center justify-center gap-1 text-[11px] text-slate-400 pt-1">
            <ShieldCheck className="w-3.5 h-3.5 text-sky-500" />
            <span>Secure {APP_NAME} user session</span>
          </div>
        </div>
      </div>
    </div>
  );
}
