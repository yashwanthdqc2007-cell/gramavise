import React from "react";
import { Button } from "@/components/ui/Button";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Analysis Error",
  message,
  onRetry,
}) => {
  return (
    <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-center space-y-3">
      <h3 className="text-base font-bold text-red-800">{title}</h3>
      <p className="text-sm text-red-600">{message}</p>
      {onRetry && (
        <Button variant="danger" size="sm" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  );
};
