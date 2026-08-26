#!/usr/bin/env python3
"""Independent reconstruction of EXP-001201.

The current audit logic is rebuilt on the previous audit's independently
implemented oscillator/term primitives, without importing the EXP-001201
primary module.  This keeps the signed grouping and reverse-order checks on a
separate computational lane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_spatial_source_spectral_window_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spatial-source-spectral-window-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-independent-{SLUG}" / "independent.json"
PHYSICAL_KEYS = ("c", "chi", "r", "g", "lambda", "hbar")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_state_weighted_commutator_sum_audit_independent as base  # noqa: E402


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_fixture() -> tuple[dict[str, Any], list[dict[str, str]]]:
    current_path = MANIFEST
    chain: list[dict[str, str]] = []
    while True:
        current = json.loads(current_path.read_text(encoding="utf-8"))
        source = current.get("source_fixture")
        if not isinstance(source, dict) or "manifest" not in source:
            raise ValueError(f"source fixture chain ended before physical fixture: {current_path}")
        next_path = REPO / str(source["manifest"])
        chain.append({"path": next_path.relative_to(REPO).as_posix(), "sha256": normalized_sha256(next_path)})
        if all(key in source for key in PHYSICAL_KEYS):
            return source, chain
        current_path = next_path


def source_supports(volume: int, source_manifest: dict[str, Any]) -> list[tuple[int, ...]]:
    return [tuple(int(site) for site in support) for support in source_manifest["source_supports_by_volume"][str(volume)]]


def term_groups(order: list[tuple[str, tuple[int, ...]]], volume: int, cutoff: int, fixture: dict[str, Any]) -> tuple[dict[tuple[int, ...], list[np.ndarray]], float]:
    groups: dict[tuple[int, ...], list[np.ndarray]] = {}
    absolute_sum = 0.0
    for left_index, left_spec in enumerate(order):
        left_support = set(left_spec[1])
        for right_spec in order[left_index + 1 :]:
            right_support = set(right_spec[1])
            if left_support.isdisjoint(right_support):
                continue
            union = tuple(sorted(left_support | right_support))
            value = base.commutator(base.local_term(left_spec, list(union), cutoff, fixture), base.local_term(right_spec, list(union), cutoff, fixture))
            groups.setdefault(union, []).append(value)
            absolute_sum += base.operator_norm(value)
    return groups, absolute_sum



def window_metric(matrix: np.ndarray, weight_power: np.ndarray, rho_sqrt: np.ndarray, projector: np.ndarray, rho: np.ndarray, shifted: np.ndarray, threshold: float, volume: int, tolerance: float) -> dict[str, Any]:
    selected = shifted <= threshold + tolerance
    rank = int(np.count_nonzero(selected))
    projected = projector @ rho_sqrt @ projector
    mass = float(np.real(np.trace(projector @ rho)))
    signed = base.weighted_two_sided(matrix, weight_power, projected)
    conditional = signed / max(np.sqrt(max(mass, 0.0)), np.finfo(float).tiny)
    if rank <= 0 or not np.isfinite(mass) or mass <= -tolerance or mass > 1.0 + tolerance:
        raise AssertionError(f'invalid spectral window threshold={threshold}: rank={rank}, mass={mass}')
    if not all(np.isfinite(float(value)) and float(value) >= -tolerance for value in (signed, conditional)):
        raise AssertionError(f'non-finite projected weighted norm threshold={threshold}')
    return {'energy_threshold': threshold, 'rank': rank, 'window_mass': mass, 'tail_mass': max(0.0, 1.0 - mass), 'signed_weighted': signed, 'signed_weighted_per_site': signed / volume, 'conditional_signed_weighted': conditional, 'conditional_signed_weighted_per_site': conditional / volume}


def row(volume: int, cutoff: int, beta: float, fixture: dict[str, Any], source_manifest: dict[str, Any], exponent: float, energy_windows: list[float], max_union_size: int, tolerance: float, positivity_tolerance: float, orientation_tolerance: float, norm_floor: float) -> dict[str, Any]:
    declared = base.specs(volume)
    reversed_order = list(reversed(declared))
    forward_groups, absolute_raw_sum = term_groups(declared, volume, cutoff, fixture)
    reverse_groups, reverse_absolute_raw_sum = term_groups(reversed_order, volume, cutoff, fixture)
    if set(forward_groups) != set(reverse_groups):
        raise AssertionError('forward and reverse union-group keys differ')
    sources = source_supports(volume, source_manifest)
    source_sets = [set(source) for source in sources]
    selected_unions = [union for union in sorted(forward_groups) if len(union) <= max_union_size and any(not set(union).isdisjoint(source) for source in source_sets)]
    if not selected_unions:
        raise AssertionError(f'no source-touching unions for V={volume}')
    union_rows: list[dict[str, Any]] = []
    union_sum = {'signed_raw_sum': 0.0, 'signed_gibbs_sum': 0.0, 'signed_weighted_sum': 0.0, 'absolute_raw_sum': 0.0, 'absolute_gibbs_sum': 0.0, 'absolute_weighted_sum': 0.0}
    orientation_raw_residual = orientation_gibbs_difference = orientation_weighted_difference = 0.0
    for union in selected_unions:
        forward = sum(forward_groups[union], np.zeros_like(forward_groups[union][0]))
        reverse = sum(reverse_groups[union], np.zeros_like(reverse_groups[union][0]))
        local_h = base.induced_hamiltonian(list(union), volume, cutoff, fixture)
        energy_values, energy_vectors = np.linalg.eigh(base.hermitian(local_h))
        shifted = energy_values - float(np.min(energy_values))
        rho = base.gibbs(local_h, beta)
        rho_sqrt = base.spectral_power(rho, 0.5)
        k_power = base.spectral_power(base.positive_weight(local_h), exponent)
        if float(np.min(np.linalg.eigvalsh(base.positive_weight(local_h)))) < 1.0 - positivity_tolerance:
            raise AssertionError(f'positive shift failed for union {union}')
        signed_raw = base.operator_norm(forward); signed_gibbs = base.two_sided_gibbs(forward, rho); signed_weighted = base.weighted_two_sided(forward, k_power, rho_sqrt)
        reverse_raw = base.operator_norm(reverse); reverse_gibbs = base.two_sided_gibbs(reverse, rho); reverse_weighted = base.weighted_two_sided(reverse, k_power, rho_sqrt)
        absolute_raw = sum(base.operator_norm(value) for value in forward_groups[union]); absolute_gibbs = sum(base.two_sided_gibbs(value, rho) for value in forward_groups[union]); absolute_weighted = sum(base.weighted_two_sided(value, k_power, rho_sqrt) for value in forward_groups[union])
        finite_values = (signed_raw, signed_gibbs, signed_weighted, reverse_raw, reverse_gibbs, reverse_weighted, absolute_raw, absolute_gibbs, absolute_weighted)
        if not all(np.isfinite(value) and value >= -norm_floor for value in finite_values):
            raise AssertionError(f'non-finite source union at V={volume}, n={cutoff}, beta={beta}, union={union}')
        orientation_raw_residual = max(orientation_raw_residual, base.operator_norm(forward + reverse))
        orientation_gibbs_difference = max(orientation_gibbs_difference, abs(signed_gibbs - reverse_gibbs))
        orientation_weighted_difference = max(orientation_weighted_difference, abs(signed_weighted - reverse_weighted))
        for key, value in (('signed_raw_sum', signed_raw), ('signed_gibbs_sum', signed_gibbs), ('signed_weighted_sum', signed_weighted), ('absolute_raw_sum', absolute_raw), ('absolute_gibbs_sum', absolute_gibbs), ('absolute_weighted_sum', absolute_weighted)):
            union_sum[key] += value
        group_windows: dict[str, dict[str, Any]] = {}
        for threshold in energy_windows:
            key = format(threshold, 'g')
            selector = shifted <= threshold + tolerance
            projector = energy_vectors[:, selector] @ energy_vectors[:, selector].conj().T
            signed_window = window_metric(forward, k_power, rho_sqrt, projector, rho, shifted, threshold, volume, tolerance)
            absolute_window = sum(window_metric(value, k_power, rho_sqrt, projector, rho, shifted, threshold, volume, tolerance)['signed_weighted'] for value in forward_groups[union])
            signed_window['absolute_weighted'] = absolute_window
            signed_window['absolute_weighted_per_site'] = absolute_window / volume
            signed_window['signed_to_absolute'] = signed_window['signed_weighted'] / max(absolute_window, np.finfo(float).tiny)
            group_windows[key] = signed_window
        labels = ['-'.join(map(str, source)) for source in sources if set(union) & set(source)]
        union_rows.append({'union': list(union), 'union_key': '-'.join(map(str, union)), 'pair_count': len(forward_groups[union]), 'source_labels': labels, 'signed_raw': signed_raw, 'signed_gibbs': signed_gibbs, 'signed_weighted': signed_weighted, 'absolute_raw': absolute_raw, 'absolute_gibbs': absolute_gibbs, 'absolute_weighted': absolute_weighted, 'reverse_raw': reverse_raw, 'reverse_gibbs': reverse_gibbs, 'reverse_weighted': reverse_weighted, 'orientation_raw_residual': base.operator_norm(forward + reverse), 'orientation_gibbs_difference': abs(signed_gibbs - reverse_gibbs), 'orientation_weighted_difference': abs(signed_weighted - reverse_weighted), 'windows': group_windows})
    for key in ('signed_raw_sum', 'signed_gibbs_sum', 'signed_weighted_sum', 'absolute_raw_sum', 'absolute_gibbs_sum', 'absolute_weighted_sum'):
        union_sum[key + '_per_union_count'] = union_sum[key] / len(selected_unions)
    return {'volume': volume, 'cutoff': cutoff, 'beta': beta, 'group_count': len(union_rows), 'pair_count': sum(item['pair_count'] for item in union_rows), 'context_count': len(union_rows), 'union_sum': union_sum, 'groups': union_rows, 'source_supports': [list(source) for source in sources], 'orientation_raw_residual': orientation_raw_residual, 'orientation_gibbs_difference': orientation_gibbs_difference, 'orientation_weighted_difference': orientation_weighted_difference, 'absolute_raw_sum_forward': absolute_raw_sum, 'absolute_raw_sum_reverse': reverse_absolute_raw_sum, 'weight_exponent': exponent}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    fixture, chain = load_fixture()
    source_manifest, audit, scope = manifest['source_fixture'], manifest['audit_fixture'], manifest['scope']
    volumes = [int(value) for value in source_manifest['volume_values']]
    cutoffs = [int(value) for value in source_manifest['cutoff_values']]
    betas = [float(value) for value in source_manifest['beta_values']]
    energy_windows = [float(value) for value in audit['energy_windows']]
    tail_cutoff_start = int(audit['tail_cutoff_start'])
    max_union_size = int(audit['max_union_size'])
    exponent = float(Fraction(str(audit['weight_exponent'])))
    tolerance = float(audit['localization_tolerance'])
    positivity_tolerance = float(audit['positivity_tolerance'])
    orientation_tolerance = float(audit['orientation_tolerance'])
    norm_floor = float(audit['commutator_floor'])
    checks: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f'{name}: actual={actual!r}, expected={expected!r}')
        checks.append({'name': name, 'group': group, 'status': 'PASS', 'actual': str(actual), 'expected': str(expected)})
    check('identity', manifest['exploration_id'] == 'EXP-001201' and manifest['task_id'] == 'T-054' and manifest['claim_bearing'] is False, [manifest['exploration_id'], manifest['task_id'], manifest['claim_bearing']], 'EXP-001201/T-054/false', 'provenance')
    check('source chain', len(chain) >= 4 and all(Path(item['path']).is_file() for item in chain), chain, 'physical fixture chain present', 'provenance')
    check('physical fixture', all(key in fixture for key in PHYSICAL_KEYS), sorted(fixture), PHYSICAL_KEYS, 'fixture')
    check('graph volumes', volumes == [2, 4, 6] and all(base.graph_edges(volume) for volume in volumes), volumes, 'registered Q3 volumes', 'fixture')
    check('cutoff grid', cutoffs == [3, 4, 5, 6, 8], cutoffs, 'declared spatial stress cutoff grid', 'fixture')
    check('beta grid', betas == [0.5, 2.0], betas, 'declared endpoint beta grid', 'fixture')
    check('energy-window grid', energy_windows == [0.5, 2.0, 4.0], energy_windows, 'declared fixed-energy windows', 'fixture')
    check('tail cutoff', tail_cutoff_start == 5 and tail_cutoff_start in cutoffs, tail_cutoff_start, 'registered tail cutoff', 'fixture')
    check('union size', max_union_size == 3, max_union_size, '<=3', 'fixture')
    check('source support coverage', all(source_supports(volume, source_manifest) for volume in volumes), {volume: source_supports(volume, source_manifest) for volume in volumes}, 'nonempty source supports', 'fixture')
    check('scope firewall', scope['finite_spatial_source_rows_closed'] and scope['finite_union_level_window_rows_closed'] and scope['finite_reverse_order_antisymmetry_closed'] and scope['finite_window_mass_rank_closed'] and scope['finite_spatial_tail_spread_diagnostic_closed'] and not scope['candidate_source_volume_uniform_bound_closed'] and not scope['global_gibbs_state_transfer_closed'] and not scope['common_core_operator_embedding_closed'] and not scope['pre_a_closed'], scope, 'finite union-level spatial proxy only', 'scope')
    rows = []
    for volume in volumes:
        reference = base.reference_localization(volume, cutoffs[0], fixture, tolerance)
        check(f'V={volume} reference localization', reference <= tolerance, reference, f'<={tolerance}', 'locality')
        for beta in betas:
            for cutoff in cutoffs:
                value = row(volume, cutoff, beta, fixture, source_manifest, exponent, energy_windows, max_union_size, tolerance, positivity_tolerance, orientation_tolerance, norm_floor)
                check(f'V={volume} n={cutoff} beta={beta} finite', all(np.isfinite(float(value['union_sum'][key])) and float(value['union_sum'][key]) >= -norm_floor for key in ('signed_raw_sum', 'signed_gibbs_sum', 'signed_weighted_sum', 'absolute_raw_sum', 'absolute_gibbs_sum', 'absolute_weighted_sum')), value['union_sum'], 'finite union sums', 'numeric')
                check(f'V={volume} n={cutoff} beta={beta} coverage', value['pair_count'] > 0 and value['group_count'] > 0 and value['context_count'] == value['group_count'], [value['pair_count'], value['group_count'], value['context_count']], '>0 and one context per union', 'coverage')
                check(f'V={volume} n={cutoff} beta={beta} orientation', value['orientation_raw_residual'] <= orientation_tolerance and value['orientation_gibbs_difference'] <= orientation_tolerance and value['orientation_weighted_difference'] <= orientation_tolerance, [value['orientation_raw_residual'], value['orientation_gibbs_difference'], value['orientation_weighted_difference']], f'<={orientation_tolerance}', 'orientation')
                check(f'V={volume} n={cutoff} beta={beta} source labels', all(item['source_labels'] for item in value['groups']), value['groups'], 'each union touches a registered source', 'source')
                check(f'V={volume} n={cutoff} beta={beta} windows', all(set(item['windows']) == {format(window, 'g') for window in energy_windows} and all(window['rank'] > 0 and -tolerance <= float(window['window_mass']) <= 1.0 + tolerance for window in item['windows'].values()) for item in value['groups']), value['groups'], 'positive ranks/masses on declared windows', 'window')
                rows.append({'reference_localization_residual': reference, **value})
    summaries = []
    threshold = float(audit['tail_stability_ratio_threshold'])
    keys = sorted({(int(item['volume']), float(item['beta']), tuple(group['union'])) for item in rows for group in item['groups']})
    for volume, beta, union in keys:
        for energy in energy_windows:
            key = format(energy, 'g')
            selected = []
            for item in rows:
                if int(item['volume']) != volume or float(item['beta']) != beta:
                    continue
                selected.extend({**group['windows'][key], 'cutoff': item['cutoff'], 'volume': volume, 'beta': beta, 'union': list(union)} for group in item['groups'] if tuple(group['union']) == union)
            tail = [item for item in selected if int(item['cutoff']) >= tail_cutoff_start]
            signed = [float(item['signed_weighted_per_site']) for item in tail]
            conditional = [float(item['conditional_signed_weighted_per_site']) for item in tail]
            ratio = max(signed) / max(min(signed), np.finfo(float).tiny)
            conditional_ratio = max(conditional) / max(min(conditional), np.finfo(float).tiny)
            summary = {'volume': volume, 'beta': beta, 'union': list(union), 'energy_threshold': energy, 'cutoff_first': cutoffs[0], 'cutoff_last': cutoffs[-1], 'tail_cutoff_start': tail_cutoff_start, 'tail_row_count': len(tail), 'signed_weighted_tail_max_per_site': max(signed), 'signed_weighted_tail_min_per_site': min(signed), 'tail_stability_ratio': ratio, 'conditional_tail_stability_ratio': conditional_ratio, 'stability_threshold': threshold, 'tail_stable': ratio <= threshold and conditional_ratio <= threshold, 'window_mass_min': min(float(item['window_mass']) for item in selected), 'window_mass_max': max(float(item['window_mass']) for item in selected), 'rank_min': min(int(item['rank']) for item in selected), 'rank_max': max(int(item['rank']) for item in selected)}
            summaries.append(summary)
            check(f'V={volume} beta={beta} U={union} E={energy} summary', len(selected) == len(cutoffs) and len(tail) == sum(int(cutoff >= tail_cutoff_start) for cutoff in cutoffs) and np.isfinite(ratio) and np.isfinite(conditional_ratio), summary, 'finite union summary', 'scaling')
    diagnostic = {'interpretation': 'finite union-level spatial/source spectral-window diagnostic; not a global state or asymptotic theorem', 'row_count': len(rows), 'summary_count': len(summaries), 'unstable_summary_count': sum(not item['tail_stable'] for item in summaries), 'all_contexts_tail_stable': all(item['tail_stable'] for item in summaries), 'maximum_tail_stability_ratio': max(item['tail_stability_ratio'] for item in summaries), 'maximum_conditional_tail_stability_ratio': max(item['conditional_tail_stability_ratio'] for item in summaries), 'candidate_source_volume_uniform_bound': 'not established by this audit', 'global_gibbs_state_transfer': 'open', 'common_core_operator_embedding': 'open', 'actual_q3_trotter_defect': 'open'}
    check('finite-only diagnostic', diagnostic['summary_count'] > 0 and diagnostic['candidate_source_volume_uniform_bound'] == 'not established by this audit' and diagnostic['global_gibbs_state_transfer'] == 'open' and diagnostic['common_core_operator_embedding'] == 'open' and diagnostic['actual_q3_trotter_defect'] == 'open', diagnostic, 'finite-only semantics', 'scope')
    check('QFT firewall', not scope['candidate_source_volume_uniform_bound_closed'] and not scope['global_gibbs_state_transfer_closed'] and not scope['common_core_operator_embedding_closed'] and not scope['actual_q3_trotter_defect_closed'] and not scope['actual_q3_thermodynamic_history_closed'] and not scope['common_alpha_closed'] and not scope['pre_a_closed'], scope, 'spatial/window/QFT gates remain open', 'scope')
    return {'schema': 'tect/foundation-audit/1.0', 'run_kind': 'independent', 'audit_id': 'PA-CP1-ST8-Q3LOCK-SPATIAL-SOURCE-SPECTRAL-WINDOW-STRESS', 'claim_id': manifest['claim_ids'][0], 'task_id': manifest['task_id'], 'exploration_id': manifest['exploration_id'], 'verdict': 'PASS', 'passed': len(checks), 'assertion_count': len(checks), 'assertions': checks, 'derived': {'source_chain': chain, 'row_count': len(rows), 'summary_count': len(summaries), 'rows': rows, 'summary': summaries, 'energy_windows': energy_windows, 'tail_cutoff_start': tail_cutoff_start, 'finite_spatial_source_rows_closed': True, 'finite_union_level_window_rows_closed': True, 'finite_reverse_order_antisymmetry_closed': True, 'finite_window_mass_rank_closed': True, 'finite_spatial_tail_spread_diagnostic_closed': True, 'candidate_source_volume_uniform_bound_closed': False, 'global_gibbs_state_transfer_closed': False, 'common_core_operator_embedding_closed': False, 'actual_q3_trotter_defect_closed': False, 'actual_q3_thermodynamic_history_closed': False, 'common_alpha_closed': False, 'pre_a_closed': False, 'sector_a_closed': False, 'diagnostic': diagnostic}, 'boundary': scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f'INDEPENDENT SPATIAL-SOURCE-SPECTRAL-WINDOW PASS {payload["passed"]}/{payload["assertion_count"]} rows={payload["derived"]["row_count"]} summaries={payload["derived"]["summary_count"]}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())