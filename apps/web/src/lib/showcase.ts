import type { CaseRecord, ExtractedField, ProviderStatus, ValidationResult } from "../types";

const now = () => new Date().toISOString();
const clone = <T>(value: T): T => structuredClone(value);

const csvCell = (value: unknown) => {
  const text = value == null ? "" : String(value);
  return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
};

/** Keep the hosted export contract aligned with the API's one-row-per-field CSV. */
export const caseToCsv = (item: CaseRecord) => {
  const columns = [
    "case_id",
    "case_name",
    "case_status",
    "decision",
    "field_key",
    "label",
    "value",
    "confidence",
    "source_document_id",
    "source_quote",
    "reviewed",
  ];
  const fields = new Map(item.fields.map((field) => [field.key, field]));
  const rows = [...fields.values()].map((field) => [
    item.id,
    item.name,
    item.status,
    item.decision ?? "",
    field.key,
    field.label,
    field.value ?? "",
    field.confidence,
    field.source_document_id ?? "",
    field.source_quote ?? "",
    field.reviewed,
  ]);
  return [columns, ...rows].map((row) => row.map(csvCell).join(",")).join("\n") + "\n";
};

const field = (
  key: string,
  label: string,
  value: string | number,
  documentId: string,
  sourceQuote: string,
): ExtractedField => ({
  key,
  label,
  value,
  confidence: 0.93,
  source_document_id: documentId,
  source_quote: sourceQuote,
  reviewed: false,
});

const initialValidations = (): ValidationResult[] => [
  {
    id: "three_way_document_set_complete",
    title: "Three-way document set complete",
    status: "passed",
    message: "All required document kinds are present: purchase_order, invoice, delivery_note.",
    related_fields: [],
  },
  {
    id: "supplier_matches",
    title: "Supplier matches across documents",
    status: "passed",
    message: "Values match across 3 documents: Northstar Components Ltd.",
    related_fields: ["supplier_name"],
  },
  {
    id: "po_number_matches",
    title: "PO number matches across documents",
    status: "passed",
    message: "Values match across 3 documents: PO-2026-0812.",
    related_fields: ["po_number"],
  },
  {
    id: "currency_matches",
    title: "Currency matches across documents",
    status: "passed",
    message: "Values match across 3 documents: USD.",
    related_fields: ["currency"],
  },
  {
    id: "invoiced_quantity_within_received_quantity",
    title: "Invoiced quantity does not exceed received quantity",
    status: "failed",
    message: "Compared 96 ≤ 90.",
    related_fields: ["invoiced_quantity", "received_quantity"],
  },
  {
    id: "invoice_total_within_received_value",
    title: "Invoice total does not exceed received value",
    status: "failed",
    message: "Compared 2400 ≤ 2250.",
    related_fields: ["invoice_total", "received_quantity", "unit_price"],
  },
];

const buildShowcaseCase = (): CaseRecord => {
  const poFields = [
    field("supplier_name", "Supplier", "Northstar Components Ltd", "po", "Supplier: Northstar Components Ltd"),
    field("po_number", "PO number", "PO-2026-0812", "po", "PO Number: PO-2026-0812"),
    field("currency", "Currency", "USD", "po", "Currency: USD"),
    field("ordered_quantity", "Ordered quantity", 100, "po", "Ordered Quantity: 100"),
    field("unit_price", "Unit price", 25, "po", "Unit Price: $25.00"),
  ];
  const invoiceFields = [
    field("supplier_name", "Supplier", "Northstar Components Ltd", "invoice", "Supplier: Northstar Components Ltd"),
    field("po_number", "PO number", "PO-2026-0812", "invoice", "PO Number: PO-2026-0812"),
    field("currency", "Currency", "USD", "invoice", "Currency: USD"),
    field("invoiced_quantity", "Invoiced quantity", 96, "invoice", "Invoiced Quantity: 96"),
    field("unit_price", "Unit price", 25, "invoice", "Unit Price: $25.00"),
    field("invoice_total", "Invoice total", 2400, "invoice", "Invoice Total: $2,400.00"),
  ];
  const deliveryFields = [
    field("supplier_name", "Supplier", "Northstar Components Ltd", "delivery", "Supplier: Northstar Components Ltd"),
    field("po_number", "PO number", "PO-2026-0812", "delivery", "PO Number: PO-2026-0812"),
    field("currency", "Currency", "USD", "delivery", "Currency: USD"),
    field("received_quantity", "Received quantity", 90, "delivery", "Received Quantity: 90"),
    field("unit_price", "Unit price", 25, "delivery", "Unit Price: $25.00"),
  ];
  const created = now();
  return {
    id: "showcase-v03",
    name: "Procurement three-way match · Live showcase",
    status: "needs_review",
    decision: null,
    progress: 100,
    documents: [
      {
        id: "po",
        file_name: "purchase-order-PO-2026-0812.txt",
        media_type: "text/plain",
        kind: "purchase_order",
        kind_label: "Purchase order",
        status: "processed",
        size_bytes: 201,
        page_count: 1,
        fields: poFields,
        error: null,
      },
      {
        id: "invoice",
        file_name: "supplier-invoice-INV-1048.txt",
        media_type: "text/plain",
        kind: "invoice",
        kind_label: "Invoice / receipt",
        status: "processed",
        size_bytes: 221,
        page_count: 1,
        fields: invoiceFields,
        error: null,
      },
      {
        id: "delivery",
        file_name: "delivery-note-DN-7721.txt",
        media_type: "text/plain",
        kind: "delivery_note",
        kind_label: "Delivery note",
        status: "processed",
        size_bytes: 194,
        page_count: 1,
        fields: deliveryFields,
        error: null,
      },
    ],
    fields: [
      ...poFields.map((item) => clone(item)),
      clone(invoiceFields.find((item) => item.key === "invoiced_quantity")!),
      clone(invoiceFields.find((item) => item.key === "invoice_total")!),
      clone(deliveryFields.find((item) => item.key === "received_quantity")!),
    ],
    validations: initialValidations(),
    metadata: {
      engine: "deterministic-rules",
      processing_mode: "rules-only",
      recipe_id: "procurement-three-way-match",
      recipe_source: "static-showcase",
      audit_log: [],
    },
    created_at: created,
    updated_at: created,
  };
};

let storedCase: CaseRecord | null = null;

const requireCase = (id: string): CaseRecord => {
  if (!storedCase || storedCase.id !== id) throw new Error("Showcase case not found");
  return storedCase;
};

const provider: ProviderStatus = {
  provider: "static-showcase",
  model: "Rules-only demo",
  available: true,
  detail: "Synthetic data runs entirely in this browser tab.",
};

export const showcaseApi = {
  listCases: async () => (storedCase ? [clone(storedCase)] : []),
  getCase: async (id: string) => clone(requireCase(id)),
  getProvider: async () => clone(provider),
  createDemo: async () => {
    storedCase = buildShowcaseCase();
    return clone(storedCase);
  },
  createProcurementDemo: async () => {
    storedCase = buildShowcaseCase();
    return clone(storedCase);
  },
  createCase: async (_name: string, _files: File[]) => {
    throw new Error("Uploads are disabled in the hosted showcase. Run DocuRule locally to process files.");
  },
  runRecipe: async (_name: string, _recipe: File, _files: File[]) => {
    throw new Error("Recipe uploads are disabled in the hosted showcase. Run DocuRule locally to execute your rules.yml.");
  },
  updateField: async (caseId: string, key: string, value: string | number | null) => {
    const item = requireCase(caseId);
    const mergedField = item.fields.find((entry) => entry.key === key);
    if (!mergedField) throw new Error("Field not found");
    mergedField.value = value;
    mergedField.reviewed = true;
    mergedField.confidence = 1;
    for (const document of item.documents) {
      for (const documentField of document.fields) {
        if (documentField.key === key && documentField.source_document_id === mergedField.source_document_id) {
          documentField.value = value;
          documentField.reviewed = true;
          documentField.confidence = 1;
        }
      }
    }
    if (key === "received_quantity" && Number(value) >= 96) {
      item.validations = initialValidations().map((validation) =>
        validation.status === "failed"
          ? {
              ...validation,
              status: "passed",
              message:
                validation.id === "invoiced_quantity_within_received_quantity"
                  ? "Compared 96 ≤ 96."
                  : "Compared 2400 ≤ 2400.",
            }
          : validation,
      );
    }
    const auditLog = item.metadata.audit_log as Array<Record<string, unknown>>;
    auditLog.push({ action: "field_updated", field: key, value, at: now() });
    item.updated_at = now();
    return clone(item);
  },
  review: async (caseId: string, decision: "approved" | "rejected") => {
    const item = requireCase(caseId);
    item.decision = decision;
    item.status = decision;
    const auditLog = item.metadata.audit_log as Array<Record<string, unknown>>;
    auditLog.push({ action: "review_decision", decision, at: now() });
    item.updated_at = now();
    return clone(item);
  },
};

export const isShowcaseCaseComplete = (item: CaseRecord) =>
  item.validations.length > 0 && item.validations.every((result) => result.status === "passed");

export const resetShowcase = () => {
  storedCase = null;
};
