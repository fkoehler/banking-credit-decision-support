export type Citation = {
  documentId: string;
  title: string;
  section: string;
  score: number;
};

export type Assessment = {
  id: string;
  caseId: string;
  riskProbability: number;
  riskBand: "LOW" | "MEDIUM" | "HIGH";
  positiveFactors: string[];
  riskFactors: string[];
  summary: string;
  citations: Citation[];
  generationMode: string;
  modelVersion: string;
  correlationId: string;
  createdAt: string;
};

export type CreditCase = {
  id: string;
  profession: string;
  status: string;
  assessments: Assessment[];
};

export type CaseInput = {
  profession: string;
  annualIncome: number;
  practiceRevenue: number;
  practiceAgeYears: number;
  existingDebt: number;
  requestedCredit: number;
  equity: number;
  latePayments: number;
};

