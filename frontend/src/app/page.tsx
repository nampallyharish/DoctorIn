import React from "react";
import Link from "next/link";
import {
  Search,
  ShieldCheck,
  Award,
  Users,
  Building2,
  Lock,
  ArrowRight,
  Stethoscope,
  BookOpen,
  MessageSquare,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { APP_NAME, APP_TAGLINE } from "@/lib/constants";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* Hero Section — Clean White */}
      <section className="relative pt-16 pb-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Column */}
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold">
                <ShieldCheck className="w-4 h-4" />
                <span>Professional Medical Network</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-[3.25rem] font-extrabold tracking-tight leading-[1.15] text-slate-900">
                Connect with{" "}
                <span className="text-blue-600">Verified</span>{" "}
                Medical Professionals.
              </h1>

              <p className="text-base sm:text-lg text-slate-500 max-w-2xl leading-relaxed">
                DoctorIn is a purpose-built professional ecosystem where medical doctors
                collaborate securely, hospitals discover talent, and users find
                accredited specialists.
              </p>

              {/* Search Bar */}
              <div className="pt-2 max-w-xl">
                <form
                  action="/doctors"
                  method="GET"
                  className="bg-white p-1.5 rounded-2xl border border-slate-200 flex flex-col sm:flex-row gap-2 shadow-sm"
                >
                  <div className="flex-1 flex items-center px-3 gap-2 bg-slate-50 rounded-xl border border-slate-200">
                    <Search className="w-5 h-5 text-slate-400 shrink-0" />
                    <input
                      type="text"
                      name="q"
                      placeholder="Search by specialization, doctor, or city..."
                      className="w-full py-3 bg-transparent text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
                    />
                  </div>
                  <Button type="submit" variant="primary" size="md" className="sm:w-auto w-full">
                    Search Doctors
                  </Button>
                </form>
              </div>

              {/* Trust Indicators */}
              <div className="pt-4 flex flex-wrap items-center gap-6 text-xs text-slate-500 font-medium">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>NMC / SMC Aligned</span>
                </div>
                <div className="flex items-center gap-2">
                  <Lock className="w-4 h-4 text-blue-600" />
                  <span>Private Doctor Messaging</span>
                </div>
                <div className="flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-slate-600" />
                  <span>Hospital Organization Pages</span>
                </div>
              </div>
            </div>

            {/* Right Column: Profile Mockup Card */}
            <div className="lg:col-span-5">
              <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-4">
                  Platform Preview
                </div>

                <div className="flex items-start gap-4 mb-5">
                  <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center text-white font-bold text-xl shrink-0">
                    AS
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-bold text-base text-slate-900">Dr. Ananya Sharma</h3>
                      <VerifiedBadge size="sm" showText={false} />
                    </div>
                    <p className="text-xs text-blue-600 font-semibold">Cardiologist & Electrophysiologist</p>
                    <p className="text-xs text-slate-500 mt-0.5">Apollo Hospitals, Hyderabad • 14 yrs exp</p>
                  </div>
                </div>

                <div className="space-y-3 mb-5">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                    <div className="flex items-center gap-2 text-slate-700 font-semibold mb-1">
                      <Award className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Credentials Verified</span>
                    </div>
                    <p className="text-slate-500 text-[11px]">
                      National Medical Commission Reg #10482 • MD Cardiology (AIIMS)
                    </p>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                    <div className="flex items-center gap-2 text-slate-700 font-semibold mb-1">
                      <BookOpen className="w-3.5 h-3.5 text-blue-600" />
                      <span>Recent Publication</span>
                    </div>
                    <p className="text-slate-500 text-[11px] line-clamp-1">
                      &quot;Advances in Catheter Ablation for Atrial Fibrillation&quot; — Lancet Cardiology 2025
                    </p>
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-slate-100">
                  <Link href="/register?role=doctor" className="flex-1">
                    <Button variant="primary" size="sm" className="w-full text-xs">
                      Claim Your Profile
                    </Button>
                  </Link>
                  <Link href="/doctors">
                    <Button variant="outline" size="sm" className="text-xs">
                      View Directory
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Roles Grid */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-14 space-y-3">
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Designed for the Medical Ecosystem
            </h2>
            <p className="text-slate-500 text-sm sm:text-base">
              Specialized workflows, authorization controls, and privacy for every medical stakeholder.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Doctors */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-11 h-11 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Stethoscope className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-slate-900">For Doctors</h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Showcase credentials, publish medical insights, and connect with verified peer doctors.
                </p>
                <ul className="space-y-1.5 text-xs text-slate-500">
                  <li className="flex items-center gap-1.5">✓ DoctorIn Verified Badge</li>
                  <li className="flex items-center gap-1.5">✓ Peer-to-peer secure messaging</li>
                  <li className="flex items-center gap-1.5">✓ Publications & achievements</li>
                </ul>
              </div>
              <div className="pt-5">
                <Link href="/register" className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1">
                  Join as Doctor <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Users */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-11 h-11 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center">
                  <Users className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-slate-900">For Users</h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Discover verified medical doctors by specialization, city, hospital, and experience.
                </p>
                <ul className="space-y-1.5 text-xs text-slate-500">
                  <li className="flex items-center gap-1.5">✓ Verified credential checks</li>
                  <li className="flex items-center gap-1.5">✓ Transparent experience filters</li>
                  <li className="flex items-center gap-1.5">✓ No clinical spam or fake reviews</li>
                </ul>
              </div>
              <div className="pt-5">
                <Link href="/doctors" className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center gap-1">
                  Find Specialists <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Hospitals */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-11 h-11 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
                  <Building2 className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-slate-900">For Hospitals</h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Manage organization profiles, publish updates, and recruit verified medical talent.
                </p>
                <ul className="space-y-1.5 text-xs text-slate-500">
                  <li className="flex items-center gap-1.5">✓ Organization presence</li>
                  <li className="flex items-center gap-1.5">✓ Doctor recruitment postings</li>
                  <li className="flex items-center gap-1.5">✓ Multi-admin management</li>
                </ul>
              </div>
              <div className="pt-5">
                <Link href="/register" className="text-xs font-bold text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
                  Register Hospital <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Admin */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-11 h-11 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-slate-900">Admin & Governance</h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Rigorous credential verification ensuring platform integrity and trust.
                </p>
                <ul className="space-y-1.5 text-xs text-slate-500">
                  <li className="flex items-center gap-1.5">✓ Document inspection queue</li>
                  <li className="flex items-center gap-1.5">✓ Comprehensive audit logging</li>
                  <li className="flex items-center gap-1.5">✓ Content moderation tools</li>
                </ul>
              </div>
              <div className="pt-5">
                <Link href="/admin" className="text-xs font-bold text-amber-600 hover:text-amber-700 flex items-center gap-1">
                  Admin Portal <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Security Banner — White */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-2xl p-8 sm:p-12 bg-slate-50 border border-slate-200 flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
                <Lock className="w-3.5 h-3.5" /> Medical Privacy Guardrails
              </div>
              <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                Trust by Design, Security by Architecture.
              </h3>
              <p className="text-sm text-slate-500 max-w-2xl leading-relaxed">
                DoctorIn enforces server-side role validation, private credential storage,
                OTP-backed access, and strict messaging authorization.
              </p>
            </div>

            <div className="flex gap-3 shrink-0">
              <Link href="/register">
                <Button variant="primary" size="lg">
                  Get Started Today
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
