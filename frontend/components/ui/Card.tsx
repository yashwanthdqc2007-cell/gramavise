import React from "react";
import { cn } from "@/lib/utils";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "bordered" | "flat" | "compact";
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = "default",
  ...props
}) => {
  const variants = {
    default: "bg-slate-900/80 rounded-2xl shadow-lg shadow-slate-950/30 border border-slate-800 p-6",
    bordered: "bg-slate-900/80 rounded-2xl border-2 border-slate-700 p-6",
    flat: "bg-slate-900/60 rounded-2xl p-6 border border-slate-800",
    compact: "bg-slate-900/80 rounded-2xl shadow-lg shadow-slate-950/30 border border-slate-800 p-4",
  };

  return (
    <div className={cn(variants[variant], className)} {...props}>
      {children}
    </div>
  );
};
