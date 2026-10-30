"""Overnight mining (CPU), beside overnight_play.py: concept_mine.py on the discovery positions as they arrive.

loop    every --every seconds, once mu.json exists: concept_mine.py lp for S and W, seeds 0 and 1 (four processes; each
        resumes where it stopped, so a pass only does the new positions)
plant   once --plant-at discovery positions have their LP: concept_mine.py plant for S and W. A failure is logged as
        PLANT FAILED and mining stops (the LP or the families cannot be trusted)
final   when overnight_play.py logs "done": the last lp pass, then per model (S and W at once) screen, families, score,
        examples, then report -> results/transcend/divergence/<prefix>-disc-s0/mine/concepts.json, .md
--dry   the final stages now, on the positions so far (timing); their caches are cleared again before the real final.

    python transcend/dynamic/overnight_mine.py
"""
import argparse, json, subprocess, sys, time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402

OV = paths.RUNS / "transcend" / "overnight"
DIV = paths.RUNS / "transcend" / "divergence"
PY = sys.executable
CM = str(Path(__file__).resolve().parent / "concept_mine.py")


def log(a, msg):
    line = f"{datetime.now():%H:%M:%S} [mine] {msg}"
    print(line, flush=True)
    with open(OV / a.name / "progress.log", "a", encoding="utf-8") as fh: fh.write(line + "\n")


def base(a):
    return ["--tag", f"{a.prefix}-disc-s0", "--tag1", f"{a.prefix}-disc-s1", "--source", str(OV / a.name / "disc")]


def run_all(a, cmds, what):
    t0 = time.time()
    ps = [subprocess.Popen([PY, "-u", CM] + c + base(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                           encoding="utf-8", errors="replace", cwd=str(paths.ROOT)) for c in cmds]
    outs = [p.communicate()[0] for p in ps]
    for c, p, o in zip(cmds, ps, outs):
        tail = o.strip().splitlines()[-3:] if o.strip() else []
        if p.returncode: log(a, f"{what} {' '.join(c)} FAILED ({p.returncode}): {' | '.join(tail)}")
        else: log(a, f"{what} {' '.join(c)}: {tail[-1] if tail else ''}")
    return all(p.returncode == 0 for p in ps), time.time() - t0, outs


def lp_pass(a):
    return run_all(a, [["lp", "--model", m, "--seed", str(s)] for m in "SW" for s in (0, 1)], "lp")


def lp_positions(a, m):
    f = DIV / f"{a.prefix}-disc-s0" / "mine" / f"lp-{m}-s0.json"
    return len({r["pos"] for r in json.loads(f.read_text())}) if f.exists() else 0


def final(a, tag):
    mine = DIV / f"{a.prefix}-disc-s0" / "mine"
    for m in "SW":
        for f in (f"screen-{m}.json",):
            if (mine / f).exists(): (mine / f).unlink()                  # screen caches itself; recompute on all positions
    t0 = time.time()
    procs = {}
    for m in "SW":                                                       # one chain per model, both at once
        chain = " && ".join(f'"{PY}" -u "{CM}" {st} --model {m} ' + " ".join(f'"{x}"' if " " in x else x for x in base(a))
                            for st in ("screen", "families", "score", "examples"))
        procs[m] = subprocess.Popen(chain, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                    encoding="utf-8", errors="replace", cwd=str(paths.ROOT))
    ok = True
    for m, p in procs.items():
        o = p.communicate()[0]; (OV / a.name / f"{tag}-{m}.out").write_text(o, encoding="utf-8")
        ok &= p.returncode == 0
        log(a, f"{tag} {m}: {'ok' if p.returncode == 0 else 'FAILED'} ({time.time() - t0:.0f}s): {' | '.join(o.strip().splitlines()[-4:])}")
    if ok:
        good, dt, outs = run_all(a, [["report"]], f"{tag} report")
        ok &= good
    log(a, f"{tag}: {'done' if ok else 'FAILED'} in {(time.time() - t0) / 60:.1f} min")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default="night1")
    ap.add_argument("--prefix", default="ov1")
    ap.add_argument("--every", type=float, default=120)
    ap.add_argument("--plant-at", type=int, default=20)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    prog = OV / a.name / "progress.log"
    if a.dry:
        lp_pass(a); final(a, "dry"); return
    planted = (OV / a.name / "plant.ok").exists()
    while True:
        play_done = prog.exists() and any(" done: " in l and "[mine]" not in l for l in prog.read_text(encoding="utf-8").splitlines())
        if (DIV / f"{a.prefix}-disc-s0" / "S" / "mu.json").exists():
            ok, dt, _ = lp_pass(a)
            n = min(lp_positions(a, "S"), lp_positions(a, "W"))
            log(a, f"lp pass: {n} discovery positions solved ({dt:.0f}s)")
            if not planted and n >= a.plant_at:
                ok, dt, outs = run_all(a, [["plant", "--model", m] for m in "SW"], "plant")
                passed = ok and all("pass = True" in o for o in outs)
                if not passed:
                    log(a, "PLANT FAILED: stopping mining"); (OV / a.name / "plant.failed").write_text("\n".join(outs)); return
                (OV / a.name / "plant.ok").write_text("\n".join(outs)); planted = True; log(a, "plant: passed (S and W)")
        if play_done:
            lp_pass(a); final(a, "final"); return
        time.sleep(a.every)


if __name__ == "__main__":
    main()
