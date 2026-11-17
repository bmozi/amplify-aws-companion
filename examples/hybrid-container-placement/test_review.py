import unittest

from review import case, review


class PlacementTests(unittest.TestCase):
    def test_regional_control_planes_hold_new_work_during_wan_loss(self):
        for platform in ('ecs_anywhere', 'eks_hybrid_nodes'):
            with self.subTest(platform=platform):
                self.assertEqual(review(case(platform))['decision'], 'HOLD')

    def test_local_control_plane_is_only_a_candidate(self):
        for platform in ('eks_anywhere', 'eks_outposts_local_cluster'):
            with self.subTest(platform=platform):
                self.assertEqual(review(case(platform))['decision'],
                                 'REVIEW_WITH_DISCONNECTION_DRILL')

    def test_local_control_plane_does_not_copy_remote_dependencies(self):
        for dependency in ('local_images', 'local_identity', 'local_data',
                           'local_ingress', 'local_power'):
            with self.subTest(dependency=dependency):
                result = review(case('eks_anywhere', **{dependency: False}))
                self.assertEqual(result['decision'], 'HOLD')
                self.assertIn(dependency, result['missing'])

    def test_ecs_external_service_load_balancing_assumption_holds(self):
        item = case('ecs_anywhere', required_outage_minutes=0,
                    needs_new_work_while_offline=False,
                    expects_aws_elb_for_local_inbound=True)
        self.assertEqual(review(item)['decision'], 'HOLD')

    def test_invalid_or_contradictory_inputs_rejected(self):
        for item in (case('unknown'), case('eks_anywhere', required_outage_minutes=-1),
                     case('eks_anywhere', required_outage_minutes=True),
                     case('eks_anywhere', required_outage_minutes=0)):
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    review(item)


if __name__ == '__main__':
    unittest.main()
