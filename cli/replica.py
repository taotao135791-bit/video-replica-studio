#!/usr/bin/env python3
"""Unified CLI for reference-video replica QC.

Orchestrates the analysis, diff, and scaffolding workflows built by A1-A4.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
TEMPLATES = ROOT / "templates"


def die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def run_script(script: Path, args: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    """Run a Python script from the pipeline and stream its output."""
    cmd = [sys.executable, str(script)] + args
    print(f"--> {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        die(f"{script.name} exited with code {result.returncode}")
    return result


def ensure_out(path: Path) -> Path:
    path = path.expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def analyze(args: argparse.Namespace) -> None:
    video = args.video.expanduser().resolve()
    if not video.exists():
        die(f"video not found: {video}")

    out = ensure_out(args.out)
    script_args = [
        str(video),
        "--out",
        str(out),
        "--detect-scenes",
        "--motion-profile",
        "--contact",
    ]
    if args.preview:
        script_args.append("--preview")
    if args.interval is not None:
        script_args += ["--interval", str(args.interval)]

    run_script(SCRIPTS / "extract_frames.py", script_args)

    print(f"\nanalysis artifacts: {out}")
    for name in ("frames-manifest.json", "motion-profile.json", "scene-transitions.json"):
        artifact = out / name
        if artifact.exists():
            print(f"  - {artifact}")


def quick(args: argparse.Namespace) -> None:
    reference = args.reference.expanduser().resolve()
    candidate = args.candidate.expanduser().resolve()
    for label, path in (("reference", reference), ("candidate", candidate)):
        if not path.exists():
            die(f"{label} not found: {path}")

    out = ensure_out(args.out)
    ref_out = out / "ref"
    cand_out = out / "cand"

    run_script(SCRIPTS / "extract_frames.py", [str(reference), "--out", str(ref_out), "--preview"])
    run_script(SCRIPTS / "extract_frames.py", [str(candidate), "--out", str(cand_out), "--preview"])

    diff_out = out / "diff"
    run_script(
        SCRIPTS / "compare_videos.py",
        [
            str(reference),
            str(candidate),
            "--out",
            str(diff_out),
            "--render-diff",
            "--interval",
            "1.0",
            "--scale",
            "320:180",
        ],
    )

    print(f"\nquick comparison artifacts: {diff_out}")


def diff(args: argparse.Namespace) -> None:
    reference = args.reference.expanduser().resolve()
    candidate = args.candidate.expanduser().resolve()
    for label, path in (("reference", reference), ("candidate", candidate)):
        if not path.exists():
            die(f"{label} not found: {path}")

    out = ensure_out(args.out)
    script_args = [
        str(reference),
        str(candidate),
        "--out",
        str(out),
        "--render-diff",
        "--interval",
        str(args.interval),
        "--scale",
        args.scale,
    ]
    if args.crops:
        crops = args.crops.expanduser().resolve()
        if not crops.exists():
            die(f"crops file not found: {crops}")
        script_args += ["--component-crop", str(crops)]

    run_script(SCRIPTS / "compare_videos.py", script_args)

    if args.report:
        report_dir = TEMPLATES / "report"
        for name in ("alignment-report.md", "patch-log.md"):
            src = report_dir / name
            dst = out / name
            if src.exists():
                if dst.exists():
                    print(f"report template already exists, skipping: {dst}")
                else:
                    shutil.copy2(src, dst)
                    print(f"copied report template: {dst}")
            else:
                print(f"warning: missing report template {src}", file=sys.stderr)

    print(f"\ndiff artifacts: {out}")


def _rewrite_text(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    new_text = text
    for old, new in replacements:
        new_text = new_text.replace(old, new)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")


def scaffold(args: argparse.Namespace) -> None:
    out = args.out.expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        die(f"output directory is not empty: {out}")
    out.mkdir(parents=True, exist_ok=True)

    if args.stack == "remotion":
        example_src = TEMPLATES / "remotion" / "example"
        components_src = TEMPLATES / "remotion" / "components"
        shared_src = TEMPLATES / "remotion" / "shared"
        for src in (example_src, components_src, shared_src):
            if not src.exists():
                die(f"missing template source: {src}")

        ignore = shutil.ignore_patterns(
            "node_modules",
            "package-lock.json",
            "dist",
            "build",
            "out",
            ".next",
        )
        shutil.copytree(example_src, out, ignore=ignore, dirs_exist_ok=True)
        shutil.copytree(components_src, out / "components", dirs_exist_ok=True)
        shutil.copytree(shared_src, out / "shared", dirs_exist_ok=True)

        # Make the example self-contained at the project root.
        _rewrite_text(
            out / "src" / "Root.tsx",
            [('from "../../components/CameraRig";', 'from "../components/CameraRig";')],
        )
        _rewrite_text(
            out / "src" / "segments" / "ExampleScenes.tsx",
            [
                ('from "../../../components/', 'from "../../components/'),
                ('from "../../../shared/', 'from "../../shared/'),
            ],
        )
        _rewrite_text(
            out / "tsconfig.json",
            [
                (
                    '"include": ["src/**/*", "../components/**/*", "../shared/**/*"]',
                    '"include": ["src/**/*", "components/**/*", "shared/**/*"]',
                )
            ],
        )

        if args.config:
            config_src = Path(args.config).expanduser().resolve()
            if not config_src.exists():
                die(f"config file not found: {config_src}")
            shutil.copy2(config_src, out / "config.json")
            print(f"copied config.json: {out / 'config.json'}")

        print(f"\nRemotion scaffold: {out}")
        print(f"  cd {out}")
        print("  npm install")
        print("  npm run typecheck")

    elif args.stack == "hyperframes":
        example_src = TEMPLATES / "hyperframes" / "example"
        if not example_src.exists():
            die(f"missing template source: {example_src}")
        ignore = shutil.ignore_patterns("node_modules", "dist", "build")
        shutil.copytree(example_src, out, ignore=ignore, dirs_exist_ok=True)
        print(f"\nHyperFrames scaffold: {out}")
        print(f"  open {out / 'index.html'} in a browser or HyperFrames pipeline")
    else:
        die(f"unknown stack: {args.stack}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="replica",
        description="Video Replica Studio CLI.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_analyze = sub.add_parser(
        "analyze", help="Extract frames, detect scenes, and build a motion profile."
    )
    p_analyze.add_argument("video", type=Path)
    p_analyze.add_argument("--out", type=Path, required=True)
    p_analyze.add_argument("--preview", action="store_true", help="Fast low-resolution mode.")
    p_analyze.add_argument("--interval", type=float, default=None)
    p_analyze.set_defaults(func=analyze)

    p_quick = sub.add_parser(
        "quick", help="Fast preview extraction + coarse render diff of two videos."
    )
    p_quick.add_argument("reference", type=Path)
    p_quick.add_argument("candidate", type=Path)
    p_quick.add_argument("--out", type=Path, required=True)
    p_quick.set_defaults(func=quick)

    p_diff = sub.add_parser(
        "diff", help="Full comparison with render diff and optional component crops."
    )
    p_diff.add_argument("reference", type=Path)
    p_diff.add_argument("candidate", type=Path)
    p_diff.add_argument("--out", type=Path, required=True)
    p_diff.add_argument("--crops", type=Path, help="JSON file with {name: [x, y, w, h]} boxes.")
    p_diff.add_argument("--report", action="store_true", help="Copy report templates into --out.")
    p_diff.add_argument("--interval", type=float, default=0.5)
    p_diff.add_argument("--scale", default="480:270")
    p_diff.set_defaults(func=diff)

    p_scaffold = sub.add_parser("scaffold", help="Copy a runnable template project.")
    p_scaffold.add_argument("stack", choices=["remotion", "hyperframes"])
    p_scaffold.add_argument("--out", type=Path, required=True)
    p_scaffold.add_argument(
        "--config",
        type=Path,
        help="JSON config to copy into the project as config.json (Remotion only).",
    )
    p_scaffold.set_defaults(func=scaffold)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
