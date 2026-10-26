"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Stethoscope,
  Search,
  ShieldCheck,
  User,
  Building2,
  LogOut,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/features/auth/hooks/useAuth";

interface ProfileDropdownProps {
  idPrefix?: string;
  align?: "left" | "right";
}

const ProfileDropdown: React.FC<ProfileDropdownProps> = ({ idPrefix = "nav", align = "right" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();
  const router = useRouter();

  // Close dropdown on click outside or Escape key
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleKeyDown);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  const handleSignOut = async () => {
    setIsOpen(false);
    try {
      await logout();
    } catch {
      if (typeof window !== "undefined") {
        localStorage.removeItem("doctorin_access_token");
        localStorage.removeItem("doctorin_refresh_token");
        router.push("/login");
      }
    }
  };

  const getInitials = (): string => {
    if (!user) return "";
    if (user.full_name) {
      const parts = user.full_name.trim().split(" ");
      if (parts.length >= 2) {
        return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
      }
      return user.full_name.slice(0, 2).toUpperCase();
    }
    if (user.email) {
      return user.email.slice(0, 2).toUpperCase();
    }
    return "";
  };

  const initials = getInitials();

  return (
    <div ref={dropdownRef} className="relative inline-block text-left">
      <button
        type="button"
        id={`${idPrefix}-profile-avatar-btn`}
        onClick={() => setIsOpen((prev) => !prev)}
        className="relative flex items-center justify-center w-8 h-8 rounded-full bg-blue-50 border border-blue-200 text-blue-600 hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-1 transition-all cursor-pointer overflow-hidden shadow-xs shrink-0"
        aria-label="User Profile Menu"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {user?.profile_photo_url ? (
          <img
            src={user.profile_photo_url}
            alt={user.full_name || user.email || "Profile"}
            className="w-full h-full object-cover rounded-full"
          />
        ) : initials ? (
          <span className="text-xs font-bold text-blue-700 tracking-wider">
            {initials}
          </span>
        ) : (
          <User className="w-4 h-4 text-blue-600" />
        )}
      </button>

      {isOpen && (
        <div
          id={`${idPrefix}-profile-dropdown-menu`}
          className={`absolute ${align === "left" ? "left-0" : "right-0"} mt-2 w-52 bg-white rounded-xl shadow-lg border border-slate-200 py-1.5 z-50 animate-in fade-in slide-in-from-top-1 duration-150`}
          role="menu"
          aria-orientation="vertical"
          aria-labelledby={`${idPrefix}-profile-avatar-btn`}
        >
          <Link
            href="/profile"
            id={`${idPrefix}-dropdown-item-profile`}
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-2.5 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition-colors"
            role="menuitem"
          >
            <User className="w-4 h-4 text-slate-400 shrink-0" />
            <span>Profile</span>
          </Link>

          <Link
            href="/verification"
            id={`${idPrefix}-dropdown-item-doctor`}
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-2.5 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition-colors"
            role="menuitem"
          >
            <Stethoscope className="w-4 h-4 text-blue-600 shrink-0" />
            <span>Doctor Account</span>
          </Link>

          <Link
            href="/hospitals/apply"
            id={`${idPrefix}-dropdown-item-hospital`}
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-2.5 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition-colors"
            role="menuitem"
          >
            <Building2 className="w-4 h-4 text-slate-600 shrink-0" />
            <span>Hospital Account</span>
          </Link>

          <div className="my-1 border-t border-slate-100" />

          <button
            type="button"
            id={`${idPrefix}-dropdown-item-signout`}
            onClick={handleSignOut}
            className="flex items-center gap-2.5 px-4 py-2.5 text-sm font-semibold text-rose-600 hover:bg-rose-50 hover:text-rose-700 transition-colors w-full text-left cursor-pointer"
            role="menuitem"
          >
            <LogOut className="w-4 h-4 text-rose-500 shrink-0" />
            <span>Sign Out</span>
          </button>
        </div>
      )}
    </div>
  );
};

export const Navbar: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2 group shrink-0">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <Stethoscope className="w-[18px] h-[18px]" />
          </div>
          <span className="text-xl font-black tracking-tight text-slate-900">
            Doctor<span className="text-blue-600">In</span>
          </span>
        </Link>

        {/* Search Bar */}
        <div className="hidden md:flex flex-1 max-w-md mx-6">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search doctors, specialization, hospital..."
              className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent focus:bg-white transition-all placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Navigation links */}
        <nav className="hidden md:flex items-center gap-5 text-sm font-semibold text-slate-600 shrink-0">
          <Link href="/doctors" className="hover:text-blue-600 transition-colors">
            Find Doctors
          </Link>
          <Link href="/hospitals/apply" className="hover:text-blue-600 transition-colors">
            Hospitals
          </Link>
          <Link href="/feed" className="hover:text-blue-600 transition-colors">
            Feed
          </Link>
          {isAuthenticated && <ProfileDropdown idPrefix="desktop" />}
          <div className="flex items-center gap-1 text-emerald-700 text-[11px] font-bold px-2 py-0.5 bg-emerald-50 rounded-full border border-emerald-200">
            <ShieldCheck className="w-3 h-3" /> Verified Network
          </div>
        </nav>

        {/* Auth CTAs & Mobile Avatar */}
        {isAuthenticated ? (
          <div className="md:hidden flex items-center gap-2 ml-4 shrink-0">
            <ProfileDropdown idPrefix="mobile" align="left" />
          </div>
        ) : !isLoading ? (
          <div className="flex items-center gap-2 ml-4 shrink-0">
            <Link href="/login">
              <Button variant="ghost" size="sm">
                Sign In
              </Button>
            </Link>
            <Link href="/register">
              <Button variant="primary" size="sm">
                Join DoctorIn
              </Button>
            </Link>
          </div>
        ) : null}
      </div>
    </header>
  );
};
