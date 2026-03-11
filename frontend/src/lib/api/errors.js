export function normalizeApiError(error) {
  const status = error?.response?.status ?? null;
  const data = error?.response?.data ?? null;
  const detail = typeof data?.detail === "string" ? data.detail : null;

  return {
    status,
    code: data?.code ?? data?.error ?? error?.code ?? "unknown_error",
    message: data?.message ?? detail ?? error?.message ?? "Unknown API error",
    details: data?.details ?? null,
  };
}
