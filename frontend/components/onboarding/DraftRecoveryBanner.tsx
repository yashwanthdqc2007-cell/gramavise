"use client";

import React, { useState } from "react";
import { OnboardingDraft } from "@/lib/storage/draftStorage";
import { useTranslation } from "@/lib/i18n";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FileText, Trash2, ArrowRight, AlertTriangle } from "lucide-react";

interface DraftRecoveryBannerProps {
  draft: OnboardingDraft;
  onContinue: (draft: OnboardingDraft) => void;
  onStartFresh: () => void;
}

export const DraftRecoveryBanner: React.FC<DraftRecoveryBannerProps> = ({
  draft,
  onContinue,
  onStartFresh,
}) => {
  const { t } = useTranslation();
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const formattedTime = new Date(draft.updated_at).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });

  const bannerText = t("draft.bannerDesc").replace("{time}", formattedTime);

  return (
    <>
      <div
        role="region"
        aria-label={t("draft.bannerTitle")}
        className="mb-4 bg-gradient-to-r from-emerald-950/60 via-[#0B1C29] to-cyan-950/40 border border-emerald-500/30 rounded-xl p-3 sm:p-4 shadow-lg shadow-slate-950/20"
      >
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/15 text-emerald-300 border border-emerald-500/25 flex items-center justify-center flex-shrink-0 mt-0.5">
              <FileText className="w-4 h-4" aria-hidden="true" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                {t("draft.bannerTitle")}
                <span className="text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/25 px-2 py-0.5 rounded">
                  Step {draft.step} of 5
                </span>
              </h3>
              <p className="text-xs sm:text-sm text-slate-300 mt-0.5">{bannerText}</p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowConfirmModal(true)}
              className="text-slate-300 hover:text-rose-300 hover:border-rose-500/40 flex items-center gap-1.5 min-h-[44px] sm:min-h-0"
            >
              <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
              <span>{t("draft.startFreshCta")}</span>
            </Button>
            <Button
              size="sm"
              onClick={() => onContinue(draft)}
              className="flex items-center gap-1.5 min-h-[44px] sm:min-h-0 font-semibold"
            >
              <span>{t("draft.continueCta")}</span>
              <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
            </Button>
          </div>
        </div>
      </div>

      {/* Confirmation Modal to Start Fresh */}
      {showConfirmModal && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="clear-draft-title"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
        >
          <Card className="max-w-md w-full p-6 space-y-4 shadow-xl border border-slate-700 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/30 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-5 h-5" aria-hidden="true" />
              </div>
              <div>
                <h3 id="clear-draft-title" className="text-base font-bold text-white">
                  {t("draft.clearConfirmTitle")}
                </h3>
                <p className="text-xs sm:text-sm text-slate-300 mt-1">
                  {t("draft.clearConfirmDesc")}
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowConfirmModal(false)}
                className="min-h-[44px]"
              >
                {t("draft.clearConfirmNo")}
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  setShowConfirmModal(false);
                  onStartFresh();
                }}
                className="min-h-[44px]"
              >
                {t("draft.clearConfirmYes")}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </>
  );
};
