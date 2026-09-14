"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslation } from "@/lib/i18n";
import { Sprout } from "lucide-react";

export const Footer: React.FC = () => {
  const { t } = useTranslation();
  const pathname = usePathname();
  const isLanding = pathname === "/";

  return (
    <footer className="py-12 transition-colors duration-200 text-xs bg-[#050E17] border-t border-slate-800/80 text-slate-400 mt-0">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pb-8 border-b border-slate-800/70">
          <div className="text-center sm:text-left space-y-1.5">
            <div className="flex items-center justify-center sm:justify-start space-x-2">
              <div className="w-6 h-6 rounded-lg bg-emerald-500 text-slate-950 flex items-center justify-center font-bold">
                <Sprout className="w-3.5 h-3.5" />
              </div>
              <span className="text-base font-extrabold tracking-tight text-white">
                GramaVise
              </span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase text-slate-400 bg-slate-800/80 border border-slate-700/60">
                {t("nav.hackathonBadge")}
              </span>
            </div>
            <p className="font-medium text-xs text-slate-300">
              {t("common.motto")}
            </p>
          </div>

          <nav aria-label="Footer Navigation" className="flex items-center space-x-6 text-xs font-medium text-slate-300">
            <Link href="/onboarding" className="transition-colors hover:text-emerald-400">
              {t("nav.newAdvisory")}
            </Link>
            <Link href="/schemes" className="transition-colors hover:text-emerald-400">
              {t("nav.schemesDirectory")}
            </Link>
            <Link href="/history" className="transition-colors hover:text-emerald-400">
              {t("nav.history")}
            </Link>
          </nav>
        </div>

        <div className="pt-6 text-center text-[11px] space-y-1 text-slate-500">
          <p>{t("common.footerText")}</p>
          <p>{t("common.disclaimerText")}</p>
        </div>
      </div>
    </footer>
  );
};
