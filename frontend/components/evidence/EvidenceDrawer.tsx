"use client";

import React, { useState } from "react";
import { EvidenceItem } from "@/lib/types";
import { EvidenceBadge } from "@/components/evidence/EvidenceBadge";
import { Card } from "@/components/ui/Card";

interface EvidenceDrawerProps {
  evidenceList: EvidenceItem[];
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ evidenceList }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Card className="border border-blue-100 bg-blue-50/30">
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div>
          <h4 className="text-sm font-bold text-gray-900">
            Audit Trail & Evidence Classification ({evidenceList.length} items)
          </h4>
          <p className="text-xs text-gray-500">
            Every insight is verified through mathematical, observed, or assumed data sources.
          </p>
        </div>
        <span className="text-xs text-blue-700 font-semibold underline">
          {isOpen ? "Hide Audit Trail ▲" : "View Audit Trail ▼"}
        </span>
      </div>

      {isOpen && (
        <div className="mt-4 pt-4 border-t border-blue-100 space-y-3">
          {evidenceList.map((item, idx) => (
            <div key={idx} className="p-2.5 bg-white rounded-lg border border-gray-100 text-xs">
              <div className="flex justify-between items-start mb-1">
                <span className="font-semibold text-gray-800">{item.indicator}</span>
                <EvidenceBadge type={item.evidence_type} confidence={item.confidence} />
              </div>
              <div className="text-gray-600 font-medium">{item.value}</div>
              {item.notes && <div className="text-gray-500 mt-1 italic">{item.notes}</div>}
              {item.source && (
                <div className="text-[10px] text-gray-400 mt-1">Source: {item.source}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
