"""Compare the cumulative Home host suites with the immutable preceding release."""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from run_host94_contract import ROOT, materialize

BASELINE_101 = '5cc1a34d451e88cfb82b7b16daeb2a5976d0021b'
BASELINE_102 = '5703b25caade638b4404570170fe9d19957271ba'


def suite_result(output, status):
    total = re.search(r'^Ran (\d+) tests? in ', output, re.M)
    summary = re.search(r'^(OK|FAILED)(?: \(([^)]+)\))?$', output, re.M)
    cases = re.findall(r'^.*?\(([\w.]+)\) \.\.\. ', output, re.M)
    traces = re.findall(r'^(FAIL|ERROR): ([^\n]+)\n-+\n(.*?)(?=^[-=]{20,}$)', output, re.M | re.S)
    skipped = re.findall(r'^.*?\(([\w.]+)\) \.\.\. skipped ', output, re.M)
    if (not total or not summary or not cases or len(cases) != int(total[1])
            or status != int(summary[1] == 'FAILED')):
        raise ValueError('Incomplete unittest report')
    reported = dict(re.findall(r'(failures|errors|skipped)=(\d+)', summary[2] or ''))
    for kind, count in (('failures', sum(kind == 'FAIL' for kind, _, _ in traces)),
                        ('errors', sum(kind == 'ERROR' for kind, _, _ in traces)),
                        ('skipped', len(skipped))):
        if count != int(reported.get(kind, '0')):
            raise ValueError('Inconsistent unittest report')
    failures = set()
    for kind, case, trace in traces:
        lines = trace.strip().splitlines()
        reason = next((line for line in reversed(lines) if re.match(r'^(?:\w*Error|\w*Exception):', line)), lines[-1])
        if lines[-1].strip() == ': src/plugin.video.xtreammate/addon.xml':
            # The active manifest is independently checked against its package.
            # Its new version changes the observed hash in these frozen snapshots.
            reason = re.sub(r"^AssertionError: '[a-f0-9]{64}' != ", 'Manifest snapshot differs from ', reason)
        failures.add(f'{kind}: {case} | {reason}')
    return set(cases), failures, set(skipped)


def collect(source_commit, checkout, report):
    subprocess.run(['git', 'clone', '--shared', '--quiet', '--no-checkout', str(ROOT), str(checkout)], check=True)
    subprocess.run(['git', 'checkout', '--quiet', '--detach', source_commit], cwd=checkout, check=True)
    archive_count = materialize(ROOT, checkout)
    print(f'{report.name}: {source_commit}, {archive_count} verified historical inputs', flush=True)
    env = dict(os.environ, XCMATE94_REVIEW_ROOT=str(ROOT), PYTHONDONTWRITEBYTECODE='1',
               PYTHONPATH=os.pathsep.join(str(checkout / directory) for directory in ('tests', 'tools')))
    report.mkdir(parents=True, exist_ok=True)
    cases, failures, skipped = set(), set(), set()
    for release in range(75, 85):
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', f'*029{release}.py', '-v'],
            cwd=checkout, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        (report / f'029{release}.log').write_text(result.stdout, encoding='utf-8')
        suite_cases, suite_failures, suite_skips = suite_result(result.stdout, result.returncode)
        cases.update(suite_cases)
        failures.update(suite_failures)
        skipped.update(suite_skips)
    return cases, failures, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    report = parser.parse_args().report.resolve()
    subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', 'src/plugin.video.xtreammate', 'tests', 'tools'],
                   cwd=ROOT, check=True)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    from xml.etree import ElementTree
    version = ElementTree.parse(ROOT / 'src/plugin.video.xtreammate/addon.xml').getroot().get('version')
    previous = BASELINE_102 if version == '0.1.29.103' else BASELINE_101
    subprocess.run(['git', 'merge-base', '--is-ancestor', previous, head], cwd=ROOT, check=True)
    with TemporaryDirectory(prefix='xcmate-home75-') as temporary:
        directory = Path(temporary)
        baseline, historical, prior_skips = collect(previous, directory / 'baseline', report / 'baseline')
        current, failures, skips = collect(head, directory / 'candidate', report / 'candidate')

    summary = dict(baseline_commit=previous, candidate_commit=head,
                   baseline_cases=len(baseline), current_cases=len(current),
                   known_failures=sorted(failures & historical), new_failures=sorted(failures - historical),
                   removed_cases=sorted(baseline - current), new_skips=sorted(skips - prior_skips))
    text = json.dumps(summary, indent=2)
    (report / 'summary.json').write_text(text + '\n', encoding='utf-8')
    print(text, flush=True)
    return int(any(summary[field] for field in ('new_failures', 'removed_cases', 'new_skips')))


if __name__ == '__main__':
    raise SystemExit(main())
