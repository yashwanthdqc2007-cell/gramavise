"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, PlusCircle, ArrowRight } from "lucide-react";
import { LanguageToggle } from "@/components/common/LanguageToggle";
import { useTranslation } from "@/lib/i18n";
import { NetworkStatusBar } from "@/components/common/NetworkStatusBar";
import { GramaViseIcon } from "@/components/common/GramaViseLogo";

interface HeaderProps {
  onOpenMobileMenu?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenMobileMenu }) => {
  const { t } = useTranslation();
  const pathname = usePathname();

  const getPageInfo = () => {
    if (pathname === "/") {
      return {
        title: t("nav.dashboard") || "Dashboard",
        subtitle: "Hyper-Local Feasibility & Financial Structuring Workspace",
      };
    }
    if (pathname === "/onboarding") {
      return {
        title: t("onboarding.pageTitle") || "New Advisory Assessment",
        subtitle: "Step-by-step business feasibility & loan sizing",
      };
    }
    if (pathname === "/schemes") {
      return {
        title: t("nav.schemesDirectory") || "Schemes Directory",
        subtitle: "Government-supported financial & credit subsidy programs",
      };
    }
    if (pathname === "/history") {
      return {
        title: t("nav.history") || "My Reports & History",
        subtitle: "Saved business assessments and deterministic decision traces",
      };
    }
    if (pathname.startsWith("/history/")) {
      return {
        title: "Feasibility Advisory Report",
        subtitle: "Detailed business breakdown, sensitivity analysis & action plan",
      };
    }
    if (pathname === "/help") {
      return {
        title: t("nav.help") || "Help & Guidance",
        subtitle: "Advisory definitions, financial principles & verification checklists",
      };
    }
    if (pathname === "/settings") {
      return {
        title: t("nav.settings") || "Settings",
        subtitle: "Application preferences and local device storage management",
      };
    }
    if (pathname === "/results") {
      return {
        title: "Feasibility Advisory Report",
        subtitle: "Live analysis results and interactive scenario simulator",
      };
    }
    return {
      title: "GramaVise",
      subtitle: "Rural Micro-Enterprise Advisory Platform",
    };
  };

  const pageInfo = getPageInfo();

  return (
    <header className="sticky top-0 z-30 bg-[#06131F]/90 backdrop-blur-md border-b border-slate-800/80 text-white transition-colors duration-200">
      <NetworkStatusBar />
      <div className="px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Mobile hamburger + Page Title / Breadcrumb */}
        <div className="flex items-center gap-3 min-w-0">
          {/* Mobile hamburger button */}
          <button
            type="button"
            onClick={onOpenMobileMenu}
            className="lg:hidden p-2 rounded-xl border border-slate-700/80 bg-[#0E2635] text-slate-200 hover:text-white hover:bg-[#102B3A] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#19D98B] min-h-[40px] min-w-[40px] flex items-center justify-center transition-colors shrink-0"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5 text-white" aria-hidden="true" />
          </button>

          {/* Mobile brand (shown only on small screens next to menu) */}
          <div className="flex lg:hidden items-center gap-2 shrink-0">
            <GramaViseIcon size={28} />
          </div>

          {/* Page Context Title */}
          <div className="flex flex-col min-w-0">
            <h1 className="text-sm sm:text-base font-bold text-white tracking-tight truncate leading-snug">
              {pageInfo.title}
            </h1>
            <p className="hidden md:block text-[11px] text-slate-400 truncate leading-none mt-0.5">
              {pageInfo.subtitle}
            </p>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="hidden sm:block">
            <LanguageToggle isDark />
          </div>

          {pathname !== "/onboarding" && (
            <Link href="/onboarding" className="hidden lg:block">
              <button
                type="button"
                className="bg-[#19D98B] hover:bg-[#16C784] text-[#06131F] font-bold px-3 sm:px-4 py-2 rounded-xl text-xs shadow-sm shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all inline-flex items-center gap-1.5 active:scale-[0.98] min-h-[36px]"
              >
                <PlusCircle className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{t("nav.newAdvisory")}</span>
                <span className="sm:hidden">New</span>
              </button>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
