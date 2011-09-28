import itertools
import math
import sys

from gametheory.base.simulation import effective_zero_diff, effective_zero
from gametheory.base.simulation import Simulation as SimBase

class Simulation(SimBase):

    def _setParserOptions(self):
        self._oparser.add_option("-t", "--types", action="store", type="int", dest="num_types", default=5, help="number of types (default 5)")
        self._oparser.add_option("-y", "--thresholds", action="store", type="int", dest="num_thresholds", default=5, help="number of thresholds (default 5)")
        self._oparser.add_option("-b", "--cost-obs", action="store", type="float", dest="cost_obs", default=0.1, help="cost for observation (default 0.1)")
        self._oparser.add_option("-w", "--cost-win", action="store", type="float", dest="cost_win", default=0.2, help="cost for a fight winner (default 0.2)")
        self._oparser.add_option("-l", "--cost-loss", action="store", type="float", dest="cost_loss", default=0.5, help="cost for a fight loser (default 0.5)")
        self._oparser.add_option("-K", "--update_modulus", action="store", type="float", dest="update_modulus", default=1., help="factor for how strong updates are after observation (default 1)")
        self._oparser.add_option("-P", "--update_correct", action="store", type="float", dest="update_correct", default=1., help="probability updates will be correct (default 1)")

    def _checkParserOptions(self):
        if not self._options.num_types or self._options.num_types < 1:
            self._oparser.error("Number of types must be at least 1")

        if not self._options.num_thresholds or self._options.num_thresholds < 1:
            self._oparser.error("Number of thresholds must be at least 1")

        if self._options.cost_obs < 0.:
            self._oparser.error("Cost for observation must not be negative")

        if self._options.cost_win < 0.:
            self._oparser.error("Cost for winning must not be negative")

        if self._options.cost_loss < 0.:
            self._oparser.error("Cost for losing must not be negative")

        if self._options.update_modulus < 0.:
            self._oparser.error("Update modulus must not be negative")

        if self._options.update_correct < 0. or self._options.update_correct > 1.:
            self._oparser.error("Correct update probability must be between 0 and 1")

    def _setData(self):
        self._data['type_step'] = type_step = 1. / float(self._options.num_types + 1)
        self._data['thresh_step'] = thresh_step = 1. / float(self._options.num_thresholds + 1)
        self._data['strategies'] = tuple([(i * type_step, j * thresh_step, (j+k) * thresh_step) for i in range(1, self._options.num_types + 1) for j in range(1, self._options.num_thresholds + 1) for k in range(self._options.num_thresholds + 1 - j)])

    def _buildTask(self):
        return [self._data['strategies'], self._options.cost_obs, self._options.cost_win, self._options.cost_loss, self._options.update_modulus, self._options.update_correct]

    
def runSimulation(args):
    import numpy.random.mtrand as rand
    rand.seed()

    def popEquals(last, this):
        return not any(abs(i - j) >= effective_zero_diff for i, j in itertools.izip(last, this))

    def decideInteraction(strategy1, strategy2, cost_obs, cost_win, cost_loss, update_modulus, update_correct):
        p1 = 0.5
        p2 = 0.5

        run = False
        fight = False

        obs_costs = 0.

        def player1Wins():
            return rand.uniform(0., 1.) <= (strategy1[0] / (strategy1[0] + strategy2[0]))

        def isFight(prob):
            return rand.uniform(0., 1.) <= prob

        while not run and not fight:
            if (obs_costs >= 1.):
                return (0., 0., False)

            #check for running
            if p1 < strategy1[1] and p2 < strategy2[1]:
                run = True
                return (max(0.5 - obs_costs, 0.), max(0.5 - obs_costs, 0.), False)
            elif p1 < strategy1[1]:
                run = True
                return (max(0.5 - obs_costs, 0.), max(1. - obs_costs, 0.), False)
            elif p2 < strategy2[1]:
                run = True
                return (max(1. - obs_costs, 0.), max(0.5 - obs_costs, 0.), False)

            #check for fighting
            if p1 >= strategy1[2] and p2 >= strategy2[2]:
                fight = True
                if player1Wins():
                    return (max(1. - obs_costs - cost_win, 0.), max(0.5 - obs_costs - cost_loss, 0.), True)
                else:
                    return (max(0.5 - obs_costs - cost_loss, 0.), max(1. - obs_costs - cost_win, 0.), True)
            elif p1 >= strategy1[2]:
                if isFight(p2):
                    fight = True
                    if player1Wins():
                        return (max(1. - obs_costs - cost_win, 0.), max(0.5 - obs_costs - cost_loss, 0.), True)
                    else:
                        return (max(0.5 - obs_costs - cost_loss, 0.), max(1. - obs_costs - cost_win, 0.), True)
                else:
                    run = True
                    return (max(1. - obs_costs, 0.), max(0.5 - obs_costs, 0.), False)
            elif p2 >= strategy2[2]:
                if isFight(p1):
                    fight = True
                    if player1Wins():
                        return (max(1. - obs_costs - cost_win, 0.), max(0.5 - obs_costs - cost_loss, 0.), True)
                    else:
                        return (max(0.5 - obs_costs - cost_loss, 0.), max(1. - obs_costs - cost_win, 0.), True)
                else:
                    run = True
                    return (max(0.5 - obs_costs, 0.), max(1. - obs_costs, 0.), False)

            obs_costs += cost_obs
            adjustment = (strategy1[0] - strategy2[0]) / (2. * update_modulus)
            if rand.uniform(0., 1.) < update_correct:
                p1 += adjustment
                p2 -= adjustment
            else:
                p1 -= adjustment
                p2 += adjustment


    def stepGeneration(last_generation, strategies, cost_obs, cost_win, cost_loss, update_modulus, update_correct):
        # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
        # a is background (lifetime) birthrate

        a = 1e-8

        num_strategies = len(strategies)
        fitness = [0] * num_strategies

        for s1 in range(num_strategies):
            for s2 in range(s1 + 1, num_strategies):
                result = decideInteraction(strategies[s1], strategies[s2], cost_obs, cost_win, cost_loss, update_modulus, update_correct)
                fitness[s1] += result[0]
                fitness[s2] += result[1]

        average_fitness = math.fsum(fitness[i] * last_generation[i] for i in range(num_strategies))

        new_generation = [(a + fitness[i]) * last_generation[i] / (a + average_fitness) for i in range(num_strategies)]

        for i in range(num_strategies):
            if new_generation[i] < effective_zero:
                new_generation[i] = 0.

        return tuple(new_generation)

    def _run(strategies, cost_obs, cost_win, cost_loss, update_modulus, update_correct, filename = None, output_skip = 1, quiet = False):

        if filename:
            out_stdout = False
            out = open(filename, "w")
        else:
            out_stdout = True
            out = sys.stdout

        dimensions = len(strategies)
        initial_population = tuple(rand.dirichlet([1] * dimensions))

        if not out_stdout or not quiet:
            print >>out, "Dimensionality: {0}".format(dimensions)
            print >>out, "Initial State"
            print >>out, initial_population

        last_generation = (0.,)
        this_generation = initial_population
        generation_count = 0
        force_stop = False

        while not popEquals(last_generation, this_generation) and not force_stop:
            if (generation_count >= 1e4):
                force_stop = True
                continue
                
            generation_count += 1
            last_generation = this_generation
            this_generation = stepGeneration(last_generation, strategies, cost_obs, cost_win, cost_loss, update_modulus, update_correct)

            if (not out_stdout or not quiet) and output_skip and generation_count % output_skip == 0:
                print >>out, "-" * 72
                print >>out, "Generation {0}".format(generation_count)
                print >>out, "\t", this_generation
                print >>out
                out.flush()

        if not out_stdout or not quiet:
            print >>out, "=" * 72
            if force_stop:
                print >>out, "Force stop! ({0} generations)".format(generation_count)
            else:
                print >>out, "Stable state! ({0} generations)".format(generation_count)
            print >>out, "\t", this_generation
            for i, pop in enumerate(this_generation):
                if pop != 0.:
                    print >>out, "\t\t{0:>5}: {1:>20}: {2}".format(i, strategies[i], pop)

        if not out_stdout:
            out.close()

        return (initial_population, this_generation, generation_count)

    return _run(*args)

def run():
    sim = Simulation(runSimulation)
    sim.go()

if __name__ == "__main__":
    run()