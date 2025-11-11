# core/repeater.py
from typing import Dict, Optional, List

class InputRepeater:
    """
    DAS/ARR scheduler for held actions (e.g., MOVE_LEFT, MOVE_RIGHT, SOFT_DROP).

    Usage:
      repeater = InputRepeater(das_ms=160, arr_ms=40, soft_ms=30)
      # on keydown:
      repeater.hold("MOVE_LEFT", True, now_ms)
      # on keyup:
      repeater.hold("MOVE_LEFT", False, now_ms)
      # each frame:
      for action in repeater.due(now_ms):
          dispatch(action)

    Semantics:
      - On first press, emits the action once immediately.
      - Then waits DAS before starting repeats at ARR cadence.
      - For SOFT_DROP, uses its own cadence (soft_ms) and no horizontal DAS.
    """
    def __init__(self, das_ms: int = 160, arr_ms: int = 40, soft_ms: int = 30) -> None:
        self.das_ms = max(0, das_ms)
        self.arr_ms = max(0, arr_ms)
        self.soft_ms = max(0, soft_ms)

        # action -> state
        self._state: Dict[str, Dict[str, Optional[int]]] = {}

        # Which actions should repeat:
        self._is_horizontal = {"MOVE_LEFT", "MOVE_RIGHT"}
        self._is_soft = {"SOFT_DROP"}

    def _ensure(self, action: str) -> Dict[str, Optional[int]]:
        if action not in self._state:
            self._state[action] = {"held": False, "first_at": None, "next_at": None, "emitted_first": False}
        return self._state[action]

    def hold(self, action: str, is_down: bool, now_ms: int) -> List[str]:
        """
        Update held state. Returns list of actions to emit IMMEDIATELY (first press).
        """
        st = self._ensure(action)
        st["held"] = is_down
        if is_down:
            st["first_at"] = now_ms
            st["emitted_first"] = False
            # Schedule first repeat time; immediate first emit handled here
            if action in self._is_horizontal:
                st["next_at"] = now_ms + self.das_ms
            elif action in self._is_soft:
                st["next_at"] = now_ms + self.soft_ms
            else:
                st["next_at"] = now_ms + self.arr_ms
            # Immediate first action
            st["emitted_first"] = True
            return [action]
        else:
            st["first_at"] = None
            st["next_at"] = None
            st["emitted_first"] = False
            return []

    def due(self, now_ms: int) -> List[str]:
        """
        Called every frame/tick; returns auto-repeat actions that are due by now_ms.
        """
        out: List[str] = []
        for action, st in self._state.items():
            if not st["held"]:
                continue
            # Horizontal: we already emitted once; wait until next_at >= now
            if st["next_at"] is None:
                continue
            if now_ms >= st["next_at"]:
                out.append(action)
                if action in self._is_horizontal:
                    st["next_at"] = now_ms + self.arr_ms
                elif action in self._is_soft:
                    st["next_at"] = now_ms + self.soft_ms
                else:
                    st["next_at"] = now_ms + self.arr_ms
        return out

    def clear(self) -> None:
        """Release everything (e.g., on pause)."""
        self._state.clear()
