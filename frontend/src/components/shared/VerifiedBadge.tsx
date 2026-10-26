import React from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface VerifiedBadgeProps {
  className?: string;
  showText?: boolean;
  size?: "sm" | "md" | "lg";
}

export const VerifiedBadge: React.FC<VerifiedBadgeProps> = ({
  className,
  showText = true,
  size = "sm",
}) => {
  const iconSizes = {
    sm: "w-3 h-3",
    md: "w-3.5 h-3.5",
    lg: "w-4 h-4",
  };

  return (
    <span
      title="DoctorIn Verified Medical Professional"
      className={cn(
        "inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-medium select-none shrink-0",
        size === "sm" && "text-[11px]",
        size === "md" && "text-xs",
        size === "lg" && "text-sm px-2 py-1",
        className
      )}
    >
      <span className="w-3.5 h-3.5 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0">
        <Check className={cn(iconSizes[size], "stroke-[3]")} />
      </span>
      {showText && <span>DoctorIn Verified</span>}
    </span>
  );
};
