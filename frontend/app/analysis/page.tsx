import Link from "next/link";
import { Button } from "@/components/ui/Button";

export default function AnalysisPage() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-4">
      <h2 className="text-2xl font-bold text-gray-900">Analysis Overview</h2>
      <p className="text-sm text-gray-600">
        To start an evaluation, please complete the onboarding questionnaire.
      </p>
      <Link href="/onboarding">
        <Button>Go to Onboarding Wizard →</Button>
      </Link>
    </div>
  );
}
