"use client";

import React from "react";
import Link from "next/link";
import { LanguageToggle } from "@/components/common/LanguageToggle";

export const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-2xl font-black text-brand-700 tracking-tight">GramaVise</span>
          <span className="text-[10px] bg-brand-100 text-brand-800 font-bold px-1.5 py-0.5 rounded uppercase">
            SIH26091
          </span>
        </Link>
        <div className="flex items-center space-x-4">
          <nav className="hidden md:flex space-x-6 text-sm font-medium text-gray-600">
            <Link href="/onboarding" className="hover:text-brand-600 transition-colors">
              New Advisory
            </Link>
            <Link href="/schemes" className="hover:text-brand-600 transition-colors">
              Schemes Directory
            </Link>
          </nav>
          <LanguageToggle />
        </div>
      </div>
    </header>
  );
};
