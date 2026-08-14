# -*- coding: utf-8 -*-
"""Run every gate and report one verdict.

Four separate checks are easy to half-run, and a skipped one is how a
regression ships. This runs all of them, never stops at the first failure
(you want the whole picture, not the first symptom), and exits non-zero if
any failed.

    py -3 check.py            # all gates
    py -3 check.py --quick    # skip the test suite (the slow one)

Deliberately shells out rather than importing: the suite is Node, and the
audits are meant to be runnable on their own too.
"""
import subprocess, sys, time

GATES = [
    ('test suite',     ['node', 'test.js'],            'node'),
    ('claims audit',   [sys.executable, 'audit_claims.py'],   'py'),
    ('coverage audit', [sys.executable, 'audit_coverage.py'], 'py'),
    ('contrast audit', [sys.executable, 'audit_contrast.py'], 'py'),
    # The Strategy Lab bridge writes strategy records with evidence badges on
    # them, so its mapping rules are an honesty surface like any other. Builds
    # its own synthetic database, so it runs without the Lab present.
    ('sync bridge',    [sys.executable, 'test_sync.py'],      'py'),
]


def run(name, cmd):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        return name, None, '%s not found on PATH' % cmd[0], 0.0
    except subprocess.TimeoutExpired:
        return name, None, 'timed out', time.time() - t0
    out = (p.stdout or '') + (p.stderr or '')
    # one interesting line per gate rather than the whole dump
    summary = ''
    for line in reversed(out.strip().splitlines()):
        if any(k in line for k in ('PASSED', 'FAILED', 'TOTAL BAN HITS',
                                   'pairs below AA', 'terms:', 'unwritten')):
            summary = line.strip()
            break
    if not summary:
        lines = out.strip().splitlines()
        summary = lines[-1].strip() if lines else '(no output)'
    return name, p.returncode, summary, time.time() - t0


def main():
    quick = '--quick' in sys.argv
    gates = [g for g in GATES if not (quick and g[0] == 'test suite')]
    results, failed = [], 0
    for name, cmd, _kind in gates:
        name, code, summary, secs = run(name, cmd)
        ok = (code == 0)
        if not ok:
            failed += 1
        results.append((name, ok, code, summary, secs))

    width = max(len(r[0]) for r in results)
    print('')
    for name, ok, code, summary, secs in results:
        print('%-*s  %-4s  %5.1fs  %s'
              % (width, name, 'ok' if ok else 'FAIL', secs, summary))
    print('')
    if failed:
        print('%d of %d gates FAILED — nothing ships until these are green.'
              % (failed, len(results)))
    else:
        print('all %d gates green.' % len(results))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
