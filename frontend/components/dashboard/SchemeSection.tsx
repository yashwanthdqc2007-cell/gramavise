"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { SchemeResult } from "@/lib/types";
import { formatCurrencyINR } from "@/lib/utils";

interface SchemeSectionProps {
  schemeResult: SchemeResult;
}

export const SchemeSection: React.FC<SchemeSectionProps> = ({ schemeResult }) => {
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Government Credit & Subsidy Matcher</h3>
        <span className="text-xs text-brand-700 font-semibold bg-brand-50 px-2.5 py-1 rounded-full">
          Total Potential Subsidy: {formatCurrencyINR(schemeResult.total_potential_subsidy)}
        </span>
      </div>
      <div className="space-y-4">
        {schemeResult.schemes.map((scheme) => (
          <div key={scheme.scheme_code} className="p-4 border border-gray-200 rounded-xl">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-semibold text-gray-900">{scheme.scheme_name}</h4>
                <p className="text-xs text-gray-500">Scheme Code: {scheme.scheme_code}</p>
              </div>
              <Badge variant="success">{scheme.eligibility_status}</Badge>
            </div>
            <div className="grid grid-cols-2 gap-2 my-3 text-xs bg-gray-50 p-2.5 rounded-lg">
              <div>
                <span className="text-gray-500">Subsidy Eligible:</span>{" "}
                <span className="font-bold text-brand-700">{formatCurrencyINR(scheme.subsidy_eligible_amount)}</span>
              </div>
              <div>
                <span className="text-gray-500">Own Margin Money:</span>{" "}
                <span className="font-bold text-gray-700">{formatCurrencyINR(scheme.own_contribution_required)}</span>
              </div>
            </div>
            {scheme.portal_url && (
              <a
                href={scheme.portal_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-brand-600 hover:text-brand-800 font-medium underline"
              >
                Official Application Portal →
              </a>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
};
