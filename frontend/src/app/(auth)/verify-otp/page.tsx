"use client";

import React, { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Stethoscope, ShieldCheck, ArrowLeft, RefreshCw, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { OTPInput } from "@/features/auth/components/OTPInput";
import { apiClient } from "@/lib/api-client";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { User } from "@/types";

function VerifyOTPContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { loginWithTokens } = useAuth();

  const identifier = searchParams.get("identifier") || "";
  const purpose = searchParams.get("purpose") || "registration";
  const nameParam = searchParams.get("name") || "";

  const [otp, setOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [timer, setTimer] = useState(60);

  useEffect(() => {
    if (!identifier) {
      router.push("/login");
      return;
    }

    const interval = setInterval(() => {
      setTimer((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(interval);
  }, [identifier, router]);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;

    if (otp.length !== 6) {
      setError("Please enter the complete 6-digit verification code.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const response = await apiClient.post("/auth/verify-otp", {
      identifier,
      otp,
      purpose,
    });

    setIsLoading(false);

    if (response.success && response.data) {
      const data: any = response.data;
      const initialUser: User = {
        id: data.user_id,
        email: identifier.includes("@") ? identifier : undefined,
        phone: !identifier.includes("@") ? identifier : undefined,
        role: data.role,
        status: "active",
        email_verified: identifier.includes("@"),
        phone_verified: !identifier.includes("@"),
        full_name: data.full_name || (nameParam ? decodeURIComponent(nameParam) : undefined),
      };

      await loginWithTokens(data.access_token, data.refresh_token, initialUser);

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
      const primaryError = response.errors?.[0];
      const errorCode = primaryError?.code;
      const errorMsg = primaryError?.message;

      if (errorCode === "OTP_EXPIRED") {
        setError("Your OTP has expired. Please request a new OTP.");
      } else if (errorCode === "OTP_MAX_ATTEMPTS") {
        setError("Too many attempts. Please wait before trying again.");
      } else if (errorCode === "NETWORK_ERROR" || errorCode === "TIMEOUT_ERROR") {
        setError(errorMsg || "Unable to connect to DoctorIn. Please try again.");
      } else {
        setError(errorMsg || "Incorrect verification code. Please try again.");
      }
    }
  };

  const handleResendOTP = async () => {
    if (timer > 0 || isLoading) return;
    setError(null);
    const response = await apiClient.post("/auth/send-otp", {
      identifier,
      purpose,
    });
    if (response.success) {
      setTimer(60);
      setOtp("");
    } else {
      const primaryError = response.errors?.[0];
      setError(primaryError?.message || "Failed to resend verification code.");
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        {/* DoctorIn Branding */}
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <Stethoscope className="w-5 h-5" />
            </div>
            <span className="text-2xl font-black text-slate-900 tracking-tight">
              Doctor<span className="text-blue-600">In</span>
            </span>
          </Link>
        </div>

        {/* OTP Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 mx-auto rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h1 className="text-xl font-extrabold text-slate-900">Verify your account</h1>
            <p className="text-xs text-slate-500 leading-relaxed">
              We&apos;ve sent a 6-digit verification code to<br />
              <strong className="text-slate-800">{identifier}</strong>
            </p>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleVerify} className="space-y-6">
            <OTPInput value={otp} onChange={setOtp} disabled={isLoading} />

            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold"
              isLoading={isLoading}
              disabled={otp.length !== 6}
            >
              Verify <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </form>

          <div className="flex items-center justify-between text-xs text-slate-500 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => router.back()}
              className="flex items-center gap-1 hover:text-slate-800 font-medium transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Change email/mobile
            </button>

            <button
              type="button"
              disabled={timer > 0}
              onClick={handleResendOTP}
              className={`flex items-center gap-1 font-semibold transition-colors ${
                timer > 0 ? "text-slate-400 cursor-not-allowed" : "text-blue-600 hover:underline"
              }`}
            >
              <RefreshCw className="w-3.5 h-3.5" />
              {timer > 0 ? `Resend in ${timer}s` : "Resend OTP"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function VerifyOTPPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-sm text-slate-500">Loading...</div>}>
      <VerifyOTPContent />
    </Suspense>
  );
}
