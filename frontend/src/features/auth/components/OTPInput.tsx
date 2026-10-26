"use client";

import React, { useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface OTPInputProps {
  length?: number;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export const OTPInput: React.FC<OTPInputProps> = ({
  length = 6,
  value,
  onChange,
  disabled = false,
}) => {
  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
    const char = e.target.value.slice(-1);
    if (!/^\d*$/.test(char)) return;

    const newOtp = value.split("");
    newOtp[index] = char;
    const combined = newOtp.join("");
    onChange(combined);

    // Auto-advance to next input box
    if (char && index < length - 1) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === "Backspace" && !value[index] && index > 0) {
      inputsRef.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text/plain").trim();
    if (/^\d+$/.test(pastedData)) {
      const trimmed = pastedData.slice(0, length);
      onChange(trimmed);
      const focusIndex = Math.min(trimmed.length, length - 1);
      inputsRef.current[focusIndex]?.focus();
    }
  };

  return (
    <div className="flex items-center justify-between gap-2 sm:gap-3" onPaste={handlePaste}>
      {Array.from({ length }).map((_, index) => (
        <input
          key={index}
          ref={(el) => {
            inputsRef.current[index] = el;
          }}
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={1}
          disabled={disabled}
          value={value[index] || ""}
          onChange={(e) => handleChange(e, index)}
          onKeyDown={(e) => handleKeyDown(e, index)}
          className={cn(
            "w-12 h-14 text-center text-xl font-bold rounded-xl border border-slate-300 bg-white text-slate-900 shadow-sm transition-all",
            "focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600",
            disabled && "bg-slate-100 opacity-60 cursor-not-allowed"
          )}
        />
      ))}
    </div>
  );
};
