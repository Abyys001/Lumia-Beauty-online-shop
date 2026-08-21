/**
 * Fold Persian and Arabic-Indic digits to ASCII.
 *
 * Persian keyboards produce ۰-۹, which every numeric field on the API rejects.
 * Mirrors `to_en_digits` in `backend/apps/accounts/models.py`.
 */
export function toEnDigits(value: string): string {
  return value
    .replace(/[۰-۹]/g, d => String(d.charCodeAt(0) - 0x06f0))
    .replace(/[٠-٩]/g, d => String(d.charCodeAt(0) - 0x0660))
}

/** ASCII digits back to Persian, for counts shown inside Persian sentences. */
export function toFaDigits(value: string | number): string {
  return String(value).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[Number(d)])
}
