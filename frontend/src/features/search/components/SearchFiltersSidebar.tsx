"use client";

import React from "react";
import { Filter, ShieldCheck, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface SearchFiltersProps {
  specializations: any[];
  selectedSpec: string;
  onSelectSpec: (spec: string) => void;
  verifiedOnly: boolean;
  onToggleVerified: (val: boolean) => void;
  minExperience: number | "";
  onChangeMinExperience: (val: number | "") => void;
  sortBy: string;
  onChangeSortBy: (val: string) => void;
  onResetFilters: () => void;
}

export const SearchFiltersSidebar: React.FC<SearchFiltersProps> = ({
  specializations,
  selectedSpec,
  onSelectSpec,
  verifiedOnly,
  onToggleVerified,
  minExperience,
  onChangeMinExperience,
  sortBy,
  onChangeSortBy,
  onResetFilters,
}) => {
  return (
    <aside className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-6">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Filter className="w-4 h-4 text-teal-600" /> Filter Doctors
        </h3>
        <button
          type="button"
          onClick={onResetFilters}
          className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1 font-medium"
        >
          <RotateCcw className="w-3 h-3" /> Reset
        </button>
      </div>

      {/* Verified Only Toggle */}
      <div className="space-y-2">
        <label className="flex items-center gap-2.5 p-3 rounded-2xl bg-teal-50/60 border border-teal-200/80 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={verifiedOnly}
            onChange={(e) => onToggleVerified(e.target.checked)}
            className="w-4 h-4 rounded text-teal-600 focus:ring-teal-500"
          />
          <div>
            <div className="text-xs font-bold text-teal-900 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-teal-600" /> DoctorIn Verified Only
            </div>
            <p className="text-[11px] text-teal-700">Display credential-verified doctors</p>
          </div>
        </label>
      </div>

      {/* Sorting Strategy */}
      <div className="space-y-2">
        <label className="block text-xs font-bold text-slate-700">Sort Ranking</label>
        <select
          value={sortBy}
          onChange={(e) => onChangeSortBy(e.target.value)}
          className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-teal-500 font-medium"
        >
          <option value="relevance">Top Relevance (Verified First)</option>
          <option value="experience_desc">Most Clinical Experience</option>
          <option value="recently_added">Recently Joined</option>
        </select>
      </div>

      {/* Minimum Experience Filter */}
      <div className="space-y-2">
        <label className="block text-xs font-bold text-slate-700">
          Minimum Experience (Years)
        </label>
        <div className="flex gap-2">
          {[0, 5, 10, 15].map((years) => (
            <button
              key={years}
              type="button"
              onClick={() => onChangeMinExperience(years === 0 ? "" : years)}
              className={`flex-1 py-1.5 rounded-xl border text-xs font-bold transition-all ${
                (years === 0 && minExperience === "") || minExperience === years
                  ? "bg-teal-600 text-white border-teal-600"
                  : "bg-slate-50 text-slate-600 border-slate-200 hover:border-slate-300"
              }`}
            >
              {years === 0 ? "Any" : `${years}+`}
            </button>
          ))}
        </div>
      </div>

      {/* Specialization Filter */}
      <div className="space-y-2">
        <label className="block text-xs font-bold text-slate-700">Medical Specialty</label>
        <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
          <button
            type="button"
            onClick={() => onSelectSpec("")}
            className={`w-full text-left px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              selectedSpec === ""
                ? "bg-teal-50 text-teal-800 font-bold"
                : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            All Specialties
          </button>
          {specializations.map((spec) => (
            <button
              key={spec.id}
              type="button"
              onClick={() => onSelectSpec(spec.slug)}
              className={`w-full text-left px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                selectedSpec === spec.slug
                  ? "bg-teal-50 text-teal-800 font-bold"
                  : "text-slate-600 hover:bg-slate-50"
              }`}
            >
              {spec.name}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};
