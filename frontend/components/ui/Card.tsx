import React from "react";
import { cn } from "@/lib/utils";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "bordered" | "flat" | "compact" | "nested";
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = "default",
  ...props
}) => {
  const variants = {
    default: "bg-[#0B1F2D] rounded-2xl shadow-xl shadow-slate-950/20 border border-slate-800/80 p-6 text-slate-100",
    bordered: "bg-[#0B1F2D] rounded-2xl border-2 border-slate-700/80 p-6 text-slate-100",
    flat: "bg-[#0E2635] rounded-2xl p-6 border border-slate-800/80 text-slate-100",
    nested: "bg-[#0E2635] rounded-xl p-5 border border-slate-700/60 text-slate-100",
    compact: "bg-[#0B1F2D] rounded-2xl shadow-lg shadow-slate-950/20 border border-slate-800/80 p-4 text-slate-100",
  };

  return (
    <div className={cn(variants[variant], className)} {...props}>
      {children}
    </div>
  );
};

