import type { CaseRecord } from "../types";

export type EmptyFieldsState = {
  kind: "vision-unavailable" | "image-only" | "text-empty";
  title: string;
  message: string;
  providerHref?: string;
};

const providerHref =
  "https://github.com/wangyinlong-wang/docurule-ai/blob/main/README.md#ai-providers";

/** Explain an empty extraction without hiding the review/export actions around it. */
export function getEmptyFieldsState(item: CaseRecord): EmptyFieldsState {
  const hasImage = item.documents.some((document) =>
    document.media_type.startsWith("image/"),
  );
  if (hasImage && item.metadata.provider_available === false) {
    return {
      kind: "vision-unavailable",
      title: "Vision provider unavailable",
      message:
        "No structured fields were extracted because the configured vision provider was unavailable. Check the provider setup, then process this review again.",
      providerHref,
    };
  }
  if (hasImage) {
    return {
      kind: "image-only",
      title: "Vision extraction is needed",
      message:
        "This packet includes image-only documents. Connect a compatible vision model to extract fields from scans, or keep the review for manual notes and export.",
      providerHref,
    };
  }
  return {
    kind: "text-empty",
    title: "No structured fields found",
    message:
      "The text documents did not contain any supported fields. Check the labels and file encoding, then keep the review for manual notes or export.",
  };
}
