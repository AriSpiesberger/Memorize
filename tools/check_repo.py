#!/usr/bin/env python3
"""Repo health check. Run it before pushing:

    python tools/check_repo.py

Standard library only, so any Python 3.9+ can run it. It looks at every file git
would commit (tracked, plus untracked files that are not ignored):

  compile     every .py file compiles
  modal       only chess_beyond/modal/ imports `modal`; nothing outside that folder
              imports from it; and the Modal files import nothing from the labs
              (they run lab scripts as subprocesses, so the labs stay standalone)
  models      no model weights or checkpoints (.safetensors, .pt, .ckpt, ...)
  size        no file over 5 MB
  links       relative links in READMEs point at files that exist, and #anchors
              at headings that exist
  duplicates  no function is copied into a second file (the same code after
              renaming variables, 4 lines or more)

Exits 1 if any check fails. To run it automatically before every push:

    ln -s ../../tools/check_repo.py .git/hooks/pre-push
"""
import ast
import copy
import hashlib
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODAL_DIR = "chess_beyond/modal/"
MODEL_EXT = {".safetensors", ".pt", ".pth", ".ckpt", ".gguf", ".onnx", ".bin"}
MAX_BYTES = 5 * 1024 * 1024
MIN_DUP_LINES = 4


def files():
    out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split("\n")
    return sorted(f for f in out if f and (ROOT / f).is_file())


def imported_names(tree):
    """Top-level module names a file imports (`import a.b` and `from a.b import c` give `a`)."""
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            names.add(n.module.split(".")[0])
            names |= {a.name for a in n.names}           # `from transcend import puzzles`
    return names


def check_compile(py, trees, fail):
    for f in py:
        try:
            trees[f] = ast.parse((ROOT / f).read_text(encoding="utf-8"), filename=f)
            compile(trees[f], f, "exec")
        except SyntaxError as e:
            fail("compile", f"{f}:{e.lineno}: {e.msg}")


def check_modal(py, trees, fail):
    modal_files = [f for f in py if f.startswith(MODAL_DIR)]
    modal_modules = {Path(f).stem for f in modal_files}
    lab_modules = {Path(f).stem for f in py if not f.startswith(MODAL_DIR)}
    lab_modules |= {Path(f).parts[i] for f in py if not f.startswith(MODAL_DIR) for i in range(len(Path(f).parts) - 1)}
    for f, tree in trees.items():
        names = imported_names(tree)
        if f.startswith(MODAL_DIR):
            for name in sorted(names & lab_modules - modal_modules):
                fail("modal", f"{f} imports lab code `{name}`; call the lab script as a subprocess instead")
        else:
            if "modal" in names:
                fail("modal", f"{f} imports `modal`; Modal code belongs in {MODAL_DIR}")
            for name in sorted(names & modal_modules):
                fail("modal", f"{f} imports `{name}` from {MODAL_DIR}; the labs must not depend on Modal code")


def check_models_and_size(all_files, fail):
    for f in all_files:
        if Path(f).suffix.lower() in MODEL_EXT:
            fail("models", f"{f} is a model file; weights stay out of git")
        size = (ROOT / f).stat().st_size
        if size > MAX_BYTES:
            fail("size", f"{f} is {size / 2**20:.1f} MB")


def slug(heading):
    """GitHub's anchor for a markdown heading."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(md_path):
    text = md_path.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)                # headings in code blocks don't count
    return {slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.*?)\s*#*\s*$", text, re.M)}


def check_links(all_files, fail):
    for f in all_files:
        if not f.lower().endswith(".md"):
            continue
        md = ROOT / f
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
        for m in re.finditer(r"\]\(([^)\s]*)\)", text):
            link = m.group(1)
            if not link or re.match(r"[a-z]+:", link):                # http(s):, mailto:, ...
                continue
            path, _, anchor = link.partition("#")
            target = (md.parent / path).resolve() if path else md
            if not target.exists():
                fail("links", f"{f}: `{link}` points at a missing file")
            elif anchor and target.suffix.lower() == ".md" and anchor not in anchors(target):
                fail("links", f"{f}: `{link}` points at a missing heading")


class _Canon(ast.NodeTransformer):
    """Rename arguments and assigned names in order of appearance, so copies that only
    differ in variable names compare equal."""

    def __init__(self):
        self.names = {}

    def _rename(self, name):
        return self.names.setdefault(name, f"v{len(self.names)}")

    def visit_arg(self, node):
        node.arg, node.annotation = self._rename(node.arg), None
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)) or node.id in self.names:
            node.id = self._rename(node.id)
        return node


def check_duplicates(trees, fail):
    seen = defaultdict(list)
    for f, tree in trees.items():
        for n in ast.walk(tree):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if n.end_lineno - n.lineno + 1 < MIN_DUP_LINES:
                continue
            m = copy.deepcopy(n)
            if m.body and isinstance(m.body[0], ast.Expr) and isinstance(getattr(m.body[0], "value", None), ast.Constant) \
                    and isinstance(m.body[0].value.value, str):
                m.body = m.body[1:] or [ast.Pass()]                 # docstrings don't count
            m.name, m.decorator_list, m.returns = "_", [], None
            key = hashlib.md5(ast.dump(_Canon().visit(m), annotate_fields=False).encode()).hexdigest()
            seen[key].append((f, n.lineno, n.name))
    for copies in seen.values():
        if len({f for f, _, _ in copies}) > 1:
            where = ", ".join(f"{f}:{line} {name}()" for f, line, name in copies)
            fail("duplicates", f"same function in several files: {where}; keep one and import it")


def main():
    os.chdir(ROOT)
    problems = defaultdict(list)
    fail = lambda check, msg: problems[check].append(msg)
    all_files = files()
    py = [f for f in all_files if f.endswith(".py")]
    trees = {}
    check_compile(py, trees, fail)
    check_modal(py, trees, fail)
    check_models_and_size(all_files, fail)
    check_links(all_files, fail)
    check_duplicates(trees, fail)

    for check in ("compile", "modal", "models", "size", "links", "duplicates"):
        msgs = problems.get(check, [])
        print(f"{'ok  ' if not msgs else 'FAIL'}  {check}")
        for msg in msgs:
            print(f"        {msg}")
    print(f"\n{len(all_files)} files, {len(py)} Python files checked")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
