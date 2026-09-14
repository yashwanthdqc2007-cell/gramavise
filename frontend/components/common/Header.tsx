"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X, Landmark, History, PlusCircle, ArrowRight, Sprout } from "lucide-react";
import { LanguageToggle } from "@/components/common/LanguageToggle";
import { useTranslation } from "@/lib/i18n";
import { NetworkStatusBar } from "@/components/common/NetworkStatusBar";

export const Header: React.FC = () => {
  const { t } = useTranslation();
  const pathname = usePathname();
  const isLanding = pathname === "/";
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header
      className={`sticky top-0 z-50 transition-colors duration-200 bg-[#06131F]/90 backdrop-blur-md border-b border-slate-800/80 text-white`}
    >
      <NetworkStatusBar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand & Subtle Hackathon Identifier */}
        <div className="flex min-w-0 items-center space-x-2 sm:space-x-3">
          <Link href="/" className="flex min-w-0 items-center space-x-2.5 group">
            {/* Emerald Nature/Growth Inspired Emblem */}
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center font-black text-lg shadow-sm transition-all bg-gradient-to-br from-emerald-400 to-teal-600 text-slate-950 shadow-emerald-500/20 group-hover:scale-105"
            >
              <Sprout className="w-5 h-5" aria-hidden="true" />
            </div>
            <span className="text-xl sm:text-2xl font-black tracking-tight transition-colors text-white group-hover:text-emerald-400 truncate">
              {t("nav.brand")}
            </span>
          </Link>
          <span className="hidden sm:inline-flex items-center text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider text-slate-400 bg-slate-800/80 border border-slate-700/60">
            {t("nav.hackathonBadge")}
          </span>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          <nav className="flex items-center space-x-7 text-sm font-medium text-slate-300">
            <Link href="/onboarding" className="inline-flex items-center gap-1.5 transition-colors hover:text-emerald-400">
              <PlusCircle className="w-4 h-4 text-emerald-400" aria-hidden="true" />
              <span>{t("nav.newAdvisory")}</span>
            </Link>
            <Link href="/schemes" className="inline-flex items-center gap-1.5 transition-colors hover:text-emerald-400">
              <Landmark className="w-4 h-4 text-slate-400" aria-hidden="true" />
              <span>{t("nav.schemesDirectory")}</span>
            </Link>
            <Link href="/history" className="inline-flex items-center gap-1.5 transition-colors hover:text-emerald-400">
              <History className="w-4 h-4 text-slate-400" aria-hidden="true" />
              <span>{t("nav.history")}</span>
            </Link>
          </nav>

          <div className="h-5 w-[1px] bg-slate-800" aria-hidden="true" />

          <div className="flex items-center gap-3">
            <LanguageToggle isDark />

            <Link href="/onboarding">
              <button
                type="button"
                className="bg-[#19D98B] hover:bg-[#16C784] text-slate-950 font-bold px-4 py-2 rounded-xl text-xs sm:text-sm shadow-md shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all inline-flex items-center gap-1"
              >
                <span>{t("nav.getStarted")}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </Link>
          </div>
        </div>

        {/* Mobile Nav Trigger & Compact Language Toggle */}
        <div className="flex shrink-0 md:hidden items-center space-x-1 sm:space-x-2">
          <LanguageToggle isDark />
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg focus:outline-none focus:ring-2 text-slate-300 hover:text-white hover:bg-slate-800 focus:ring-emerald-500"
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6 text-white" aria-hidden="true" />
            ) : (
              <Menu className="w-6 h-6 text-white" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div
        className="md:hidden border-t border-slate-800 bg-[#071827] text-white px-4 pt-3 pb-5 space-y-2 animate-in fade-in duration-150"
        >
          <div className="flex items-center justify-between py-1 px-3 mb-2">
            <span className="text-xs font-medium text-slate-400">
              {t("nav.hackathonBadge")}
            </span>
          </div>
          <Link
            href="/onboarding"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-semibold text-emerald-300 bg-emerald-950/40 border border-emerald-800/50 hover:bg-emerald-950/60 transition-colors"
          >
            <PlusCircle className="w-4 h-4 text-emerald-400" aria-hidden="true" />
            <span>{t("nav.newAdvisory")}</span>
          </Link>
          <Link
            href="/schemes"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800/60 hover:text-white transition-colors"
          >
            <Landmark className="w-4 h-4 text-slate-400" aria-hidden="true" />
            <span>{t("nav.schemesDirectory")}</span>
          </Link>
          <Link
            href="/history"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800/60 hover:text-white transition-colors"
          >
            <History className="w-4 h-4 text-slate-400" aria-hidden="true" />
            <span>{t("nav.history")}</span>
          </Link>

          {isLanding && (
            <div className="pt-2">
              <Link
                href="/onboarding"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full bg-[#19D98B] hover:bg-[#16C784] text-slate-950 font-bold px-4 py-2.5 rounded-xl text-sm shadow-md shadow-emerald-500/20 transition-all flex items-center justify-center gap-1.5"
              >
                <span>{t("nav.getStarted")}</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
};
