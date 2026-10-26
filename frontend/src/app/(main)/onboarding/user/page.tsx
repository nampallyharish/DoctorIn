"use client";

import React from "react";
import Link from "next/link";
import { UserCheck, Search, Stethoscope, ArrowRight, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function UserOnboardingPage() {
  return (
    <div className="min-h-[80vh] bg-white flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg bg-white border border-slate-200 rounded-2xl p-8 shadow-xs text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto">
          <UserCheck className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
            <ShieldCheck className="w-3 h-3" /> Account Verified
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Welcome to DoctorIn!
          </h1>
          <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
            Your user account is now active. You can explore verified medical professionals, search by specialization or hospital, and view professional posts.
          </p>
        </div>

        <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/doctors" className="flex-1">
            <Button variant="primary" size="md" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold">
              <Search className="w-4 h-4 mr-1.5" /> Find Doctors
            </Button>
          </Link>
          <Link href="/feed" className="flex-1">
            <Button variant="outline" size="md" className="w-full font-semibold">
              Explore Medical Feed <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
