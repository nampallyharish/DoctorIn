import React from "react";
import Link from "next/link";
import { Stethoscope, ShieldCheck, Heart } from "lucide-react";
import { APP_NAME, APP_TAGLINE } from "@/lib/constants";

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-50 text-slate-500 py-12 border-t border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <Stethoscope className="w-4 h-4" />
              </div>
              <span className="text-lg font-black text-slate-900">
                Doctor<span className="text-blue-600">In</span>
              </span>
            </div>
            <p className="text-xs leading-relaxed text-slate-500">
              {APP_TAGLINE}
            </p>
            <div className="flex items-center gap-1.5 text-xs text-emerald-600 font-semibold pt-1">
              <ShieldCheck className="w-4 h-4" /> Rigorous Credential Verification
            </div>
          </div>

          <div>
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
              For Users
            </h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/doctors" className="hover:text-blue-600 transition-colors">Search Doctors</Link></li>
              <li><Link href="/doctors?specialization=cardiology" className="hover:text-blue-600 transition-colors">Find Specialists</Link></li>
              <li><Link href="/hospitals" className="hover:text-blue-600 transition-colors">Hospital Directory</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
              For Doctors
            </h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/register?role=doctor" className="hover:text-blue-600 transition-colors">Create Profile</Link></li>
              <li><Link href="/verification" className="hover:text-blue-600 transition-colors">Get Verified</Link></li>
              <li><Link href="/feed" className="hover:text-blue-600 transition-colors">Medical Feed</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
              Governance & Security
            </h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/admin" className="hover:text-blue-600 transition-colors">Verification Portal</Link></li>
              <li><Link href="/privacy" className="hover:text-blue-600 transition-colors">Privacy Policy</Link></li>
              <li><Link href="/terms" className="hover:text-blue-600 transition-colors">Terms of Service</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-200 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
          <p>© {new Date().getFullYear()} {APP_NAME} Inc. All rights reserved.</p>
          <p className="flex items-center gap-1">
            Built for Healthcare Professionals with <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" />
          </p>
        </div>
      </div>
    </footer>
  );
};
