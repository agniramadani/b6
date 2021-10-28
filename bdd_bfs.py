# Agni Ramadnai, Fisnik Kuci, Selaudin Agolli
# Since Fisnik visited the corse last year the solution has been adopted from the last year.
import itertools

from task import Task
from search.bdd import *


class BDDSearch(object):
    def __init__(self, task):
        self.task = task
        self.fact_to_id = dict()
        for i, f in enumerate(self.task.facts):
            self.fact_to_id[f] = 2*i
            self.fact_to_id[f + "PRIME"] = 2*i + 1
            # TODO switch the order above with the one below and
            # evaluate the effect in exercise B.5(b)
#            self.fact_to_id[f] = i
#            self.fact_to_id[f + "PRIME"] = i + len(self.task.facts)
        self.id_to_fact = {i : f for f, i in self.fact_to_id.items()}
        self.transition_relation = self.create_transition_relation()

    def state_to_ids(self, state):
        # result = {self.fact_to_id[fact]: fact in state for fact in self.task.facts}
        result = dict()
        for fact in self.task.facts:
            result[self.fact_to_id[fact]] = fact in state
        return result

    def ids_to_state(self, ids):
        # result = {self.id_to_fact[v] for v, value in ids.items() if value}
        result = set()
        for v, value in ids.items():
            if value:
                result.add(self.id_to_fact[v])
        return result

    def get_fact_id(self, fact, primed=False):
        if primed:
            fact = fact + "PRIME"
        return self.fact_to_id[fact]

    def get_atom_bdd(self, fact, primed):
        return bdd_atom(self.get_fact_id(fact, primed))

    def conjunction_to_set(self, conjunction):
        b = one()
        for fact in conjunction:
            fact_bdd = self.get_atom_bdd(fact, False)
            b = bdd_intersection(b, fact_bdd)
        return b

    def create_transition_relation(self):
        t = zero()
        # TODO add your code for exercise B.5(a) here.

        # Note that the task is in STRIPS, so the formula for
        # the transition relation can be simplified to the conjunction
        # of the following formulas:
        #   {v | v in op.preconditions}
        #   {v' | v in op.add_effects}
        #   {not v' | v in op.del_effects \ op.add_effects}
        #   {v <-> v' | v in self.task.facts \ op.del_effects \ op.add_effects}

        # To get the BDD representing a fact, use self.get_atom_bdd.
        # To construct BDDs, use the functions imported from bdd.py.
        # Have a look at that file to see which functions are available.

        # Got little bit help from Professor Malte Helmet on Discord channel on 18th October 2020

        for op in self.task.operators:
            tau_v_o = one()
            for v in op.preconditions:
                tau_v_o = bdd_intersection(tau_v_o, self.get_atom_bdd(v, primed=False))
            for v in op.add_effects:
                tau_v_o = bdd_intersection(tau_v_o, self.get_atom_bdd(v, primed=True))
            for v in op.del_effects:
                if v not in op.add_effects:
                    tau_v_o = bdd_setdifference(tau_v_o, self.get_atom_bdd(v, primed=True))
            for v in self.task.facts:
                if v not in op.del_effects and v not in op.add_effects:
                    v_unchanged = bdd_biimplication(self.get_atom_bdd(v, primed=False), self.get_atom_bdd(v, primed=True))
                    tau_v_o = bdd_intersection(tau_v_o, v_unchanged)
            t = bdd_union(t, tau_v_o)

        return t

    def apply_ops(self, reached):
        b = self.transition_relation

        # TODO add your code for exercise B.5(a) here.

        # Return a BDD that represents the set of states that can be
        # reached in one step from the states represented by the BDD
        # given in the parameter "reached".

        b = bdd_intersection(b, reached)

        for v in self.task.facts:
            b = bdd_forget(b, self.get_fact_id(v, primed=False))
        for v in self.task.facts:
            b = bdd_rename(b, self.get_fact_id(v, primed=True), self.get_fact_id(v, primed=False))

        return b

    def construct_plan(self, reached):
        goal = self.conjunction_to_set(self.task.goals)
        s_ids = bdd_get_ids_of_arbitrary_state(bdd_intersection(goal, reached[-1]))
        plan = []
        for reached_i in reversed(reached[:-1]):
            s = self.ids_to_state(s_ids)
            for op in self.task.operators:
                regr_s = (s - op.add_effects) | op.preconditions
                p = bdd_state(self.state_to_ids(regr_s))
                c = bdd_intersection(p, reached_i)
                if not bdd_equals(c, zero()):
                    s_ids = bdd_get_ids_of_arbitrary_state(c)
                    plan.insert(0, op)
                    break
        return plan

    def run(self):
        goal = self.conjunction_to_set(self.task.goals)
        reached = [bdd_state(self.state_to_ids(self.task.initial_state))]

        # TODO add your code for exercise B.5(a) here.

        # Create new BDDs with self.apply_ops(reached[i]) and append
        # them to the list "reached" in each step.

        # If you find a plan, return the result of
        #     self.construct_plan(reached)
        # otherwise (if the task is unsolvable) return None.


        i = 0
        while True:
            b1 = bdd_intersection(reached[i], goal)
            if not bdd_isempty(b1):
                return self.construct_plan(reached)
            b2 = bdd_union(reached[i], self.apply_ops(reached[i]))
            reached.append(b2)
            if bdd_equals(reached[i+1], reached[i]):
                return None
            i += 1




def bdd_bfs_solve(task):
    search = BDDSearch(task)
    return search.run()

def print_bdd_nodes():
    print ("Amount of BDD Nodes {}".format(len(VAR)))
