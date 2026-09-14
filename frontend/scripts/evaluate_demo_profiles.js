/**
 * Evaluates the 4 demo profiles against the live backend API
 * and outputs exact real deterministic results.
 */

const http = require("http");

const PROFILES = [
  {
    id: "kisan_flour_mill",
    name: "Kisan Flour Mill",
    payload: {
      profile: {
        business_name: "Kisan Flour Mill",
        category: "Flour & Spice Milling (Atta Chakki)",
        description: "Modern grain milling, whole-wheat atta processing, and packaged retail spice supply for village grocery stores.",
        location: {
          state: "Maharashtra",
          district: "Pune",
          village: "Baramati",
        },
        experience_years: 5,
        own_capital: 150000,
        desired_loan: 150000,
        is_new_business: true,
      },
      financials: {
        startup_cost: 50000,
        equipment_cost: 200000,
        inventory_cost: 50000,
        monthly_fixed_cost: 20000,
        customers_per_day: 35,
        avg_ticket_price: 500,
        working_days_per_month: 26,
        variable_cost_pct: 45,
        interest_rate_pct: 10.5,
        loan_tenure_months: 60,
      },
    },
  },
  {
    id: "lakshmi_tailoring",
    name: "Lakshmi Tailoring Centre",
    payload: {
      profile: {
        business_name: "Lakshmi Tailoring Centre",
        category: "Tailoring & Garment Making",
        description: "Custom ladies and children garment stitching, school uniform contracts, and embroidery alteration services.",
        location: {
          state: "Tamil Nadu",
          district: "Madurai",
          village: "Melur",
        },
        experience_years: 3,
        own_capital: 100000,
        desired_loan: 70000,
        is_new_business: true,
      },
      financials: {
        startup_cost: 20000,
        equipment_cost: 120000,
        inventory_cost: 30000,
        monthly_fixed_cost: 15000,
        customers_per_day: 8,
        avg_ticket_price: 500,
        working_days_per_month: 26,
        variable_cost_pct: 30,
        interest_rate_pct: 10.5,
        loan_tenure_months: 48,
      },
    },
  },
  {
    id: "village_dairy",
    name: "Village Dairy Unit",
    payload: {
      profile: {
        business_name: "Village Dairy Unit",
        category: "Dairy Farming & Milk Chilling",
        description: "Procurement of crossbred milch cows, fodder management, and morning/evening fresh milk collection.",
        location: {
          state: "Uttar Pradesh",
          district: "Varanasi",
          village: "Ramnagar",
        },
        experience_years: 2,
        own_capital: 80000,
        desired_loan: 300000,
        is_new_business: true,
      },
      financials: {
        startup_cost: 50000,
        equipment_cost: 250000,
        inventory_cost: 50000,
        monthly_fixed_cost: 25000,
        customers_per_day: 15,
        avg_ticket_price: 250,
        working_days_per_month: 26,
        variable_cost_pct: 65,
        interest_rate_pct: 11.0,
        loan_tenure_months: 60,
      },
    },
  },
  {
    id: "sri_amman_tea",
    name: "Sri Amman Tea & Snacks",
    payload: {
      profile: {
        business_name: "Sri Amman Tea & Snacks",
        category: "Kirana & General Store",
        description: "Daily roadside tea stall, traditional snack frying, bakery goods, and morning breakfast catering.",
        location: {
          state: "Karnataka",
          district: "Mysuru",
          village: "Nanjangud",
        },
        experience_years: 4,
        own_capital: 60000,
        desired_loan: 100000,
        is_new_business: true,
      },
      financials: {
        startup_cost: 25000,
        equipment_cost: 100000,
        inventory_cost: 25000,
        monthly_fixed_cost: 18000,
        customers_per_day: 40,
        avg_ticket_price: 50,
        working_days_per_month: 26,
        variable_cost_pct: 55,
        interest_rate_pct: 10.5,
        loan_tenure_months: 48,
      },
    },
  },
];

function analyzeProfile(profileObj) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(profileObj.payload);
    const options = {
      hostname: "localhost",
      port: 8000,
      path: "/api/analyze",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(postData),
      },
    };

    const req = http.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          const parsed = JSON.parse(data);
          resolve({ profileName: profileObj.name, statusCode: res.statusCode, result: parsed });
        } catch (e) {
          reject(new Error(`Failed to parse response: ${data}`));
        }
      });
    });

    req.on("error", (e) => reject(e));
    req.write(postData);
    req.end();
  });
}

async function run() {
  console.log("Evaluating 4 Demo Profiles against Live FastAPI Backend...\n");
  for (const p of PROFILES) {
    try {
      const res = await analyzeProfile(p);
      console.log(`=======================================================`);
      console.log(`PROFILE: ${res.profileName}`);
      console.log(`Status Code: ${res.statusCode}`);
      const r = res.result;
      console.log(`Recommendation: ${r.recommendation_status}`);
      console.log(`Overall Verdict: ${r.overall_verdict}`);
      console.log(`Confidence Score: ${r.confidence_score}%`);
      console.log(`Monthly Revenue: ₹${r.financial_result?.monthly_revenue?.toLocaleString("en-IN")}`);
      console.log(`Monthly Net Profit: ₹${r.financial_result?.monthly_net_profit?.toLocaleString("en-IN")}`);
      console.log(`Net Profit Margin: ${r.financial_result?.net_profit_margin_pct}%`);
      console.log(`Monthly EMI: ₹${r.financial_result?.monthly_emi?.toLocaleString("en-IN")}`);
      console.log(`DSCR: ${r.financial_result?.dscr}x`);
      console.log(`Break-Even Daily Units: ${r.financial_result?.break_even_units_daily} / day`);
      console.log(`Total Capex: ₹${r.financial_result?.total_capex?.toLocaleString("en-IN")}`);
      console.log(`Required Loan: ₹${r.financial_result?.required_loan_amount?.toLocaleString("en-IN")}`);
      console.log(`Risk Factors: ${(r.risk_factors || []).map(rf => `${rf.factor} (${rf.severity})`).join(", ") || "None"}`);
      console.log(`Matched Schemes: ${(r.scheme_result?.schemes || []).map(s => `${s.scheme_name} (${s.eligibility_status})`).join(", ") || "None"}`);
      console.log("\n");
    } catch (err) {
      console.error(`Error evaluating ${p.name}:`, err.message);
    }
  }
}

run();
