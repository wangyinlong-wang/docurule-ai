export type CaseStatus =
  | "uploaded"
  | "processing"
  | "needs_review"
  | "approved"
  | "rejected"
  | "failed";

export interface ExtractedField {
  key: string;
  label: string;
  value: string | number | null;
  confidence: number;
  source_document_id: string | null;
  source_quote: string | null;
  reviewed: boolean;
}

export interface DocumentRecord {
  id: string;
  file_name: string;
  media_type: string;
  kind: string;
  kind_label: string;
  status: "queued" | "processed" | "failed";
  size_bytes: number;
  page_count: number;
  fields: ExtractedField[];
  error: string | null;
}

export interface ValidationResult {
  id: string;
  title: string;
  status: "passed" | "warning" | "failed";
  message: string;
  related_fields: string[];
}

export interface CaseRecord {
  id: string;
  name: string;
  status: CaseStatus;
  decision: string | null;
  progress: number;
  documents: DocumentRecord[];
  fields: ExtractedField[];
  validations: ValidationResult[];
  metadata: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface ProviderStatus {
  provider: string;
  model: string;
  available: boolean;
  detail: string;
}
