"use client";

import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { RiskFactor } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";

interface RiskSectionProps {
  risks: RiskFactor[];
}

export const RiskSection: React.FC<RiskSectionProps> = ({ risks }) => {
  const { t } = useTranslation();

  const severityBadge = (sev: "HIGH" | "MEDIUM" | "LOW") => {
    switch (sev) {
      case "HIGH":
        return <Badge variant="danger">HIGH RISK</Badge>;
      case "MEDIUM":
        return <Badge variant="warning">MODERATE</Badge>;
      case "LOW":
        return <Badge variant="info">LOW RISK</Badge>;
    }
  };

  return (
    <Card>
      <h3 className="text-lg font-bold text-gray-900 mb-4">{t("results.risks.title")}</h3>
      {risks.length === 0 ? (
        <p className="text-sm text-gray-500">{t("results.risks.noCriticalRisks")}</p>
      ) : (
        <div className="space-y-3">
          {risks.map((risk, index) => (
            <div key={index} className="p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-semibold text-gray-800">{risk.factor}</span>
                {severityBadge(risk.severity)}
              </div>
              <p className="text-xs text-gray-600">
                <strong>{t("results.risks.mitigation")}:</strong> {risk.mitigation}
              </p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
