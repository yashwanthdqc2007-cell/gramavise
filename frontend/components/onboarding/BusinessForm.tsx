"use client";

import React from "react";
import { Input } from "@/components/ui/Input";
import { POPULAR_BUSINESS_CATEGORIES } from "@/lib/constants";

interface BusinessFormProps {
  businessName: string;
  category: string;
  description?: string;
  isNewBusiness: boolean;
  onChange: (fields: Record<string, any>) => void;
}

export const BusinessForm: React.FC<BusinessFormProps> = ({
  businessName,
  category,
  description,
  isNewBusiness,
  onChange,
}) => {
  // TODO [Frontend Lead]: Add category-specific benchmark suggestions
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Business Concept</h3>
      <Input
        label="Business Name"
        placeholder="e.g. Kisan Flour Mill & Spices"
        value={businessName}
        onChange={(e) => onChange({ business_name: e.target.value })}
      />
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Business Category</label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
          value={category}
          onChange={(e) => onChange({ category: e.target.value })}
        >
          <option value="">Select a category...</option>
          {POPULAR_BUSINESS_CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Brief Description (Optional)</label>
        <textarea
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
          placeholder="Briefly describe products, target customers, and operations..."
          value={description || ""}
          onChange={(e) => onChange({ description: e.target.value })}
        />
      </div>
    </div>
  );
};
