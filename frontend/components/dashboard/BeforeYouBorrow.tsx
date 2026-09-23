"use client";

import React, { useState } from "react";
import { VerificationCheckItem } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { ClipboardCheck, CheckSquare, Square } from "lucide-react";

interface BeforeYouBorrowProps {
  checklist: VerificationCheckItem[];
}

export const BeforeYouBorrow: React.FC<BeforeYouBorrowProps> = ({ checklist = [] }) => {
  const { t } = useTranslation();
  const [completedItems, setCompletedItems] = useState<Record<string, boolean>>({});

  if (checklist.length === 0) return null;

  const toggleItem = (id: string) => {
    setCompletedItems((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const highPriorityItems = checklist.filter(
    (item) =>
      item.category === "MARKET" ||
      item.category === "PRICING" ||
      item.action_type === "ON_GROUND_SURVEY"
  );
  const otherItems = checklist.filter(
    (item) => !highPriorityItems.some((h) => h.item_id === item.item_id)
  );

  const finalHighPriority = highPriorityItems.length > 0 ? highPriorityItems : checklist.slice(0, 3);
  const finalOther = highPriorityItems.length > 0 ? otherItems : checklist.slice(3);

  const completedCount = Object.values(completedItems).filter(Boolean).length;

  const renderChecklistRow = (item: VerificationCheckItem) => {
    const isDone = !!completedItems[item.item_id];
    return (
      <div
        key={item.item_id}
        onClick={() => toggleItem(item.item_id)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            toggleItem(item.item_id);
          }
        }}
        tabIndex={0}
        role="checkbox"
        aria-checked={isDone}
        className={`p-3.5 rounded-xl border text-xs cursor-pointer select-none transition-all flex items-start gap-3.5 ${
          isDone
            ? "bg-[#06131F] border-slate-800 text-slate-600 opacity-60"
            : "bg-[#0E2635] border-slate-700/60 hover:border-emerald-500/40 hover:bg-[#102B3A]"
        }`}
      >
        <button
          type="button"
          tabIndex={-1}
          aria-hidden="true"
          className="mt-0.5 text-slate-600 hover:text-emerald-400 focus:outline-none"
        >
          {isDone ? (
            <CheckSquare className="w-4 h-4 text-emerald-500 shrink-0" />
          ) : (
            <Square className="w-4 h-4 text-slate-600 shrink-0" />
          )}
        </button>

        <div className="space-y-1 flex-1">
          <div className="flex flex-wrap items-center justify-between gap-1.5">
            <span className={`font-bold text-sm ${isDone ? "line-through text-slate-600" : "text-white"}`}>
              {item.title}
            </span>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
              {item.category}
            </span>
          </div>
          <p className={`text-xs leading-relaxed ${isDone ? "line-through text-slate-600" : "text-slate-400"}`}>
            {item.description}
          </p>
        </div>
      </div>
    );
  };

  return (
    <section className="bg-[#0B1F2D] rounded-2xl border border-slate-800/80 p-6 md:p-7 shadow-xl shadow-slate-950/20 space-y-6" id="before-you-borrow">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <ClipboardCheck className="w-5 h-5 text-amber-400" aria-hidden="true" />
            <h2 className="text-xl font-black text-white tracking-tight">
              {t("results.beforeYouBorrow.title")}
            </h2>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            {t("results.beforeYouBorrow.subtitle")}
          </p>
        </div>

        {/* Progress pill */}
        <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700 self-start sm:self-auto">
          {completedCount} / {checklist.length} {t("results.beforeYouBorrow.completedCount")}
        </span>
      </div>

      {/* High Priority Group */}
      {finalHighPriority.length > 0 && (
        <div className="space-y-2.5">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-500" aria-hidden="true" />
            <h3 className="text-xs font-bold text-amber-400 tracking-wider uppercase">
              {t("results.beforeYouBorrow.highPriority")}
            </h3>
          </div>
          <div className="space-y-2">
            {finalHighPriority.map(renderChecklistRow)}
          </div>
        </div>
      )}

      {/* Other Checks Group */}
      {finalOther.length > 0 && (
        <div className="space-y-2.5 pt-2 border-t border-slate-800">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-slate-600" aria-hidden="true" />
            <h3 className="text-xs font-bold text-slate-500 tracking-wider uppercase">
              {t("results.beforeYouBorrow.otherChecks")}
            </h3>
          </div>
          <div className="space-y-2">
            {finalOther.map(renderChecklistRow)}
          </div>
        </div>
      )}
    </section>
  );
};
