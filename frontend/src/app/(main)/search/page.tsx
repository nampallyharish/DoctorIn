"use client";

import React, { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Search,
  Building2,
  Briefcase,
  ShieldCheck,
  ArrowRight,
  Filter,
  Users,
} from "lucide-react";
import { SearchFiltersSidebar } from "@/features/search/components/SearchFiltersSidebar";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { DoctorSearchResultItem, LookupItem } from "@/types";

function SearchPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const queryQ = searchParams.get("q") || "";
  const querySpec = searchParams.get("specialization_slug") || "";

  const [searchTerm, setSearchTerm] = useState(queryQ);
  const [selectedSpec, setSelectedSpec] = useState(querySpec);
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [minExperience, setMinExperience] = useState<number | "">("");
  const [sortBy, setSortBy] = useState("relevance");

  const [doctors, setDoctors] = useState<DoctorSearchResultItem[]>([]);
  const [specializations, setSpecializations] = useState<LookupItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  // Load specializations
  useEffect(() => {
    async function loadSpecs() {
      const res = await apiClient.get<LookupItem[]>("/search/specializations");
      if (res.success && res.data) {
        setSpecializations(res.data);
      }
    }
    loadSpecs();
  }, []);

  // Execute Search
  const executeSearch = async () => {
    setIsLoading(true);
    const params = new URLSearchParams();
    if (searchTerm.trim()) params.set("q", searchTerm.trim());
    if (selectedSpec) params.set("specialization_slug", selectedSpec);
    if (verifiedOnly) params.set("verified_only", "true");
    if (minExperience !== "") params.set("min_experience", String(minExperience));
    if (sortBy) params.set("sort_by", sortBy);

    const res = await apiClient.get<DoctorSearchResultItem[]>(`/search/doctors?${params.toString()}`);
    setIsLoading(false);

    if (res.success && res.data) {
      setDoctors(res.data);
      setTotalCount(res.meta?.total || res.data.length);
    }
  };

  useEffect(() => {
    executeSearch();
  }, [selectedSpec, verifiedOnly, minExperience, sortBy]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch();
  };

  const handleResetFilters = () => {
    setSearchTerm("");
    setSelectedSpec("");
    setVerifiedOnly(false);
    setMinExperience("");
    setSortBy("relevance");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Search Bar */}
      <div className="bg-white rounded-3xl p-4 sm:p-6 border border-slate-200 shadow-sm space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 flex items-center px-4 gap-2 bg-slate-50 border border-slate-300 rounded-2xl focus-within:ring-2 focus-within:ring-teal-500 focus-within:bg-white transition-all">
            <Search className="w-5 h-5 text-teal-600 shrink-0" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by doctor name, medical specialty, hospital, or clinical focus..."
              className="w-full py-3 bg-transparent text-sm focus:outline-none"
            />
          </div>
          <Button type="submit" variant="primary" size="md" className="sm:w-auto w-full">
            Search Doctors
          </Button>
        </form>
      </div>

      {/* Main Grid: Sidebar + Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Filters Sidebar */}
        <div className="lg:col-span-4">
          <SearchFiltersSidebar
            specializations={specializations}
            selectedSpec={selectedSpec}
            onSelectSpec={setSelectedSpec}
            verifiedOnly={verifiedOnly}
            onToggleVerified={setVerifiedOnly}
            minExperience={minExperience}
            onChangeMinExperience={setMinExperience}
            sortBy={sortBy}
            onChangeSortBy={setSortBy}
            onResetFilters={handleResetFilters}
          />
        </div>

        {/* Right Search Results */}
        <div className="lg:col-span-8 space-y-6">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 border-b border-slate-200 pb-3">
            <span>Found {totalCount} matching doctor(s)</span>
            <span className="text-teal-700">Sorted by: {sortBy.replace("_", " ")}</span>
          </div>

          {isLoading ? (
            <div className="text-center py-20 text-sm text-slate-500">
              Searching doctor directory...
            </div>
          ) : doctors.length === 0 ? (
            <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 space-y-3">
              <Users className="w-8 h-8 text-slate-300 mx-auto" />
              <p className="text-base font-bold text-slate-800">No doctors match your criteria</p>
              <p className="text-xs text-slate-400">
                Try widening your experience range or clearing specialty filters.
              </p>
              <Button variant="outline" size="sm" onClick={handleResetFilters} className="text-xs">
                Reset All Filters
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {doctors.map((doc) => (
                <div
                  key={doc.id}
                  className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-teal-600 to-sky-600 text-white font-bold text-xl flex items-center justify-center shadow shrink-0">
                      {doc.full_name.split(" ").map((n: string) => n[0]).slice(0, 2).join("")}
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-bold text-slate-900 text-base">{doc.full_name}</h3>
                        {doc.verification_status === "verified" && <VerifiedBadge size="sm" />}
                      </div>

                      <p className="text-xs text-teal-700 font-semibold">{doc.headline || "Medical Specialist"}</p>

                      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 pt-0.5">
                        {doc.current_organization && (
                          <span className="flex items-center gap-1">
                            <Building2 className="w-3.5 h-3.5 text-slate-400" /> {doc.current_organization}
                          </span>
                        )}
                        {doc.years_of_experience !== undefined && (
                          <span className="flex items-center gap-1">
                            <Briefcase className="w-3.5 h-3.5 text-slate-400" /> {doc.years_of_experience} yrs exp
                          </span>
                        )}
                      </div>

                      {doc.specializations && doc.specializations.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1.5">
                          {doc.specializations.map((spec: any) => (
                            <Badge key={spec.id} variant="info" className="text-[10px]">
                              {spec.name}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="self-end sm:self-center shrink-0 w-full sm:w-auto">
                    <Link href={`/doctors/${doc.slug}`}>
                      <Button variant="primary" size="sm" className="w-full sm:w-auto text-xs flex items-center justify-center gap-1">
                        View Profile <ArrowRight className="w-3.5 h-3.5" />
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-sm text-slate-500">Loading Search...</div>}>
      <SearchPageContent />
    </Suspense>
  );
}
