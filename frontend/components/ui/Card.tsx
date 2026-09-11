import React from "react";
import { cn } from "@/lib/utils";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "bordered" | "flat";
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = "default",
  ...props
}) => {
  const variants = {
    default: "bg-white rounded-xl shadow-sm border border-gray-100 p-6",
    bordered: "bg-white rounded-xl border-2 border-gray-200 p-6",
    flat: "bg-gray-50 rounded-xl p-6",
  };

  return (
    <div className={cn(variants[variant], className)} {...props}>
      {children}
    </div>
  );
};
