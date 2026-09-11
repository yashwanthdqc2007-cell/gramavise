"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { AIExplanation } from "@/lib/types";

interface RecommendationCardProps {
  explanation?: AIExplanation;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ explanation }) => {
  if (!explanation) return null;

  return (
    <Card className="bg-gradient-to-br from-brand-50 to-emerald-50 border-brand-200">
      <h3 className="text-lg font-bold text-gray-900 mb-2">AI Explainable Advisory & Guidance</h3>
      <p className="text-sm text-gray-800 mb-4">{explanation.summary}</p>
      
      <div className="space-y-3">
        {explanation.actionable_next_steps.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
              Actionable Next Steps
            </h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
              {explanation.actionable_next_steps.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <p className="text-[11px] text-gray-500 italic mt-4 pt-3 border-t border-brand-200/50">
        {explanation.disclaimer}
      </p>
    </Card>
  );
};
