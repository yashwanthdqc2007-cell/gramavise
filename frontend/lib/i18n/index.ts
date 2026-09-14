"use client";

import React, { createContext, useContext, useState, useEffect, useMemo, ReactNode } from "react";
import { SupportedLanguage, TranslationDictionary } from "./types";
import { en } from "./dictionaries/en";
import { hi } from "./dictionaries/hi";
import { mr } from "./dictionaries/mr";
import { bn } from "./dictionaries/bn";
import { te } from "./dictionaries/te";
import { ta } from "./dictionaries/ta";

export * from "./types";

export const DICTIONARIES: Record<SupportedLanguage, TranslationDictionary> = {
  en,
  hi,
  mr,
  bn,
  te,
  ta,
};

export const SUPPORTED_LANGUAGE_OPTIONS: { code: SupportedLanguage; label: string; nativeLabel: string }[] = [
  { code: "en", label: "English", nativeLabel: "English" },
  { code: "hi", label: "Hindi", nativeLabel: "हिन्दी" },
  { code: "mr", label: "Marathi", nativeLabel: "मराठी" },
  { code: "bn", label: "Bengali", nativeLabel: "বাংলা" },
  { code: "te", label: "Telugu", nativeLabel: "తెలుగు" },
  { code: "ta", label: "Tamil", nativeLabel: "தமிழ்" },
];

interface LanguageContextType {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  t: (path: string, params?: Record<string, string | number>) => string;
  dictionary: TranslationDictionary;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Helper function to resolve nested keys like "results.financial.title"
function getNestedTranslation(obj: any, path: string): string | undefined {
  const parts = path.split(".");
  let current: any = obj;
  for (const part of parts) {
    if (current === undefined || current === null) return undefined;
    current = current[part];
  }
  return typeof current === "string" ? current : undefined;
}

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<SupportedLanguage>("en");

  // Load language preference from sessionStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = sessionStorage.getItem("gramavise_language") as SupportedLanguage;
        if (stored && DICTIONARIES[stored]) {
          setLanguageState(stored);
        }
      } catch {
        // Fallback to default
      }

      // Listen for language changes dispatched anywhere in the window
      const handleLanguageChanged = (e: Event) => {
        const customEvent = e as CustomEvent<SupportedLanguage>;
        if (customEvent.detail && DICTIONARIES[customEvent.detail]) {
          setLanguageState(customEvent.detail);
        }
      };

      window.addEventListener("gramavise_language_changed", handleLanguageChanged as EventListener);
      return () => {
        window.removeEventListener("gramavise_language_changed", handleLanguageChanged as EventListener);
      };
    }
  }, []);

  const setLanguage = (newLang: SupportedLanguage) => {
    if (!DICTIONARIES[newLang]) return;
    setLanguageState(newLang);
    if (typeof window !== "undefined") {
      try {
        sessionStorage.setItem("gramavise_language", newLang);
        window.dispatchEvent(new CustomEvent("gramavise_language_changed", { detail: newLang }));
      } catch {
        // Ignore storage errors
      }
    }
  };

  const dictionary = useMemo(() => {
    return DICTIONARIES[language] || DICTIONARIES.en;
  }, [language]);

  const t = useMemo(() => {
    return (path: string, params?: Record<string, string | number>): string => {
      // 1. Try selected language dictionary
      let text = getNestedTranslation(dictionary, path);

      // 2. Fallback to English dictionary if key is missing in active language
      if (text === undefined) {
        text = getNestedTranslation(DICTIONARIES.en, path);
      }

      // 3. Final fallback: return key path itself
      if (text === undefined) {
        return path;
      }

      // Replace optional parameters like {count} or {name}
      if (params) {
        Object.entries(params).forEach(([key, val]) => {
          text = text?.replace(new RegExp(`\\{${key}\\}`, "g"), String(val));
        });
      }

      return text || path;
    };
  }, [dictionary]);

  return React.createElement(
    LanguageContext.Provider,
    { value: { language, setLanguage, t, dictionary } },
    children
  );
};

export const useTranslation = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    // Return a graceful fallback if rendered outside LanguageProvider
    const defaultDict = DICTIONARIES.en;
    return {
      language: "en",
      setLanguage: () => {},
      t: (path: string, params?: Record<string, string | number>) => {
        let text = getNestedTranslation(defaultDict, path) || path;
        if (params) {
          Object.entries(params).forEach(([k, v]) => {
            text = text.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
          });
        }
        return text;
      },
      dictionary: defaultDict,
    };
  }
  return context;
};
