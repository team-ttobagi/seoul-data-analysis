import React from "react";
import { AlertTriangle, Loader2 } from "lucide-react";

export type QueryStateKind = "loading" | "error" | "empty";

// error는 loading/empty와 확실히 구분되도록 빨간 테두리 + 경고 아이콘을 쓴다.
// 정상 데이터 화면(검은 테두리)과 절대 혼동되지 않게 하기 위함.
const KIND_STYLES: Record<
  QueryStateKind,
  { border: string; text: string; icon: React.ReactNode | null }
> = {
  loading: {
    border: "border-black",
    text: "text-gray-700",
    icon: <Loader2 className="w-4 h-4 animate-spin" />,
  },
  error: {
    border: "border-red-600",
    text: "text-red-700",
    icon: <AlertTriangle className="w-4 h-4" />,
  },
  empty: {
    border: "border-gray-300",
    text: "text-gray-500",
    icon: null,
  },
};

/** 표/카드 내부 한 영역에 쓰는 작은 인라인 상태 배너. */
export const StatusInline: React.FC<{
  kind: QueryStateKind;
  message: string;
}> = ({ kind, message }) => {
  const style = KIND_STYLES[kind];
  return (
    <div
      className={`flex items-center gap-2 border ${style.border} ${style.text} px-3 py-2 font-mono text-xs font-bold bg-white`}
    >
      {style.icon}
      <span>{message}</span>
    </div>
  );
};

/** 페이지/큰 섹션 전체를 대체하는 상태 블록. */
export const StatusBlock: React.FC<{
  kind: QueryStateKind;
  title: string;
  description?: string;
  action?: React.ReactNode;
}> = ({ kind, title, description, action }) => {
  const style = KIND_STYLES[kind];
  return (
    <div className={`border-2 ${style.border} bg-white p-12 text-center space-y-4`}>
      <div className={`flex items-center justify-center gap-2 ${style.text}`}>
        {style.icon}
        <p className="font-mono text-base font-bold">{title}</p>
      </div>
      {description && (
        <p className="font-mono text-xs text-gray-500">{description}</p>
      )}
      {action}
    </div>
  );
};
