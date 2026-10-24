#!/usr/bin/env python3
"""MIT. Non-mutating replay of the fixed Vol.6.1 repository import.

Past package verification records reproduce fixed manuscript tables; they never
stand in for fresh runtime evidence. No golden freeze, PDF build or remote write.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): digest(p)
            for p in sorted(root.rglob("*"))
            if p.is_file() and ".git" not in p.relative_to(root).parts}


def safe_path(relative: str) -> Path:
    rel = Path(relative)
    require(not rel.is_absolute() and ".." not in rel.parts
            and "\\" not in relative, "unsafe manifest path")
    path = ROOT / rel
    require(not path.is_symlink() and path.is_file(), "missing/linked input: " + relative)
    require(path.resolve().is_relative_to(ROOT), "input escapes repository")
    return path


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "NOT_AVAILABLE_LOCAL_RECONSTRUCTION"


def replay(report: dict) -> None:
    manifest = load(HERE / "integration/phase3-manifest.json")
    require(manifest["edition"] == "2026-10-23", "wrong edition")
    rows = manifest["phase2_copies"] + manifest["phase3_support_copies"]
    require(len({r["repository_path"] for r in rows}) == len(rows), "duplicate mapping")
    for row in rows:
        p = safe_path(row["repository_path"])
        require(p.stat().st_size == row["bytes"] and digest(p) == row["sha256"],
                "mapped input changed: " + row["repository_path"])
    require(len(manifest["phase2_copies"]) == 61, "incomplete phase-2 mapping")
    expected_harness = {r["repository_path"].split("harness/", 1)[1]: r["sha256"]
                        for r in manifest["phase2_copies"] if "/harness/" in r["repository_path"]}
    harness = HERE / "harness"
    require(len(expected_harness) == 59 and inventory(harness) == expected_harness,
            "harness file set/bytes mismatch")
    expected_generated = manifest["manuscript_result_sha256"]
    require(len(expected_generated) == 17 and inventory(harness / "generated") == expected_generated,
            "repository/manuscript generated mismatch")
    require(len(manifest["manuscript_generated_sha256"]) == 8, "incomplete table expectation")
    report["identity"] = {"phase2_copies": 61, "phase3_support_copies": len(rows) - 61,
                          "harness_files": 59, "manuscript_result_files": 17, "status": "PASS"}
    report["manifest_sha256"] = digest(HERE / "integration/phase3-manifest.json")
    report["sync_contract_sha256"] = digest(HERE / "SYNC_CONTRACT.json")
    with tempfile.TemporaryDirectory(prefix="vol61-replay-") as td:
        work = Path(td)
        def run(label: str, arguments: list[str]) -> dict:
            command = [sys.executable, "-I", "-B"] + arguments
            proc = subprocess.run(command, cwd=ROOT, capture_output=True,
                                  text=True, encoding="utf-8", timeout=240)
            clean = lambda s: s.replace(str(ROOT), "<REPO>").replace(str(work), "<WORKDIR>").replace(sys.executable, "<PYTHON>")
            entry = {"label": label, "command": [clean(s) for s in command],
                     "returncode": proc.returncode, "stdout": clean(proc.stdout),
                     "stderr": clean(proc.stderr)}
            report["executions"].append(entry)
            require(proc.returncode == 0, "execution failed: " + label)
            return entry
        for mode in ("normal", "optimized"):
            flags = [] if mode == "normal" else ["-O"]
            out = work / mode / "generated"
            base = "witnesses/vol6_1/harness/"
            gate = run("gate_" + mode, flags + [base + "run_all.py", "--release", "--out-dir", str(out)])
            summary = json.loads(gate["stdout"])
            require(summary["status"] == "PASS_FIXED_SUITE" and summary["checked_witnesses"] == 13
                    and summary["claims_checked"] == 50, "unexpected gate result")
            fresh = inventory(out)
            require(fresh == expected_generated, "fresh result file set/bytes differs: " + mode)
            result = {"suite_cases": 13, "finite_predicates": 50, "generated_files_byte_equal": 17}
            for script, expected_count, expected_status, key in (
                    ("selftest.py", 97, "PASS", "primary_selftests"),
                    ("checker_selftest.py", 116, "PASS_CHECKER_SELFTEST", "checker_selftests")):
                evidence = work / mode / (script + ".json")
                run(key + "_" + mode, flags + [base + script, "--out", str(evidence)])
                data = load(evidence)
                # Test count and failures are mandatory; primary's actual status is retained.
                require(data["tests"] == expected_count and data["passed"] == expected_count
                        and data["failed"] == 0 and data["status"] == expected_status, "selftest mismatch")
                result[key] = expected_count
                result[key + "_status"] = data["status"]
                report["fresh_evidence"][mode + "_" + key] = data
            independent = work / mode / "independent.json"
            run("independent_" + mode, flags + [base + "independent_check.py", "--specs", str(harness / "specs"),
                 "--results", str(out), "--out", str(independent)])
            data = load(independent)
            require(data["status"] == "PASS_INDEPENDENT_FINITE_EVIDENCE" and data["witness_count"] == 13,
                    "independent result mismatch")
            require(sum(r["claim_check_count"] for r in data["results"]) == 50, "independent predicates mismatch")
            result["independent_complete_records"] = 13
            report["fresh_evidence"][mode + "_independent"] = data
            bounded = work / mode / "bounded.json"
            run("bounded_" + mode, flags + [base + "bounded_check.py", "--out", str(bounded)])
            data = load(bounded)
            require(data["status"] == "PASS_BOUNDED_CROSS_IMPLEMENTATION" and data["path_models"] == 20740
                    and data["path_summary_fields_compared"] == 373320
                    and data["one_decision_policy_models"] == 2696, "bounded comparison mismatch")
            result.update(bounded_path_models=20740, bounded_path_fields=373320, bounded_policy_models=2696)
            report["fresh_evidence"][mode + "_bounded"] = data
            toy = work / mode / "toy_d.json"
            run("toy_d_" + mode, flags + ["witnesses/vol6_1/checks/toy_d_information_correspondence.py",
                                          "--software-root", str(ROOT), "--out", str(toy)])
            data = load(toy)
            require(data["status"] == "PASS_FIXED_TOY_D_INFORMATION_CORRESPONDENCE" and len(data["worlds"]) == 2
                    and all(r["status"] == "PASS" for r in data["worlds"]), "Toy D mismatch")
            result["toy_d_worlds"] = 2
            report["fresh_evidence"][mode + "_toy_d"] = data
            report["per_mode"][mode] = result
        require(inventory(work / "normal/generated") == inventory(work / "optimized/generated"), "mode outputs differ")
        table = work / "table-source"
        shutil.copytree(HERE / "integration/table-inputs", table)
        shutil.copyfile(HERE / "SYNC_CONTRACT.json", table / "SYNC_CONTRACT.json")
        shutil.copytree(work / "normal/generated", table / "results")
        run("manuscript_tables", [str(table / "build_tables.py")])
        require(inventory(table / "generated") == manifest["manuscript_generated_sha256"], "manuscript table bytes differ")
        report["manuscript_tables"] = {"files_byte_equal": 8, "status": "PASS", "pdf_build": "NOT_RUN",
            "inputs": "fresh normal-mode results plus unchanged historical package verification/source records"}
        report["status"] = "PASS_REPOSITORY_REPLAY"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args()
    target = a.report.resolve()
    if target == ROOT or target.is_relative_to(ROOT) or target.exists():
        ap.error("report must be a new path outside the repository; no overwrite")
    before = inventory(ROOT)
    report = {"schema": "rephase.vol61.repository-replay-result.v1", "status": "RUNNING",
              "started_at_utc": datetime.now(timezone.utc).isoformat(), "repository_commit": git_commit(),
              "platform": platform.system(), "python": platform.python_version(),
              "native_windows_execution": platform.system() == "Windows", "executions": [],
              "per_mode": {}, "fresh_evidence": {}, "golden_freeze_calls": 0,
              "remote_actions": 0, "pdf_build": "NOT_RUN", "patch_applications": "NOT_RUN",
              "scope": "fixed finite suite, named bounded models and mapped source/table bytes; not external certification"}
    try:
        replay(report)
    except Exception as exc:
        report["status"] = "FAIL_REPOSITORY_REPLAY"
        report["error"] = str(exc).replace(str(ROOT), "<REPO>")
    finally:
        report["source_unchanged"] = inventory(ROOT) == before
        if not report["source_unchanged"]:
            report["status"] = "FAIL_REPOSITORY_REPLAY"
            report["source_change_error"] = "repository file set/bytes changed during replay"
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as f:
            f.write((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({k: v for k, v in report.items() if k not in {"fresh_evidence", "executions"}}, indent=2))
    return 0 if report["status"] == "PASS_REPOSITORY_REPLAY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
