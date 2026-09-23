"use client";

import React from "react";

export interface GramaViseLogoProps {
  variant?: "full" | "icon" | "stacked";
  theme?: "dark" | "light";
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  showTagline?: boolean;
  animated?: boolean;
}

/**
 * GramaVise Geometric Icon Mark (Clean Vector)
 * Subtly synthesizes:
 * 1. Community / Grama Hexagonal Foundation
 * 2. Precision Advisory "G" Arc
 * 3. Dynamic "V" Ascending Decision & Growth Vector (Checkmark & Upward Trend)
 * 4. Hyper-Local Data Apex Node in Cyan (#27C7D9)
 */
export const GramaViseIcon: React.FC<{
  size?: number | string;
  className?: string;
  theme?: "dark" | "light";
}> = ({ size = 32, className = "", theme = "dark" }) => {
  const isDark = theme === "dark";

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 36 36"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`shrink-0 transition-transform duration-200 ${className}`}
      aria-hidden="true"
    >
      <defs>
        <linearGradient
          id={`gv_emerald_grad_${theme}`}
          x1="4"
          y1="4"
          x2="32"
          y2="32"
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0%" stopColor={isDark ? "#27C7D9" : "#0284C7"} />
          <stop offset="50%" stopColor={isDark ? "#19D98B" : "#059669"} />
          <stop offset="100%" stopColor={isDark ? "#0E9F6E" : "#047857"} />
        </linearGradient>
        {isDark && (
          <filter
            id="gv_subtle_glow"
            x="-10%"
            y="-10%"
            width="120%"
            height="125%"
            filterUnits="userSpaceOnUse"
          >
            <feDropShadow
              dx="0"
              dy="1.5"
              stdDeviation="2"
              floodColor="#19D98B"
              floodOpacity="0.3"
            />
          </filter>
        )}
      </defs>

      {/* Hexagonal Community Foundation */}
      <path
        d="M18 3L31 10.5V25.5L18 33L5 25.5V10.5L18 3Z"
        fill={isDark ? "#081B27" : "#F0FDF4"}
        stroke={`url(#gv_emerald_grad_${theme})`}
        strokeWidth="1.75"
        strokeLinejoin="round"
      />

      {/* Inner Geometric "G" Community Arch */}
      <path
        d="M12 14.5C12 11.5 14.5 9 18 9C21 9 23.5 10.8 24.5 13.5"
        stroke={isDark ? "#27C7D9" : "#0284C7"}
        strokeWidth="2"
        strokeLinecap="round"
      />

      {/* Dynamic Ascending "V" Decision Vector */}
      <path
        d="M11 19.5L16.5 25L25.5 12"
        stroke={isDark ? "#19D98B" : "#059669"}
        strokeWidth="2.75"
        strokeLinecap="round"
        strokeLinejoin="round"
        filter={isDark ? "url(#gv_subtle_glow)" : undefined}
      />

      {/* Hyper-Local Intelligence Apex Node */}
      <circle
        cx="25.5"
        cy="12"
        r="2.25"
        fill={isDark ? "#27C7D9" : "#0284C7"}
      />
      <circle cx="25.5" cy="12" r="1" fill="#FFFFFF" />
      <circle
        cx="11"
        cy="19.5"
        r="1.5"
        fill={isDark ? "#19D98B" : "#059669"}
      />
    </svg>
  );
};

export const GramaViseLogo: React.FC<GramaViseLogoProps> = ({
  variant = "full",
  theme = "dark",
  size = "md",
  className = "",
  showTagline = false,
  animated = true,
}) => {
  const isDark = theme === "dark";

  const sizeConfig = {
    sm: { icon: 24, text: "text-base", badge: "text-[9px]" },
    md: { icon: 32, text: "text-xl", badge: "text-[10px]" },
    lg: { icon: 40, text: "text-2xl", badge: "text-xs" },
    xl: { icon: 48, text: "text-3xl", badge: "text-xs" },
  }[size];

  if (variant === "icon") {
    return (
      <div
        className={`inline-flex items-center justify-center ${className}`}
        aria-label="GramaVise Icon"
      >
        <GramaViseIcon size={sizeConfig.icon} theme={theme} />
      </div>
    );
  }

  if (variant === "stacked") {
    return (
      <div
        className={`flex flex-col items-center gap-2 ${className}`}
        aria-label="GramaVise Logo"
      >
        <GramaViseIcon size={sizeConfig.icon} theme={theme} />
        <div className="flex flex-col items-center text-center">
          <span
            className={`${sizeConfig.text} font-black tracking-tight tracking-[-0.03em] ${
              isDark ? "text-white" : "text-[#06131F]"
            }`}
          >
            GRAMA<span className="text-[#19D98B]">VISE</span>
          </span>
          {showTagline && (
            <span
              className={`text-[11px] font-medium mt-0.5 ${
                isDark ? "text-slate-400" : "text-slate-600"
              }`}
            >
              Decide before you borrow
            </span>
          )}
        </div>
      </div>
    );
  }

  // Default: Horizontal Full Logo (Icon + Wordmark)
  return (
    <div
      className={`inline-flex items-center gap-3 ${
        animated ? "group" : ""
      } select-none ${className}`}
      aria-label="GramaVise"
    >
      <div
        className={`flex items-center justify-center ${
          animated
            ? "group-hover:scale-105 group-hover:-translate-y-0.5 transition-transform duration-200"
            : ""
        }`}
      >
        <GramaViseIcon size={sizeConfig.icon} theme={theme} />
      </div>

      <div className="flex flex-col min-w-0">
        <span
          className={`${sizeConfig.text} font-black tracking-tight tracking-[-0.03em] leading-tight ${
            isDark ? "text-white" : "text-[#06131F]"
          }`}
        >
          GRAMA<span className="text-[#19D98B]">VISE</span>
        </span>
        {showTagline && (
          <span
            className={`text-[10px] font-semibold tracking-tight ${
              isDark ? "text-slate-400" : "text-slate-500"
            } leading-none mt-0.5`}
          >
            Decide before you borrow
          </span>
        )}
      </div>
    </div>
  );
};
