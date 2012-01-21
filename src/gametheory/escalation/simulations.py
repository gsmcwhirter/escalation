import numpy.random as rand

from gametheory.base.dynamics.discrete_replicator import OnePopDiscreteReplicatorDynamics as OPDRD
from gametheory.base.simulation import SimulationBatch as SimBatchBase

class SimulationBatch(SimBatchBase):
    
    def _add_listeners(self):

        def _set_options(this):
            this.oparser.add_option("-t", "--types", action="store", type="int", dest="num_types", default=5, help="number of types (default 5)")
            this.oparser.add_option("-y", "--thresholds", action="store", type="int", dest="num_thresholds", default=5, help="number of thresholds (default 5)")
            this.oparser.add_option("-b", "--cost-obs", action="store", type="float", dest="cost_obs", default=0.1, help="cost for observation (default 0.1)")
            this.oparser.add_option("-w", "--cost-win", action="store", type="float", dest="cost_win", default=0.2, help="cost for a fight winner (default 0.2)")
            this.oparser.add_option("-l", "--cost-loss", action="store", type="float", dest="cost_loss", default=0.5, help="cost for a fight loser (default 0.5)")
            this.oparser.add_option("-k", "--update_modulus", action="store", type="float", dest="update_modulus", default=1., help="factor for how strong updates are after observation (default 1)")
            this.oparser.add_option("-p", "--update_correct", action="store", type="float", dest="update_correct", default=1., help="probability updates will be correct (default 1)")

        def _check_options(this):
            if not this.options.num_types or this.options.num_types < 1:
                this.oparser.error("Number of types must be at least 1")

            if not this.options.num_thresholds or this.options.num_thresholds < 1:
                this.oparser.error("Number of thresholds must be at least 1")

            if this.options.cost_obs < 0.:
                this.oparser.error("Cost for observation must not be negative")

            if this.options.cost_win < 0.:
                this.oparser.error("Cost for winning must not be negative")

            if this.options.cost_loss < 0.:
                this.oparser.error("Cost for losing must not be negative")

            if this.options.update_modulus < 0.:
                this.oparser.error("Update modulus must not be negative")

            if this.options.update_correct < 0. or this.options.update_correct > 1.:
                this.oparser.error("Correct update probability must be between 0 and 1")

        def _set_data(this):
            this.data['type_step'] = type_step = 1. / float(this.options.num_types + 1)
            this.data['thresh_step'] = thresh_step = 1. / float(this.options.num_thresholds + 1)
            
            this._simulation_class.types = tuple([(i * type_step, j * thresh_step, (j+k) * thresh_step) for i in range(1, this.options.num_types + 1) for j in range(1, this.options.num_thresholds + 1) for k in range(this.options.num_thresholds + 1 - j)]) 

            this.data['cost_obs'] = this.options.cost_obs
            this.data['cost_win'] = this.options.cost_win
            this.data['cost_loss'] = this.options.cost_loss
            this.data['update_modulus'] = this.options.update_modulus
            this.data['update_correct'] = this.options.update_correct
            
        self.on('oparser set up', _set_options)
        self.on('options parsed', _check_options)
        self.on('options parsed', _set_data)

class Simulation(OPDRD):
    
    background_rate = 1e-8
    
    def _add_listeners(self):
        def generation_handler(this, num, thispop, lastpop):
            if num >= 1e4:
                this.force_stop = True
        
        self.on('generation', generation_handler)

    def _interaction(self, my_place, profile):
        
        strategy1 = self.types[profile[my_place]]
        strategy2 = self.types[profile[my_place]]
        
        cost_obs = self.data['cost_obs']
        cost_win = self.data['cost_win']
        cost_loss = self.data['cost_loss']
        update_modulus = self.data['update_modulus']
        update_correct = self.data['update_correct']

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
                res = (0., 0., False)[my_place]
                self.emit('interaction', self, res, False)
                return res

            #check for running
            if p1 < strategy1[1] and p2 < strategy2[1]:
                run = True
                res = (max(0.5 - obs_costs, 0.), max(0.5 - obs_costs, 0.), False)[my_place]
                self.emit('interaction', self, res, False)
                return res
            elif p1 < strategy1[1]:
                run = True
                res = (max(0.5 - obs_costs, 0.), max(1. - obs_costs, 0.), False)[my_place]
                self.emit('interaction', self, res, False)
                return res
            elif p2 < strategy2[1]:
                run = True
                res = (max(1. - obs_costs, 0.), max(0.5 - obs_costs, 0.), False)[my_place]
                self.emit('interaction', self, res, False)
                return res

            #check for fighting
            if p1 >= strategy1[2] and p2 >= strategy2[2]:
                fight = True
                if player1Wins():
                    res = (max(1. - obs_costs - cost_win, 0.), max(0.5 - obs_costs - cost_loss, 0.), True)[my_place]
                    self.emit('interaction', self, res, True)
                    return res
                else:
                    res = (max(0.5 - obs_costs - cost_loss, 0.), max(1. - obs_costs - cost_win, 0.), True)[my_place]
                    self.emit('interaction', self, res, True)
                    return res
            elif p1 >= strategy1[2]:
                if isFight(p2):
                    fight = True
                    if player1Wins():
                        res = (max(1. - obs_costs - cost_win, 0.), max(0.5 - obs_costs - cost_loss, 0.), True)[my_place]
                        self.emit('interaction', self, res, True)
                        return res
                    else:
                        res = (max(0.5 - obs_costs - cost_loss, 0.), max(1. - obs_costs - cost_win, 0.), True)[my_place]
                        self.emit('interaction', self, res, True)
                        return res
                else:
                    run = True
                    res = (max(1. - obs_costs, 0.), max(0.5 - obs_costs, 0.), False)[my_place]
                    self.emit('interaction', self, res, False)
                    return res
            elif p2 >= strategy2[2]:
                if isFight(p1):
                    fight = True
                    if player1Wins():
                        res = (max(1. - obs_costs - cost_win, 0.), max(0.5 - obs_costs - cost_loss, 0.), True)[my_place]
                        self.emit('interaction', self, res, True)
                        return res
                    else:
                        res = (max(0.5 - obs_costs - cost_loss, 0.), max(1. - obs_costs - cost_win, 0.), True)[my_place]
                        self.emit('interaction', self, res, True)
                        return res
                else:
                    run = True
                    res = (max(0.5 - obs_costs, 0.), max(1. - obs_costs, 0.), False)[my_place]
                    self.emit('interaction', self, res, True)
                    return res

            obs_costs += cost_obs
            adjustment = (strategy1[0] - strategy2[0]) / (2. * update_modulus)
            if rand.uniform(0., 1.) < update_correct:
                p1 += adjustment
                p2 -= adjustment
            else:
                p1 -= adjustment
                p2 += adjustment
