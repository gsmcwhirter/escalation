import sys
import multiprocessing as mp
import cPickle

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
        print >>out

    #last_generation = ((0.,),(0.,))
    #generation_count = 0
    #while not pop_equals(last_generation, this_generation):
    #    generation_count += 1
    #    last_generation = this_generation
    #    this_generation = step_generation(last_generation[0], last_generation[1], s_payoffs=s_payoffs, r_payoffs=r_payoffs)
    #    #for i in this_generation:
    #    #    assert(abs(math.fsum(i) - 1.) < effective_zero_diff)
    #
    #    if (not out_stdout or not quiet) and output_skip and generation_count % output_skip == 0:
    #        print >>out, "-" * 72
    #        print >>out, "Generation {0}".format(generation_count)
    #        print >>out, "Senders:"
    #        print >>out, "\t", this_generation[0]
    #        print >>out, "Receivers:"
    #        print >>out, "\t", this_generation[1]
    #        print >>out
    #        out.flush()

    #if not out_stdout or not quiet:
    #    print >>out, "=" * 72
    #    print >>out, "Stable state! ({0} generations)".format(generation_count)
    #    print >>out, "Senders:"
    #    print >>out, "\t", this_generation[0]
    #    for i, pop in enumerate(this_generation[0]):
    #        if pop != 0.:
    #            print >>out, "\t\t",i,":", pop
    #    print >>out
    #    print >>out, "Receivers:"
    #    print >>out, "\t", this_generation[1]
    #    for i, pop in enumerate(this_generation[1]):
    #        if pop != 0.:
    #            print >>out, "\t\t",i,":", pop

    if not out_stdout:
        out.close()

    #return ((initial_senders, initial_receivers), this_generation, generation_count)
    return (0,)

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
        #print
        #print "Strategies:"
        #print strategies

    if options.file_dump:
        tasks = [(strategies, output_base % (options.output_file % (i + 1,),), options.skip) for i in range(options.dup)]
    else:
        tasks = [(strategies, None, options.skip, options.quiet)] * options.dup

    results = pool.imap_unordered(runSimulationIMap, tasks)
    finished_count = 0
    for result in results:
        finished_count += 1
        if not options.quiet:
            #print result[2], result[1], result[0]
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
    oparser.add_option("-f", "--filename", action="store", dest="output_file", default="duplication_%i", help="output file name template")
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