from escalation.simulation import Simulation


class TestFakeness:

    def setUp(self):
        self.sim = None

    def test_fake_stuff(self):
        self.sim = Simulation({'types': None}, 2, None)

        assert self.sim is not None, "self.sim was None"

