#!/usr/bin/env python
import bisect
from collections import defaultdict, namedtuple
import csv
from typing import List
from operator import itemgetter

Individual = namedtuple("Individual", ["index", "fitness"])

def isDominated(wvalues1: List, wvalues2: List):
    not_equal = False
    for self_wvalue, other_wvalue in zip(wvalues1, wvalues2):
        if self_wvalue > other_wvalue:
            return False
        elif self_wvalue < other_wvalue:
            not_equal = True
    return not_equal

def sortNonDominated(individuals):
    map_fit_ind = defaultdict(list)
    for ind in individuals:
        map_fit_ind[ind.fitness].append(ind)
    fits = list(map_fit_ind.keys())

    current_front = []
    next_front = []
    dominating_fits = defaultdict(int)
    dominated_fits = defaultdict(list)

    # Rank first Pareto front
    for i, fit_i in enumerate(fits):
        for fit_j in fits[i+1:]:
            if isDominated(fit_j, fit_i):
                dominating_fits[fit_j] += 1
                dominated_fits[fit_i].append(fit_j)
            elif isDominated(fit_i, fit_j):
                dominating_fits[fit_i] += 1
                dominated_fits[fit_j].append(fit_i)
        if dominating_fits[fit_i] == 0:
            current_front.append(fit_i)

    fronts = [[]]
    for fit in current_front:
        fronts[-1].extend(map_fit_ind[fit])
    pareto_sorted = len(fronts[-1])

    # Rank the next front until all individuals are sorted
    N = len(individuals)
    while pareto_sorted < N:
        fronts.append([])
        for fit_p in current_front:
            for fit_d in dominated_fits[fit_p]:
                dominating_fits[fit_d] -= 1
                if dominating_fits[fit_d] == 0:
                    next_front.append(fit_d)
                    pareto_sorted += len(map_fit_ind[fit_d])
                    fronts[-1].extend(map_fit_ind[fit_d])
        current_front = next_front
        next_front = []

    return fronts

def sortCSVFile(fpath, output, columns_metrics):
    assert isinstance(fpath, str)
    assert isinstance(columns_metrics, tuple) or isinstance(columns_metrics, list)
    for column in columns_metrics:
        assert isinstance(column, str), column

    columns_metrics = set(columns_metrics)
    to_sort = []
    rows = []
    with open(fpath) as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        fit_index = []
        for column in columns_metrics:
            assert column in header, f"{column} not in {header}"

        for i,column in enumerate(header):
            if column in columns_metrics:
                fit_index.append(i)

        for index, row in enumerate(reader):
            fitnesses = tuple([row[i] for i in fit_index])
            to_sort.append(Individual(index, fitnesses))
            rows.append(row)

    fronts = sortNonDominated(to_sort)
    for front_index, front in enumerate(fronts):
        for elem in front:
            rows[elem.index].append(front_index)

    rows.sort(key=lambda x: x[-1])

    with open(output, 'w') as handle:
        writer = csv.writer(handle)
        writer.writerow(header + ['front'])
        for row in rows:
            writer.writerow(row)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Non-dominated sort.')
    parser.add_argument('-i', '--input_file', type=str, required=True, help='input csv file')
    parser.add_argument('-c', '--columns', type=str, nargs="*", help="columns to optimize over")
    parser.add_argument('-o', '--output_file', type=str, required=True, help='output csv file')

    args = parser.parse_args()

    sortCSVFile(args.input_file, args.output_file, args.columns)
