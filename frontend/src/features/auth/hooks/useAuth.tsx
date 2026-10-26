"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { User, UserRole } from "@/types";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  loginWithTokens: (accessToken: string, refreshToken: string, userData?: any) => Promise<void> | void;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();

  const refreshProfile = async () => {
    try {
      const response = await apiClient.get<User>("/auth/me");
      if (response.success && response.data) {
        let profile = response.data;
        if (profile.role === "doctor") {
          try {
            const docRes = await apiClient.get<any>("/doctors/me");
            if (docRes.success && docRes.data) {
              profile = {
                ...profile,
                full_name: docRes.data.full_name,
                profile_photo_url: docRes.data.profile_photo_url,
              };
            }
          } catch {
            // Non-blocking fallback
          }
        }
        setUser((prev) => ({
          ...(prev || {}),
          ...profile,
          full_name: profile.full_name || prev?.full_name,
          profile_photo_url: profile.profile_photo_url || prev?.profile_photo_url,
        }));
      } else {
        const token = typeof window !== "undefined" ? localStorage.getItem("doctorin_access_token") : null;
        if (!token) {
          setUser(null);
        }
      }
    } catch {
      const token = typeof window !== "undefined" ? localStorage.getItem("doctorin_access_token") : null;
      if (!token) {
        setUser(null);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("doctorin_access_token");
    if (token) {
      refreshProfile();
    } else {
      setIsLoading(false);
    }
  }, []);

  const loginWithTokens = async (accessToken: string, refreshToken: string, userData?: any) => {
    localStorage.setItem("doctorin_access_token", accessToken);
    localStorage.setItem("doctorin_refresh_token", refreshToken);
    if (userData) {
      setUser((prev) => ({
        ...(prev || {}),
        ...userData,
      }));
      setIsLoading(false);
    }
    await refreshProfile();
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem("doctorin_refresh_token");
    if (refreshToken) {
      try {
        await apiClient.post("/auth/logout", { refresh_token: refreshToken });
      } catch {
        // Continue clearing tokens locally even if API call fails
      }
    }
    localStorage.removeItem("doctorin_access_token");
    localStorage.removeItem("doctorin_refresh_token");
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        loginWithTokens,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    return {
      user: null,
      isLoading: false,
      isAuthenticated: false,
      loginWithTokens: () => {},
      logout: async () => {
        if (typeof window !== "undefined") {
          localStorage.removeItem("doctorin_access_token");
          localStorage.removeItem("doctorin_refresh_token");
          window.location.href = "/login";
        }
      },
      refreshProfile: async () => {},
    };
  }
  return context;
};
