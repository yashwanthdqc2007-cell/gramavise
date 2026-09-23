import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "success" | "warning" | "danger" | "info" | "neutral" | "calculated" | "modelled";
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  className,
  variant = "neutral",
  ...props
}) => {
  const variants = {
    success: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
    warning: "bg-amber-500/15 text-amber-300 border-amber-500/30",
    danger: "bg-rose-500/15 text-rose-300 border-rose-500/30",
    info: "bg-sky-500/15 text-sky-300 border-sky-500/30",
    neutral: "bg-[#0E2635] text-slate-200 border-slate-700/80",
    calculated: "bg-teal-500/15 text-teal-300 border-teal-500/30",
    modelled: "bg-indigo-500/15 text-indigo-300 border-indigo-500/30",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

