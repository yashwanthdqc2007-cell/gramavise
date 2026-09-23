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
    "inline-flex items-center justify-center font-bold rounded-xl transition-all duration-150 focus:outline-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:ring-offset-[#06131F]";

  const variants = {
    // Primary CTA — GramaVise Emerald #19D98B with crisp dark text #06131F
    primary:
      "bg-[#19D98B] hover:bg-[#16C784] text-[#06131F] font-bold focus-visible:ring-[#19D98B] shadow-md shadow-emerald-500/20 hover:shadow-emerald-500/30 active:scale-[0.99]",
    // Secondary neutral — nested dark surface #0E2635 / #102B3A with subtle border
    secondary:
      "bg-[#0E2635] border border-slate-700/80 text-slate-100 hover:bg-[#102B3A] hover:border-slate-600 focus-visible:ring-[#19D98B] active:scale-[0.99]",
    // Outline — emerald-tinted border with dark inner
    outline:
      "border border-[#19D98B]/60 text-emerald-300 hover:bg-[#19D98B]/10 hover:border-[#19D98B] focus-visible:ring-[#19D98B]",
    // Ghost — transparent with hover surface
    ghost: "text-slate-200 hover:bg-[#0E2635] hover:text-white focus-visible:ring-slate-600",
    // Danger — clear red for destructive actions
    danger:
      "bg-red-600 text-white hover:bg-red-500 focus-visible:ring-red-500 shadow-md shadow-red-600/20 active:scale-[0.99]",
  };

  const sizes = {
    sm: "px-3.5 py-2 text-xs min-h-[38px] sm:min-h-[36px]",
    md: "px-4 py-2.5 text-sm min-h-[44px]",
    lg: "px-6 py-3.5 text-base min-h-[48px]",
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


