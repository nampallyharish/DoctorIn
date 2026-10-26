"use client";

import { useEffect } from "react";

export function PWARegister() {
  useEffect(() => {
    if (typeof window !== "undefined" && "serviceWorker" in navigator) {
      window.addEventListener("load", () => {
        navigator.serviceWorker
          .register("/sw.js")
          .then((registration) => {
            console.log("DoctorIn PWA Service Worker registered:", registration.scope);
          })
          .catch((error) => {
            console.error("DoctorIn Service Worker registration failed:", error);
          });
      });
    }
  }, []);

  return null;
}
