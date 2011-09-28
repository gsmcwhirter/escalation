import cPickle
import itertools
import math
import multiprocessing as mp
import sys

from gametheory.base.simulation import effective_zero_diff, effective_zero
from gametheory.base.simulation import Simulation as SimBase

class Simulation(SimBase):

    def _setParserOptions(self):
        self._oparser.add_option("-t", "--types", action="store", type="int", dest="num_types", default=5, help="number of types")
        self._oparser.add_option("-y", "--thresholds", action="store", type="int", dest="num_thresholds", default=5, help="number of thresholds")

    def _checkParserOptions(self):
        if not self._options.num_types or self._options.num_types < 1:
            self._oparser.error("Number of types must be at least 1")

        if not self._options.num_thresholds or self._options.num_thresholds < 1:
            self._oparser.error("Number of thresholds must be at least 1")

    def _setData(self):
        self._data['type_step'] = type_step = 1. / float(self._options.num_types + 1)
        self._data['thresh_step'] = thresh_step = 1. / float(self._options.num_thresholds + 1)
        self._data['strategies'] = tuple([(i * type_step, j * thresh_step, (j+k) * thresh_step) for i in range(1, self._options.num_types + 1) for j in range(1, self._options.num_thresholds + 1) for k in range(self._options.num_thresholds + 1 - j)])

    def _buildTask(self):
        return [self._data['strategies']]

    @classmethod
    def runSimulation(cls, strategies, filename = None, output_skip = 1, quiet = False):
        def popEquals(last, this):
            return not any(abs(i - j) >= effective_zero_diff for i, j in itertools.izip(last, this))

        def decideInteraction(strategy1, strategy2):
            return (0.,0.)

        def stepGeneration(last_generation, strategies):
            # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
            # a is background (lifetime) birthrate

            a = 1e-8

            num_strategies = len(strategies)
            fitness = [0] * num_strategies

            for s1 in range(num_strategies):
                for s2 in range(s1 + 1, num_strategies):
                    result = decideInteraction(strategies[s1], strategies[s2])
                    fitness[s1] += result[0]
                    fitness[s2] += result[1]

            average_fitness = math.fsum(fitness[i] * last_generation[i] for i in range(num_strategies))

            new_generation = [(a + fitness[i]) * last_generation[i] / (a + average_fitness) for i in range(num_strategies)]

            for i in range(num_strategies):
                if new_generation[i] < effective_zero:
                    new_generation[i] = 0.

            return new_generation

        import numpy.random.mtrand as rand
        if filename:
            out_stdout = False
            out = open(filename, "w")
        else:
            out_stdout = True
            out = sys.stdout

        dimensions = len(strategies)
        rand.seed()
        initial_population = tuple(rand.dirichlet([1] * dimensions))

        if not out_stdout or not quiet:
            print >>out, "Dimensionality: {0}".format(dimensions)
            print >>out, "Initial State"
            print >>out, initial_population

        last_generation = (0.,)
        this_generation = initial_population
        generation_count = 0

        while not popEquals(last_generation, this_generation):
            generation_count += 1
            last_generation = this_generation
            this_generation = stepGeneration(last_generation, strategies)

            if (not out_stdout or not quiet) and output_skip and generation_count % output_skip == 0:
                print >>out, "-" * 72
                print >>out, "Generation {0}".format(generation_count)
                print >>out, "\t", this_generation
                print >>out
                out.flush()

        if not out_stdout or not quiet:
            print >>out, "=" * 72
            print >>out, "Stable state! ({0} generations)".format(generation_count)
            print >>out, "\t", this_generation
            for i, pop in enumerate(this_generation):
                if pop != 0.:
                    print >>out, "\t\t{0:>5}: {1}".format(i, pop)

        if not out_stdout:
            out.close()

        return (initial_population, this_generation, generation_count)

def runSimulation(strategies, filename = None, output_skip = 1, quiet = False):
    import numpy.random.mtrand as rand
    if filename:
        out_stdout = False
        out = open(filename, "w")
    else:
        out_stdout = True
        out = sys.stdout

    dimensions = len(strategies)
    rand.seed()
    initial_population = tuple(rand.dirichlet([1] * dimensions))

    if not out_stdout or not quiet:
        print >>out, "Dimensionality: {0}".format(dimensions)
        print >>out, "Initial State"
        print >>out, initial_population

    last_generation = (0.,)
    this_generation = initial_population
    generation_count = 0

    while not popEquals(last_generation, this_generation):
        generation_count += 1
        last_generation = this_generation
        this_generation = stepGeneration(last_generation, strategies)

        if (not out_stdout or not quiet) and output_skip and generation_count % output_skip == 0:
            print >>out, "-" * 72
            print >>out, "Generation {0}".format(generation_count)
            print >>out, "\t", this_generation
            print >>out
            out.flush()

    if not out_stdout or not quiet:
        print >>out, "=" * 72
        print >>out, "Stable state! ({0} generations)".format(generation_count)
        print >>out, "\t", this_generation
        for i, pop in enumerate(this_generation):
            if pop != 0.:
                print >>out, "\t\t{0:>5}: {1}".format(i, pop)

    if not out_stdout:
        out.close()

    return (initial_population, this_generation, generation_count)

def run():
    sim = Simulation()
    sim.go()

if __name__ == "__main__":
    run()