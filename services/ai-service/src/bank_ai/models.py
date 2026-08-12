from pydantic import BaseModel, Field


class CreditFeatures(BaseModel):
    profession: str
    annualIncome: float = Field(ge=0)
    practiceRevenue: float = Field(ge=0)
    practiceAgeYears: int = Field(ge=0, le=100)
    existingDebt: float = Field(ge=0)
    requestedCredit: float = Field(gt=0)
    equity: float = Field(ge=0)
    latePayments: int = Field(ge=0, le=100)


class AssessmentRequest(CreditFeatures):
    correlationId: str


class Citation(BaseModel):
    documentId: str
    title: str
    section: str
    score: float


class AssessmentResponse(BaseModel):
    riskProbability: float
    riskBand: str
    positiveFactors: list[str]
    riskFactors: list[str]
    summary: str
    citations: list[Citation]
    generationMode: str
    modelVersion: str


class DocumentRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=20, max_length=2_000_000)
    source: str = Field(default="synthetic", max_length=200)


class DocumentResponse(BaseModel):
    documentId: str
    title: str
    checksum: str
    chunkCount: int


class DocumentSummary(BaseModel):
    documentId: str
    title: str
    source: str
    chunkCount: int
