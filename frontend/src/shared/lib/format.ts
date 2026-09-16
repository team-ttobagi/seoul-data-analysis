// 상권 상세/비교 화면에서 반복되던 숫자·분기 표시 로직을 모아둔 순수 함수 모음.
// [연동] 백엔드가 데이터 부족 시 null 을 내려주는 필드(growth_rate, seoul_rank, exploration_score,
// store_count 등)를 화면에 표시할 때, 0처럼 "유효하지만 falsy"한 값이 null 폴백에 잘못 덮이지
// 않도록 항상 null/undefined 여부만 명시적으로 검사한다(`||` 대신 `??`/`== null`).

/**
 * 부호가 있는 퍼센트 값을 표시용 문자열로 바꾼다.
 * - null/undefined 이면 "-"
 * - 0 이면 부호 없이 "0.0%" (0은 유효한 값이라 "-"로 감추지 않는다)
 * - 양수면 "+", 음수면 그대로("-"는 toFixed가 이미 붙여준다)
 */
export function formatSignedPercent(
  value: number | null | undefined,
  digits: number = 1,
): string {
  if (value == null) return "-";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(digits)}%`;
}

/**
 * 부호가 있는 개수 값을 표시용 문자열로 바꾼다(예: 점포 수 증감).
 * - null/undefined 이면 "-"
 * - 0 이면 부호 없이 "0개"
 */
export function formatSignedCount(
  value: number | null | undefined,
  unit: string = "개",
): string {
  if (value == null) return "-";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value}${unit}`;
}

/**
 * null/undefined 이면 "-", 아니면 값 뒤에 suffix 를 붙인 문자열을 반환한다.
 * exploration_score, seoul_rank(+"위"), store_count(+"개") 처럼 "값이 없을 때만" 감춰야 하는
 * 필드에 쓴다 — 0은 유효한 값이라 그대로 "0"(+suffix)으로 보여준다.
 */
export function formatNullable(
  value: number | string | null | undefined,
  suffix: string = "",
): string {
  if (value == null) return "-";
  return `${value}${suffix}`;
}

/**
 * 백엔드 quarter 코드(YYYYN, 예: "20254")를 화면 표시용 "2025 Q4" 형식으로 변환한다.
 * GET /api/v1/sales/quarters 가 내려주는 value 포맷과 동일하게 맞춘다.
 * 형식이 맞지 않는 입력은 그대로 반환한다(방어적 fallback).
 */
export function formatQuarterLabel(code: string): string {
  if (!/^\d{5}$/.test(code)) return code;
  return `${code.slice(0, 4)} Q${code.slice(4)}`;
}
