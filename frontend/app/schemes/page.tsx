"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { fetchSchemes, SchemeInfo } from "@/services/api/schemes";
import { formatCurrencyINR } from "@/lib/utils";

const sampleSchemes: SchemeInfo[] = [
  {
    scheme_code: "PMEGP",
    scheme_name: "Prime Minister Employment Generation Programme",
    ministry_or_dept: "Ministry of MSME",
    max_loan_amount: 5000000,
    subsidy_percentage_general: 25,
    subsidy_percentage_special: 35,
    official_portal_url: "https://www.kviconline.gov.in/pmegpeportal",
  },
  {
    scheme_code: "MUDRA_KISHORE",
    scheme_name: "Pradhan Mantri MUDRA Yojana (Kishore)",
    ministry_or_dept: "Ministry of Finance",
    max_loan_amount: 500000,
    subsidy_percentage_general: 0,
    subsidy_percentage_special: 0,
    official_portal_url: "https://www.mudra.org.in",
  },
  {
    scheme_code: "PMFME",
    scheme_name: "PM Formalisation of Micro Food Processing Enterprises",
    ministry_or_dept: "Ministry of Food Processing Industries",
    max_loan_amount: 1000000,
    subsidy_percentage_general: 35,
    subsidy_percentage_special: 35,
    official_portal_url: "https://pmfme.mofpi.gov.in",
  },
];

export default function SchemesDirectoryPage() {
  const [schemes, setSchemes] = useState<SchemeInfo[]>(sampleSchemes);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // TODO [Frontend Lead]: Fetch dynamic list from /api/schemes
    fetchSchemes()
      .then((data) => {
        if (data && data.length > 0) setSchemes(data);
      })
      .catch((err) => console.log("Using static scheme list preview", err));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Government Credit & Subsidy Directory</h2>
          <p className="text-sm text-gray-500">
            Explore active credit schemes, margin subsidy percentages, and official application links.
          </p>
        </div>
        <Link href="/onboarding">
          <Button size="sm">Check My Business Eligibility →</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {schemes.map((scheme) => (
          <Card key={scheme.scheme_code} className="flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start mb-2">
                <Badge variant="info">{scheme.scheme_code}</Badge>
                <span className="text-xs text-gray-500">{scheme.ministry_or_dept}</span>
              </div>
              <h3 className="font-bold text-base text-gray-900 mb-2">{scheme.scheme_name}</h3>
              <div className="space-y-1 text-xs text-gray-600 mb-4">
                <div>
                  <strong>Max Loan:</strong> {formatCurrencyINR(scheme.max_loan_amount)}
                </div>
                <div>
                  <strong>Subsidy (General / Special):</strong> {scheme.subsidy_percentage_general}% / {scheme.subsidy_percentage_special}%
                </div>
              </div>
            </div>
            {scheme.official_portal_url && (
              <a
                href={scheme.official_portal_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-brand-600 hover:text-brand-800 font-semibold underline pt-2 border-t border-gray-100 block"
              >
                Visit Official Portal ↗
              </a>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
