#!/usr/bin/env python3
"""CLK-001 adversarial type, algebra, units and provenance fixtures, v1.0.1."""
import argparse
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import tect_clk001_primary as p


def run():
    e = p.load_inputs()
    checks = []
    mutations = [
        (('sources','bothwell','gradient_budget','unit'), '1e-20/m', 'millimetre_metre_swap'),
        (('sources','bothwell','distinct_precision_observable','unit'), '1/mm', 'precision_dimension_swap'),
        (('sources','bothwell','distinct_precision_observable','not_the_redshift_gradient_uncertainty'), False, 'precision_as_gradient_error'),
        (('sources','bothwell','decay_observable','not_a_transition_frequency'), False, 'decay_as_transition'),
        (('sources','chou','clock_species'), 'Al and Be and Mg clocks', 'logic_ions_as_clock_species'),
        (('sources','chou','elevation','height_uncertainty'), '0', 'unreported_height_error_zero'),
        (('holdout','used_for_parameter_fit'), True, 'validation_fit_leak'),
        (('holdout','blind'), True, 'retroactive_blinding'),
        (('holdout','prospective'), True, 'retrospective_as_prospective'),
        (('holdout','prospective_prediction_claim'), True, 'new_prediction_claim'),
        (('holdout','missing_joint_table'), 'Complete joint table observed', 'unmatched_experiments_pooled'),
        (('candidate','physical_readout_owner'), 'Identical units imply same observable', 'readout_owner_invented'),
        (('candidate','time'), 'Proper time', 'time_reinterpretation'),
        (('reference_formula','c_role'), 'TECT predicted', 'inserted_constant_as_prediction'),
        (('sources','bothwell','covariance'), 'All independent', 'covariance_diagonal_assumed'),
        (('sources','chou','covariance'), 'No systematic error', 'statistical_error_as_total')]
    for path, value, label in mutations:
        changed = deepcopy(e)
        target = changed
        for key in path[:-1]: target = target[key]
        target[path[-1]] = value
        try:
            p.validate_semantics(changed)
        except AssertionError:
            checks.append(label)
        else:
            raise AssertionError('Mutation accepted: '+label)
    for table in ([], [[]], [[F(0)]], [[F(1)], [F(1),F(2)]], [[F(1),F(2)],[F(3),F(7)]]):
        try: p.factor(table)
        except ValueError: checks.append('invalid_or_nonfactorizing_table_'+str(len(checks)))
        else: raise AssertionError('Invalid table accepted')
    for values in ((F(0),F(1),F(1),F(1)), (F(1),F(-1),F(1),F(1))):
        try: p.double_ratio(*values)
        except ValueError: checks.append('nonpositive_frequency_'+str(len(checks)))
        else: raise AssertionError('Nonpositive frequency accepted')
    try: p.ratio_interval([(F(0),F(1))]*4)
    except ValueError: checks.append('interval_touching_zero')
    else: raise AssertionError('Zero denominator box accepted')
    # Explicit exact arithmetic hostile fixtures, not empirical data.
    assert p.double_ratio(F(2),F(3),F(4),F(6)) == 1
    assert p.double_ratio(F(2),F(3),F(4),F(7)) != 1
    checks.append('genuine_nonunit_ratio_not_normalization_gauge')
    single = [[F(2),F(3)]]
    assert p.factor(single)
    assert p.double_ratio(F(2),F(3),F(5),F(9)) != 1
    checks.append('single_clock_pass_does_not_force_second_clock')
    original = p.run()['derived']
    wrong_units = F(original['bothwell_M0_gradient_budget_units'])*1000
    assert abs(wrong_units-F(e['sources']['bothwell']['gradient_budget']['known_redshift_mean'])) > 1
    checks.append('thousandfold_unit_error_detected_by_source_value')
    return {'schema':'tect/clk001-run/1.0','role':'hostile','status':'PASS_MUTATIONS_REJECTED',
            'script_sha256':p.sha(Path(__file__)),'primary_sha256':p.sha(Path(p.__file__)),
            'checks':checks,'check_count':len(checks),
            'boundary':'Explicit mutation fixtures and written objections, same-task authorship; not an external hostile referee and not empirical validation.'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=run()
    p.issue_or_check(result,p.RUNS/'hostile.json',args.check)
    print('CLK-001 HOSTILE: PASS',result['check_count'],'checks')
