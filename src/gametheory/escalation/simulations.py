import cPickle
import itertools
import math
import multiprocessing as mp
import sys

effective_zero_diff = 1e-11
effective_zero = 1e-10

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

def runSimulationIMap(args):
    return runSimulation(*args)

def goBabyGo(options, num_types, num_thresholds):
    output_base = "{0}/{1}".format(options.output_dir, "{0}")

    stats = open(output_base.format(options.stats_file), "wb")

    pool = mp.Pool(options.pool_size)
    if not options.quiet:
        print "Pool: {0}".format(pool)

    mp.log_to_stderr()

    type_step = 1. / float(num_types + 1)
    thresh_step = 1. / float(num_thresholds + 1)
    strategies = [(i * type_step, j * thresh_step, (j+k) * thresh_step) for i in range(1, num_types + 1) for j in range(1, num_thresholds + 1) for k in range(num_thresholds + 1 - j)]

    if not options.quiet:
        print "Running {0} duplications.".format(options.dup)

    if options.file_dump:
        tasks = [(strategies, output_base.format(options.output_file.format(i + 1)), options.skip) for i in range(options.dup)]
    else:
        tasks = [(strategies, None, options.skip, options.quiet)] * options.dup

    results = pool.imap_unordered(runSimulationIMap, tasks)
    finished_count = 0
    for result in results:
        finished_count += 1
        if not options.quiet:
            print result
        print >>stats, cPickle.dumps(result)
        print >>stats
        stats.flush()
        print "done #{0}".format(finished_count)

    stats.close()

def run():
    from optparse import OptionParser

    oparser = OptionParser()
    oparser.add_option("-d", "--duplications", type="int", action="store", dest="dup", default=1, help="number of duplications")
    oparser.add_option("-o", "--output", action="store", dest="output_dir", default="./output", help="directory to dump output files")
    oparser.add_option("-f", "--filename", action="store", dest="output_file", default="duplication_{0}", help="output file name template")
    oparser.add_option("-g", "--nofiledump", action="store_false", dest="file_dump", default=True, help="do not output duplication files")
    oparser.add_option("-k", "--skip", action="store", type="int", dest="skip", default=1, help="number of generations between dumping output -- 0 for only at the end")
    oparser.add_option("-s", "--statsfile", action="store", dest="stats_file", default="aggregate", help="file for aggregate stats to be dumped")
    oparser.add_option("-m", "--poolsize", action="store", type="int", dest="pool_size", default=2, help="number of parallel computations to undertake")
    oparser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False, help="suppress standard output")
    oparser.add_option("-t", "--types", action="store", type="int", dest="num_types", default=5, help="number of types")
    oparser.add_option("-y", "--thresholds", action="store", type="int", dest="num_thresholds", default=5, help="number of thresholds")

    (options,args) = oparser.parse_args()

    if not options.dup or options.dup <= 0:
        oparser.error("Number of duplications must be positive")

    if not options.num_types or options.num_types < 1:
        oparser.error("Number of types must be at least 1")

    if not options.num_thresholds or options.num_thresholds < 1:
        oparser.error("Number of thresholds must be at least 1")

    goBabyGo(options, options.num_types, options.num_thresholds)

if __name__ == "__main__":
    run()