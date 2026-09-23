"use client";

import React from "react";
import Link from "next/link";
import { useTranslation } from "@/lib/i18n";
import { GramaViseLogo } from "@/components/common/GramaViseLogo";

export const Footer: React.FC = () => {
  const { t } = useTranslation();

  return (
    <footer className="py-12 transition-colors duration-200 text-xs bg-[#06131F] border-t border-slate-800/80 text-slate-400 mt-0">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pb-8 border-b border-slate-800/80">
          <div className="text-center sm:text-left space-y-1.5">
            <div className="flex items-center justify-center sm:justify-start space-x-2.5">
              <GramaViseLogo size="sm" animated={false} />
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase text-slate-400 bg-[#0E2635] border border-slate-700/60">
                {t("nav.hackathonBadge")}
              </span>
            </div>
            <p className="font-medium text-xs text-slate-300">
              {t("common.motto")}
            </p>
          </div>

          <nav aria-label="Footer Navigation" className="flex flex-wrap justify-center sm:justify-start items-center gap-6 text-xs font-semibold text-slate-300">
            <Link href="/" className="transition-colors hover:text-[#19D98B]">
              Home
            </Link>
            <Link href="/onboarding" className="transition-colors hover:text-[#19D98B]">
              {t("nav.newAdvisory")}
            </Link>
            <Link href="/schemes" className="transition-colors hover:text-[#19D98B]">
              {t("nav.schemesDirectory")}
            </Link>
            <Link href="/history" className="transition-colors hover:text-[#19D98B]">
              {t("nav.history")}
            </Link>
          </nav>
        </div>

        <div className="pt-6 text-center text-[11px] space-y-1.5 text-slate-500">
          <p>{t("common.footerText")}</p>
          <p className="max-w-2xl mx-auto leading-relaxed">{t("common.disclaimerText")}</p>
        </div>
      </div>
    </footer>
  );
};

