"use client";

import React, { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Search, MapPin, Building2, Briefcase, Filter, ShieldCheck, ArrowRight } from "lucide-react";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { DoctorPublicProfileResponse } from "@/types";

function DoctorsDirectoryContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [searchTerm, setSearchTerm] = useState(initialQuery);
  const [doctors, setDoctors] = useState<DoctorPublicProfileResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDoctors = async () => {
    setIsLoading(true);
    const res = await apiClient.get<DoctorPublicProfileResponse[]>("/doctors?page=1&per_page=20");
    setIsLoading(false);

    if (res.success && res.data) {
      setDoctors(res.data);
    }
  };

  useEffect(() => {
    fetchDoctors();
  }, []);

  const filteredDoctors = doctors.filter((doc) => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    return (
      doc.full_name.toLowerCase().includes(term) ||
      (doc.headline && doc.headline.toLowerCase().includes(term)) ||
      (doc.current_organization && doc.current_organization.toLowerCase().includes(term))
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header & Search */}
      <div className="space-y-4 max-w-3xl">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-teal-50 text-teal-700 text-xs font-semibold border border-teal-200">
          <ShieldCheck className="w-3.5 h-3.5" /> Verified Medical Practitioners
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Doctor Directory & Discovery
        </h1>
        <p className="text-sm text-slate-600">
          Search and connect with accredited medical specialists across specializations and hospitals.
        </p>

        <div className="pt-2 flex items-center gap-2 bg-white p-2 rounded-2xl border border-slate-200 shadow-sm">
          <Search className="w-5 h-5 text-teal-600 ml-2" />
          <input
            type="text"
            placeholder="Search by doctor name, specialization, or hospital..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full py-2 bg-transparent text-sm focus:outline-none"
          />
        </div>
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between text-xs font-semibold text-slate-500 border-b border-slate-200 pb-3">
        <span>Showing {filteredDoctors.length} doctors</span>
      </div>

      {/* Directory Grid */}
      {isLoading ? (
        <div className="text-center py-20 text-sm text-slate-500">
          Loading doctor directory...
        </div>
      ) : filteredDoctors.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 space-y-3">
          <p className="text-sm font-semibold text-slate-700">No doctors match your query.</p>
          <p className="text-xs text-slate-400">Try adjusting your keywords or clearing the search filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDoctors.map((doc) => (
            <div
              key={doc.id}
              className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-teal-600 to-sky-600 text-white font-bold text-lg flex items-center justify-center shadow shrink-0">
                    {doc.full_name.split(" ").map((n: string) => n[0]).slice(0, 2).join("")}
                  </div>

                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5">
                      <h3 className="font-bold text-slate-900 text-sm">{doc.full_name}</h3>
                      {doc.verification_status === "verified" && <VerifiedBadge size="sm" />}
                    </div>
                    <p className="text-xs text-teal-700 font-medium line-clamp-1">{doc.headline || "Medical Specialist"}</p>
                    {doc.current_organization && (
                      <p className="text-xs text-slate-400 flex items-center gap-1">
                        <Building2 className="w-3 h-3" /> {doc.current_organization}
                      </p>
                    )}
                  </div>
                </div>

                {doc.years_of_experience !== undefined && (
                  <p className="text-xs text-slate-500 flex items-center gap-1 pt-1">
                    <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                    <span>{doc.years_of_experience} years clinical experience</span>
                  </p>
                )}

                {doc.specializations && doc.specializations.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {doc.specializations.map((spec: any) => (
                      <Badge key={spec.id} variant="info" className="text-[10px]">
                        {spec.name}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <div className="pt-2 border-t border-slate-100">
                <Link href={`/doctors/${doc.slug}`}>
                  <Button variant="outline" size="sm" className="w-full text-xs flex items-center justify-center gap-1">
                    View Verified Profile <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function DoctorsDirectoryPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-sm text-slate-500">Loading Directory...</div>}>
      <DoctorsDirectoryContent />
    </Suspense>
  );
}
