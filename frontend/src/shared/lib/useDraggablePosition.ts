import React, { useEffect, useRef, useState } from "react";

export type DragPos = { x: number; y: number };

// 모달 헤더바를 마우스로 누른 채 움직이면 모달 전체가 따라 이동하게 해주는 훅.
// pos는 기본(중앙) 위치로부터의 픽셀 오프셋이며, onMouseDown을 헤더바에 걸어 쓴다.
export function useDraggablePosition(initial: DragPos) {
  const [pos, setPos] = useState<DragPos>(initial);
  const [dragging, setDragging] = useState(false);
  const start = useRef<DragPos>({ x: 0, y: 0 });
  const origin = useRef<DragPos>({ x: 0, y: 0 });

  const onMouseDown = (e: React.MouseEvent) => {
    start.current = { x: e.clientX, y: e.clientY };
    origin.current = pos;
    setDragging(true);
  };

  useEffect(() => {
    if (!dragging) return;
    const handleMouseMove = (e: MouseEvent) => {
      setPos({
        x: origin.current.x + (e.clientX - start.current.x),
        y: origin.current.y + (e.clientY - start.current.y),
      });
    };
    const handleMouseUp = () => setDragging(false);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [dragging]);

  return { pos, setPos, onMouseDown };
}
