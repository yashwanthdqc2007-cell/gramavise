import React from "react";

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Evaluating business feasibility and structuring financial metrics...",
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-4">
      <div className="w-10 h-10 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
      <p className="text-sm font-medium text-gray-600 animate-pulse">{message}</p>
    </div>
  );
};
