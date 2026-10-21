import os, random, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hillclimb import (Benchmark, EuclideanFitness, FirstChoice, HillClimber, ManhattanFitness,
                       NoRestart, Position, RandomRestart, ScenarioCatalog, SelectionStrategy,
                       SteepestAscent, Status, Stochastic)


def climber(case, strategy=None, restart=None, seed=0, fitness=None):
    return HillClimber(ScenarioCatalog.create(case), fitness or ManhattanFitness(),
                       strategy or SteepestAscent(), restart or NoRestart(), random.Random(seed))


class MazeTests(unittest.TestCase):
    def test_walls_and_bounds(self):
        m = ScenarioCatalog.create("B")
        self.assertTrue(m.is_wall(Position(7, 5)))
        self.assertEqual(m.blocked_reason(Position(-1, 0)), "fuera")
        self.assertEqual(m.blocked_reason(Position(7, 5)), "muro")

    def test_toggle_wall_protects_start_and_goal(self):
        m = ScenarioCatalog.create("A")
        self.assertFalse(m.toggle_wall(m.start))
        self.assertFalse(m.toggle_wall(m.goal))
        self.assertTrue(m.toggle_wall(Position(0, 5)))
        self.assertTrue(m.is_wall(Position(0, 5)))


class FitnessTests(unittest.TestCase):
    def test_optimum_is_zero_at_goal(self):
        m = ScenarioCatalog.create("A")
        for f in (ManhattanFitness(), EuclideanFitness()):
            self.assertEqual(f(m.goal, m), 0)
            self.assertLess(f(m.start, m), 0)


class ClimberTests(unittest.TestCase):
    def test_case_a_reaches_goal(self):
        r = climber("A").run()
        self.assertTrue(r.success)
        self.assertEqual(r.final_position, Position(13, 9))
        self.assertEqual(r.iterations, 21)

    def test_case_b_gets_trapped_in_local_maximum(self):
        c = climber("B")
        r = c.run()
        self.assertFalse(r.success)
        self.assertEqual(r.final_position, Position(6, 5))
        self.assertEqual(r.final_fitness, -6)
        self.assertEqual(c.last_result.status, Status.LOCAL_MAXIMUM)

    def test_restarts_escape_the_trap(self):
        r = climber("B", restart=RandomRestart(20), seed=3).run()
        self.assertTrue(r.success)
        self.assertGreaterEqual(r.restarts, 1)

    def test_step_telemetry_lists_four_neighbors(self):
        s = climber("B").step()
        self.assertEqual(len(s.neighbors), 4)
        self.assertEqual(s.chosen.position, Position(6, 5))
        self.assertEqual(s.chosen.delta, 1)

    def test_all_strategies_succeed_on_case_a(self):
        for strat in (SteepestAscent(), FirstChoice(), Stochastic()):
            self.assertTrue(climber("A", strat, seed=5).run().success, strat.label)

    def test_strategies_are_polymorphic(self):
        for strat in (SteepestAscent(), FirstChoice(), Stochastic()):
            self.assertIsInstance(strat, SelectionStrategy)
        with self.assertRaises(TypeError):
            SelectionStrategy()


class BenchmarkTests(unittest.TestCase):
    def test_reported_numbers_are_reproducible(self):
        b = Benchmark(ScenarioCatalog.create("B"), ManhattanFitness())
        plain = b.evaluate(SteepestAscent(), NoRestart())
        rr = b.evaluate(SteepestAscent(), RandomRestart(20))
        self.assertAlmostEqual(plain.success_rate, 73.4, places=1)
        self.assertAlmostEqual(rr.success_rate, 100.0)
        self.assertAlmostEqual(plain.mean_iterations, 7.7, places=1)


if __name__ == "__main__":
    unittest.main()
