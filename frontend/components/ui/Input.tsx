import React, { useId } from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  rightElement?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  rightElement,
  className,
  id,
  required,
  ...props
}) => {
  const generatedId = useId();
  const inputId = id || generatedId;
  const errorId = error ? `${inputId}-error` : undefined;
  const helperId = helperText ? `${inputId}-helper` : undefined;

  const describedBy = [errorId, helperId].filter(Boolean).join(" ") || undefined;

  return (
    <div className="w-full space-y-1.5">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-slate-200">
          {label}
          {required && <span className="text-red-400 ml-1" aria-hidden="true">*</span>}
        </label>
      )}
      <div className={rightElement ? "flex items-center gap-2" : undefined}>
        <input
          id={inputId}
          required={required}
          aria-required={required ? "true" : undefined}
          aria-invalid={Boolean(error)}
          aria-describedby={describedBy}
          className={cn(
            "w-full px-3.5 py-2.5 border rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-[#19D98B] focus:border-[#19D98B] text-white text-sm bg-[#102B3A] placeholder:text-slate-500 transition-colors min-h-[44px]",
            error
              ? "border-red-500 focus:ring-red-500 focus:border-red-500"
              : "border-slate-700/80 hover:border-slate-600",
            className
          )}
          {...props}
        />
        {rightElement}
      </div>
      {error && (
        <p id={errorId} className="text-xs text-red-400 mt-1 flex items-center gap-1" role="alert">
          <span>⚠</span> {error}
        </p>
      )}
      {helperText && !error && (
        <p id={helperId} className="text-xs text-slate-400 mt-1">
          {helperText}
        </p>
      )}
    </div>
  );
};



