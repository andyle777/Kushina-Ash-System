"""
OmniSoul Mystic X 4.5.1 — Analytical Mystic Engine Edition
Robust mill / store / card runner with validation, error recovery,
extended instruction set, and persistent engine state.
Fully runnable.

Changelog 4.5 -> 4.5.1 (stress-test hardening):
  FIX:   `cards <program>` args form was broken; only --prog worked.
         Args are now joined and split on "|".
  FIX:   JZ with out-of-range target now reports an ERROR instead of
         lying "JZ not taken".
  FIX:   Startup demo clobbered persisted pc/cards; demo now loads only
         when there is no restorable state.
  FIX:   Backup filenames collided at 1-second resolution; now unique per
         step_count, and backups are throttled (on load/reset, every 50 steps).
  ADD:   Undefined variable reads are logged as warnings instead of
         silently fabricating 0.0.
  CLEAN: Removed unused imports (hashlib, zlib) and dead VAULT constant.
"""

import json
import shlex
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple

ENGINE_STATE = Path("omnisoul_ame_engine.json")
BACKUP_DIR = Path("omnisoul_ame_backups")
BACKUP_DIR.mkdir(exist_ok=True)


class AnalyticalMysticEngine:
    """Hardened Analytical Engine simulator.
    Mill = accumulator, Store = variable memory, Cards = program.
    """

    VALID_OPS = {"SET", "LOAD", "STORE", "ADD", "SUB", "MUL", "DIV", "PRINT", "HALT", "NOP", "JMP", "JZ"}

    def __init__(self):
        self.store: Dict[str, float] = {}
        self.mill: float = 0.0
        self.cards: List[str] = []
        self.pc: int = 0
        self.halted: bool = False
        self.error_log: List[str] = []
        self.step_count: int = 0
        self._load_state()

    def _load_state(self):
        if ENGINE_STATE.exists():
            try:
                data = json.loads(ENGINE_STATE.read_text())
                self.store = {k: float(v) for k, v in data.get("store", {}).items()}
                self.mill = float(data.get("mill", 0.0))
                self.cards = data.get("cards", [])
                self.pc = int(data.get("pc", 0))
                self.halted = bool(data.get("halted", False))
                self.step_count = int(data.get("step_count", 0))
            except Exception as e:
                self.error_log.append(f"State load failed: {e}")

    def _save_state(self, backup: bool = False):
        payload = {
            "store": self.store,
            "mill": self.mill,
            "cards": self.cards,
            "pc": self.pc,
            "halted": self.halted,
            "step_count": self.step_count,
        }
        ENGINE_STATE.write_text(json.dumps(payload, indent=2))
        # Backup on demand (load/reset) and every 50 steps; unique name
        # per step_count so fast runs never overwrite each other.
        if backup or self.step_count % 50 == 0:
            stamp = time.strftime("%Y%m%d_%H%M%S")
            (BACKUP_DIR / f"engine_{stamp}_s{self.step_count}.json").write_text(json.dumps(payload))

    def _read(self, var: str, op: str) -> float:
        """Store read that refuses to silently fabricate zeros."""
        if var not in self.store:
            self.error_log.append(f"warn: {op} read undefined var '{var}' as 0.0")
            return 0.0
        return self.store[var]

    def reset(self):
        self.store.clear()
        self.mill = 0.0
        self.cards.clear()
        self.pc = 0
        self.halted = False
        self.step_count = 0
        self.error_log.clear()
        self._save_state(backup=True)

    def load_cards(self, program: List[str]) -> Tuple[bool, str]:
        cleaned = []
        for i, raw in enumerate(program):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if not parts or parts[0].upper() not in self.VALID_OPS:
                return False, f"Invalid op on card {i}: {line}"
            cleaned.append(line)
        self.cards = cleaned
        self.pc = 0
        self.halted = False
        self._save_state(backup=True)
        return True, f"Loaded {len(cleaned)} cards"

    def step(self) -> str:
        if self.halted or self.pc >= len(self.cards):
            self.halted = True
            return "HALT"
        card = self.cards[self.pc]
        self.pc += 1
        self.step_count += 1
        result = self._execute(card)
        self._save_state()
        return result

    def run(self, max_steps: int = 128) -> List[str]:
        log = []
        for _ in range(max_steps):
            if self.halted:
                break
            log.append(self.step())
        return log

    def _execute(self, card: str) -> str:
        parts = card.split()
        op = parts[0].upper()
        try:
            if op == "SET" and len(parts) == 3:
                var, val = parts[1], float(parts[2])
                self.store[var] = val
                return f"SET {var} = {val}"
            if op == "LOAD" and len(parts) == 2:
                var = parts[1]
                self.mill = self._read(var, "LOAD")
                return f"LOAD {var} → mill={self.mill}"
            if op == "STORE" and len(parts) == 2:
                var = parts[1]
                self.store[var] = self.mill
                return f"STORE {var} ← {self.mill}"
            if op == "ADD" and len(parts) == 2:
                var = parts[1]
                self.mill += self._read(var, "ADD")
                return f"ADD {var} → mill={self.mill}"
            if op == "SUB" and len(parts) == 2:
                var = parts[1]
                self.mill -= self._read(var, "SUB")
                return f"SUB {var} → mill={self.mill}"
            if op == "MUL" and len(parts) == 2:
                var = parts[1]
                self.mill *= self._read(var, "MUL")
                return f"MUL {var} → mill={self.mill}"
            if op == "DIV" and len(parts) == 2:
                var = parts[1]
                denom = self._read(var, "DIV")
                if denom == 0:
                    self.error_log.append("DIV by zero")
                    return "ERROR: DIV by zero"
                self.mill /= denom
                return f"DIV {var} → mill={self.mill}"
            if op == "PRINT":
                return f"PRINT mill={self.mill} store={dict(self.store)}"
            if op == "JMP" and len(parts) == 2:
                target = int(parts[1])
                if 0 <= target < len(self.cards):
                    self.pc = target
                    return f"JMP → {target}"
                self.error_log.append("JMP out of range")
                return "ERROR: JMP out of range"
            if op == "JZ" and len(parts) == 2:
                if self.mill != 0:
                    return "JZ not taken"
                target = int(parts[1])
                if 0 <= target < len(self.cards):
                    self.pc = target
                    return f"JZ taken → {target}"
                self.error_log.append("JZ out of range")
                return "ERROR: JZ out of range"
            if op == "HALT":
                self.halted = True
                return "HALT"
            if op == "NOP":
                return "NOP"
            return f"ERROR: bad card '{card}'"
        except Exception as e:
            self.error_log.append(str(e))
            return f"ERROR: {e}"

    def status(self) -> Dict[str, Any]:
        return {
            "mill": self.mill,
            "store": self.store,
            "pc": self.pc,
            "cards": len(self.cards),
            "halted": self.halted,
            "steps": self.step_count,
            "errors": self.error_log[-5:],
        }


class Parser:
    @staticmethod
    def parse(line: str) -> Dict[str, Any]:
        if not line.strip():
            return {"cmd": "", "args": [], "flags": {}}
        try:
            tokens = shlex.split(line)
        except ValueError:
            tokens = line.split()
        if not tokens:
            return {"cmd": "", "args": [], "flags": {}}
        cmd = tokens[0].lower()
        args, flags = [], {}
        i = 1
        while i < len(tokens):
            tok = tokens[i]
            if tok.startswith("--"):
                key = tok[2:]
                if i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                    flags[key] = tokens[i + 1]
                    i += 2
                else:
                    flags[key] = True
                    i += 1
            else:
                args.append(tok)
                i += 1
        return {"cmd": cmd, "args": args, "flags": flags}


class OmniSoulAME:
    def __init__(self):
        self.parser = Parser()
        self.engine = AnalyticalMysticEngine()

    def handle(self, line: str) -> str:
        p = self.parser.parse(line)
        cmd, args, flags = p["cmd"], p["args"], p["flags"]

        if cmd == "cards":
            prog: List[str] = []
            if "prog" in flags:
                prog = flags["prog"].split(";")
            elif args:
                joined = " ".join(args)
                prog = [c.strip() for c in joined.split("|")]
            ok, msg = self.engine.load_cards(prog)
            return msg if ok else f"Load failed: {msg}"
        if cmd == "run":
            steps = int(flags.get("steps", 64))
            log = self.engine.run(steps)
            return "\n".join(log) if log else "(no steps)"
        if cmd == "step":
            return self.engine.step()
        if cmd == "reset":
            self.engine.reset()
            return "Engine reset"
        if cmd == "status":
            return json.dumps(self.engine.status(), indent=2)
        if cmd in ("help", "?"):
            return (
                "Analytical Mystic Engine commands:\n"
                "  cards SET A 5 | LOAD A | ADD B | STORE C | MUL C | PRINT | HALT\n"
                "  cards --prog \"SET A 5;LOAD A;ADD A;PRINT;HALT\"\n"
                "  run [--steps N]\n"
                "  step\n"
                "  reset\n"
                "  status\n"
                "  quit"
            )
        return f"Unknown command '{cmd}'. Type help."


if __name__ == "__main__":
    soul = OmniSoulAME()
    print("OmniSoul Mystic X 4.5.1 — Analytical Mystic Engine Edition")
    print("Robust mill/store/card runner. Type help.\n")

    # Load the demo ONLY when there is nothing to restore, so persisted
    # programs survive restarts instead of being clobbered.
    if soul.engine.cards:
        print("Persisted engine state restored. Type 'status' to inspect.\n")
    else:
        demo = ["SET A 8", "SET B 2", "LOAD A", "MUL B", "STORE C", "PRINT", "HALT"]
        soul.engine.load_cards(demo)
        print("Demo program loaded (8 * 2). Type 'run' or 'step'.\n")

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line or line.lower() == "quit":
            break
        print(soul.handle(line))
        print()
    print("Shutdown.")
