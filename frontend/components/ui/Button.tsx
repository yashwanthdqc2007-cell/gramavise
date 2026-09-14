import React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = "primary",
  size = "md",
  disabled,
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center font-medium rounded-xl transition-colors focus:outline-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:ring-offset-[#050E17]";

  const variants = {
    // Primary CTA — emerald (success/proceed action)
    primary: "bg-emerald-500 text-slate-950 hover:bg-emerald-400 focus-visible:ring-emerald-400 shadow-lg shadow-emerald-500/20",
    // Secondary neutral — dark surface with subtle borders 
    secondary: "bg-slate-800 border border-slate-700 text-slate-100 hover:bg-slate-700 focus-visible:ring-emerald-500",
    // Outline — emerald bordered (secondary CTA with brand presence)
    outline: "border border-emerald-500/70 text-emerald-300 hover:bg-emerald-500/10 focus-visible:ring-emerald-500",
    // Ghost — low-priority actions
    ghost: "text-slate-200 hover:bg-slate-800 focus-visible:ring-slate-600",
    // Danger — red (destructive/irreversible actions only)
    danger: "bg-red-500 text-white hover:bg-red-400 focus-visible:ring-red-500",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm min-h-[36px]",
    md: "px-4 py-2 text-base min-h-[44px]",
    lg: "px-6 py-3 text-lg min-h-[48px]",
  };

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      disabled={disabled}
      aria-disabled={disabled ? "true" : undefined}
      {...props}
    >
      {children}
    </button>
  );
};

