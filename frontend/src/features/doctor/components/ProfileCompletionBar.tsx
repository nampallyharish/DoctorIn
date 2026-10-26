"use client";

import React from "react";
import { CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ProfileCompletionBarProps {
  percentage: number;
  className?: string;
}

export const ProfileCompletionBar: React.FC<ProfileCompletionBarProps> = ({
  percentage,
  className,
}) => {
  const getStatusColor = () => {
    if (percentage >= 80) return "bg-emerald-500 text-emerald-700";
    if (percentage >= 50) return "bg-teal-500 text-teal-700";
    return "bg-amber-500 text-amber-700";
  };

  return (
    <div className={cn("bg-white rounded-2xl p-4 border border-slate-200 shadow-sm space-y-2", className)}>
      <div className="flex items-center justify-between text-xs font-bold text-slate-800">
        <span className="flex items-center gap-1.5">
          {percentage === 100 ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          ) : (
            <AlertCircle className="w-4 h-4 text-teal-600" />
          )}
          Profile Strength
        </span>
        <span>{percentage}% Complete</span>
      </div>

      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-500", getStatusColor())}
          style={{ width: `${Math.max(percentage, 5)}%` }}
        />
      </div>

      <p className="text-[11px] text-slate-500 leading-tight">
        {percentage >= 80
          ? "🌟 Excellent! Your profile is comprehensive and stands out to peers and patients."
          : "Add your degrees, past hospitals, and publications to increase discovery visibility."}
      </p>
    </div>
  );
};
