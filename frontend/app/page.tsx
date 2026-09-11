import Link from "next/link";
import { Button } from "@/components/ui/Button";

export default function HomePage() {
  // TODO [Frontend Lead]: Design hero banner with vernacular prompt selector and quick-demo launch
  return (
    <div className="max-w-5xl mx-auto px-4 py-16 text-center space-y-8">
      <div className="inline-flex items-center gap-2 px-3 py-1 bg-brand-100 text-brand-800 text-xs font-semibold rounded-full">
        <span>Smart India Hackathon 2024 (SIH26091)</span>
      </div>

      <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight">
        Hyper-Local Business Advisory & Financial Structuring for{" "}
        <span className="text-brand-600">Rural Micro-Entrepreneurs</span>
      </h1>

      <p className="max-w-2xl mx-auto text-lg text-gray-600">
        Transform grassroots business ideas into viable, bankable enterprises with deterministic
        financial modeling, local competitor mapping, and government subsidy matching.
      </p>

      <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
        <Link href="/onboarding">
          <Button size="lg" className="w-full sm:w-auto">
            Start Business Assessment →
          </Button>
        </Link>
        <Link href="/schemes">
          <Button variant="outline" size="lg" className="w-full sm:w-auto">
            Explore Government Schemes
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12 text-left">
        <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <h3 className="font-bold text-gray-900 mb-2">1. Localized Market Grounding</h3>
          <p className="text-sm text-gray-600">
            Assesses village cluster demand, footfall, and competitor POIs via OpenStreetMap data.
          </p>
        </div>
        <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <h3 className="font-bold text-gray-900 mb-2">2. Bankable Financial Models</h3>
          <p className="text-sm text-gray-600">
            Calculates exact break-even units, cash flows, EMI schedules, and DSCR coverage.
          </p>
        </div>
        <div className="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <h3 className="font-bold text-gray-900 mb-2">3. Subsidy & Scheme Matching</h3>
          <p className="text-sm text-gray-600">
            Matches profiles with PMEGP, Mudra, PMFME, and credit-linked subsidies.
          </p>
        </div>
      </div>
    </div>
  );
}
