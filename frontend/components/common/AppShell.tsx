"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  PlusCircle,
  Landmark,
  History,
  Sprout,
  ArrowRight,
  Menu,
  X,
  Sparkles,
  ShieldCheck,
  HelpCircle,
  Settings,
} from "lucide-react";
import { LanguageToggle } from "@/components/common/LanguageToggle";
import { useTranslation } from "@/lib/i18n";
import { Header } from "@/components/common/Header";
import { GramaViseIcon, GramaViseLogo } from "@/components/common/GramaViseLogo";

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const { t } = useTranslation();
  const pathname = usePathname();
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  const navItems = [
    {
      href: "/",
      label: t("nav.dashboard") || "Dashboard",
      icon: LayoutDashboard,
      isActive: pathname === "/",
    },
    {
      href: "/onboarding",
      label: t("nav.newAdvisory"),
      icon: PlusCircle,
      isActive: pathname === "/onboarding",
    },
    {
      href: "/history",
      label: t("nav.history"),
      icon: History,
      isActive: pathname === "/history" || pathname.startsWith("/history/"),
    },
    {
      href: "/schemes",
      label: t("nav.schemesDirectory"),
      icon: Landmark,
      isActive: pathname === "/schemes",
    },
    {
      href: "/help",
      label: t("nav.help") || "Help & Guidance",
      icon: HelpCircle,
      isActive: pathname === "/help",
    },
    {
      href: "/settings",
      label: t("nav.settings") || "Settings",
      icon: Settings,
      isActive: pathname === "/settings",
    },
  ];

  return (
    <div className="min-h-screen flex bg-[#050E17] text-slate-100 antialiased selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* ============================================================ */}
      {/* DESKTOP PERSISTENT SIDEBAR                                  */}
      {/* ============================================================ */}
      <aside className="hidden lg:flex flex-col w-64 shrink-0 bg-[#040F19] border-r border-slate-800/80 sticky top-0 h-screen z-40">
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800/70">
          <Link href="/" className="flex items-center justify-between group">
            <GramaViseLogo size="md" animated={true} />
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 uppercase tracking-wider">
                {t("nav.hackathonBadge")}
              </span>
              <span className="text-[10px] text-slate-400 font-medium mt-0.5">v1.0</span>
            </div>
          </Link>
        </div>

        {/* Primary CTA Button */}
        <div className="p-4 pb-2">
          <Link
            href="/onboarding"
            className="w-full bg-gradient-to-r from-[#19D98B] to-emerald-500 hover:from-[#16C784] hover:to-emerald-400 text-[#040F19] font-bold px-4 py-2.5 rounded-xl text-xs shadow-md shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all flex items-center justify-between group active:scale-[0.98]"
          >
            <span className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>{t("nav.newAdvisory")}</span>
            </span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>

        {/* Navigation Links */}
        <nav aria-label="Sidebar Navigation" className="flex-1 px-3 py-3 space-y-1.5 overflow-y-auto">
          <div className="px-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Workspace
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={item.isActive ? "page" : undefined}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  item.isActive
                    ? "text-[#19D98B] bg-[#0E2635] border border-emerald-500/30 shadow-xs font-bold"
                    : "text-slate-400 hover:text-slate-100 hover:bg-[#0E2635]/60 border border-transparent"
                }`}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 ${
                    item.isActive ? "text-[#19D98B]" : "text-slate-400 group-hover:text-slate-300"
                  }`}
                  aria-hidden="true"
                />
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-slate-800/80 space-y-3 bg-[#030B13]/60">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium text-slate-400">Language</span>
            <LanguageToggle isDark />
          </div>

          <div className="pt-2 border-t border-slate-800/60 flex items-center gap-1.5 text-[10px] text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400/80 shrink-0" />
            <span className="truncate leading-tight">Deterministic Feasibility Engine</span>
          </div>
        </div>
      </aside>

      {/* ============================================================ */}
      {/* MOBILE SLIDE-OVER DRAWER OVERLAY                            */}
      {/* ============================================================ */}
      {mobileDrawerOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200"
            onClick={() => setMobileDrawerOpen(false)}
            aria-hidden="true"
          />

          {/* Drawer Panel */}
          <div className="relative w-72 max-w-[80vw] bg-[#040F19] border-r border-slate-800 h-full flex flex-col z-50 p-5 shadow-2xl animate-in slide-in-from-left duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <GramaViseLogo size="sm" animated={false} />
              <button
                type="button"
                onClick={() => setMobileDrawerOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                aria-label="Close menu"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-4">
              <Link
                href="/onboarding"
                onClick={() => setMobileDrawerOpen(false)}
                className="w-full bg-[#19D98B] text-[#040F19] font-bold px-4 py-2.5 rounded-xl text-xs flex items-center justify-between"
              >
                <span>{t("nav.newAdvisory")}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <nav className="flex-1 space-y-1.5 overflow-y-auto">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileDrawerOpen(false)}
                    aria-current={item.isActive ? "page" : undefined}
                    className={`flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-semibold transition-colors ${
                      item.isActive
                        ? "text-[#19D98B] bg-[#0E2635] border border-emerald-500/40"
                        : "text-slate-300 hover:bg-[#0E2635]/60 hover:text-white"
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${item.isActive ? "text-[#19D98B]" : "text-slate-400"}`} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            <div className="pt-4 border-t border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Language</span>
                <LanguageToggle isDark />
              </div>
              <p className="text-[10px] text-slate-400 text-center">
                Smart India Hackathon SIH26091
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* RIGHT WORKSPACE AREA: TOPBAR + MAIN CONTENT                  */}
      {/* ============================================================ */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        <Header onOpenMobileMenu={() => setMobileDrawerOpen(true)} />
        <main className="flex-1 min-w-0 bg-[#050E17]">{children}</main>
      </div>
    </div>
  );
};
