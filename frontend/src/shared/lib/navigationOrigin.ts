import { useEffect } from "react";
import { useNavigationType } from "react-router-dom";

// 이 브라우저 탭에서 SPA가 부팅된 이후 앱 내부 이동(PUSH/REPLACE, 즉 <Link>/navigate() 호출)이
// 한 번이라도 있었는지 기록하는 모듈 스코프 플래그. 클라이언트 사이드 라우팅으로는 리셋되지 않고,
// 실제 새로고침이나 주소창 직접 입력처럼 새 문서가 로드되어 이 모듈이 다시 평가될 때만 초기화된다.
let hasNavigatedInApp = false;

/**
 * 지금 이 렌더가 "주소창 직접 입력/새로고침/북마크로 곧바로 들어온 진입점"인지 판단한다.
 * - 이번 이동이 PUSH/REPLACE(앱 내부 <Link>/navigate() 클릭)면 항상 false.
 * - 이번 이동이 POP이어도, 그 전에 이 세션에서 앱 내부 이동이 한 번이라도 있었다면
 *   (예: 이전에 PUSH로 들어왔다가 브라우저 뒤로가기로 돌아온 경우) false.
 * - POP이고 이 세션에서 앱 내부 이동이 한 번도 없었다면(진짜 최초 진입) true.
 */
export function useIsFreshDirectEntry(): boolean {
  const navigationType = useNavigationType();
  const isFresh = navigationType === "POP" && !hasNavigatedInApp;

  useEffect(() => {
    if (navigationType !== "POP") {
      hasNavigatedInApp = true;
    }
  }, [navigationType]);

  return isFresh;
}
