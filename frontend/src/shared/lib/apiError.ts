import { isAxiosError } from "axios";

/**
 * axios 에러를 사용자에게 보여줄 한글 메시지로 변환한다.
 * 백엔드 에러 응답 포맷은 { error: { code, message } } (schemas.py 기준)이며,
 * 이 메시지가 있으면 우선 사용하고, 없으면 네트워크/타임아웃 여부에 따라 안내 문구를 반환한다.
 */
export function getApiErrorMessage(
  error: unknown,
  fallback = "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
): string {
  if (isAxiosError(error)) {
    const backendMessage = error.response?.data?.error?.message;
    if (typeof backendMessage === "string" && backendMessage) {
      return backendMessage;
    }
    if (error.code === "ECONNABORTED") {
      return "요청이 시간 초과되었습니다. 잠시 후 다시 시도해주세요.";
    }
    if (!error.response) {
      return "네트워크 연결을 확인해주세요.";
    }
  }
  return fallback;
}
