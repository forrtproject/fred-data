"""A different extraction must not restart a report's blind-attempt budget."""
import unittest
from unittest.mock import patch

from prepare_dispatch import identical_source_budget, prepare


class IdenticalArticleBudget(unittest.TestCase):
    def setUp(self):
        self.registry = {doc: {'article.txt': digest} for doc, digest in
                         [('old', 'a' * 64), ('alias', 'a' * 64),
                          ('third', 'a' * 64), ('other', 'b' * 64)]}
        self.tasks = [dict(role='blind_coder', packet_ids=[doc], attempt=1,
                           status='completed_parent_mechanically_validated')
                      for doc in ['old', 'alias']]

    def check(self, docs=('third',), role='blind_coder', upgrades=()):
        return identical_source_budget(docs, role, self.tasks, self.registry, upgrades)

    def test_distinct_opaque_ids_cannot_reset_two_completed_attempts(self):
        with self.assertRaisesRegex(ValueError, 'Identical source attempt budget exhausted'):
            self.check()

    def test_initial_alias_inherits_upgrade_single_read_cap(self):
        self.tasks.pop()
        with self.assertRaisesRegex(ValueError, 'Identical source attempt budget exhausted'):
            self.check(upgrades=[dict(document_id='old', max_attempts_per_role=1)])

    def test_other_model_role_keeps_its_own_budget(self):
        aliases, limit, budgets = self.check(role='blind_comparison_coder')
        self.assertEqual(aliases, {'old', 'alias', 'third'})
        self.assertEqual(limit, 2)
        self.assertEqual(budgets['a' * 64]['prior_role_tasks'], 0)

    def test_unrelated_source_tasks_do_not_consume_budget(self):
        aliases, limit, budgets = self.check(docs=('other',))
        self.assertEqual(aliases, {'other'})
        self.assertEqual(budgets['b' * 64]['prior_role_tasks'], 0)

    def test_budget_is_per_source_not_sum_of_group_tasks(self):
        self.tasks.pop()
        self.tasks.append(dict(self.tasks[0], packet_ids=['other']))
        _, _, budgets = self.check(docs=('third', 'other'))
        self.assertEqual([x['prior_role_tasks'] for x in budgets.values()], [1, 1])

    def test_active_alias_cannot_start_a_parallel_read(self):
        self.tasks.pop()
        for status in ['running', 'completed_pending_parent_validation', 'cancel_requested']:
            with self.subTest(status=status):
                self.tasks[0]['status'] = status
                with self.assertRaisesRegex(ValueError, 'still active or awaiting validation'):
                    self.check()

    def test_same_source_cannot_appear_twice_in_one_task(self):
        with self.assertRaisesRegex(ValueError, 'Group contains identical source aliases'):
            self.check(docs=('alias', 'third'))

    def test_missing_hash_and_invalid_cap_fail_closed(self):
        self.tasks.clear()
        with self.assertRaisesRegex(ValueError, 'Invalid source-specific attempt limit'):
            self.check(upgrades=[dict(document_id='old', max_attempts_per_role=True)])
        self.registry['third'] = {}
        with self.assertRaisesRegex(ValueError, 'Missing or invalid frozen article hash'):
            self.check()


class ReachedFrozenInputCheck(Exception):
    pass


class SharedSourceBudget(unittest.TestCase):
    def setUp(self):
        old = dict(document_id='document_0684', parent_work_key='10.example/report',
                   primary_pdf_sha256='a' * 64)
        new = dict(old, document_id='document_0685',
                   attempt_history_document_ids=['document_0684', 'document_0685'])
        self.upgrades = {'upgrades': [old, new]}
        self.first = dict(role='blind_coder', group_id='document_0684', packet_ids=['document_0684'],
                          status='completed_parent_mechanically_validated', attempt=1)
        self.state = dict(tasks=[self.first], validated_opus_documents=['document_0684'],
                          validated_fresh_sol_documents=[], max_active_model_children=3)

    def read(self, path):
        if path.name == 'state.json': return self.state
        if path.name == 'dispatch_plan.json': return {'groups': []}
        if path.name == 'source_upgrades.json': return self.upgrades
        if path.name == 'packet_input_receipts.json': raise ReachedFrozenInputCheck
        raise AssertionError(path)

    def check(self, provider, attempt):
        with patch('prepare_dispatch.read', side_effect=self.read):
            return prepare('document_0685', provider, attempt)

    def test_new_extraction_cannot_restart_at_attempt_one(self):
        with self.assertRaisesRegex(ValueError, 'Attempt already registered'):
            self.check('opus', 1)

    def test_second_attempt_can_reach_new_immutable_input_validation(self):
        with self.assertRaises(ReachedFrozenInputCheck):
            self.check('opus', 2)

    def test_spent_second_attempt_blocks_another_extraction(self):
        self.state['tasks'].append(dict(self.first, attempt=2))
        with self.assertRaisesRegex(ValueError, 'Attempt already registered'):
            self.check('opus', 2)

    def test_another_primary_pdf_cannot_supply_the_first_attempt(self):
        self.upgrades['upgrades'][0]['primary_pdf_sha256'] = 'b' * 64
        with self.assertRaisesRegex(ValueError, 'another primary report'):
            self.check('opus', 2)

    def test_model_roles_cannot_borrow_each_others_attempts(self):
        with self.assertRaisesRegex(ValueError, 'Retry requires preserved first attempt'):
            self.check('sol', 2)

    def test_active_earlier_extraction_blocks_a_second_reader_of_that_role(self):
        self.first['status'] = 'running'
        with self.assertRaisesRegex(ValueError, 'Owned task still active'):
            self.check('opus', 2)

    def test_source_worker_helper_reservation_consumes_capacity(self):
        self.state['tasks'].extend([
            dict(role='source_acquisition', status='running', reserved_slots=2),
            dict(role='source_adjudicator', status='running')])
        with self.assertRaisesRegex(ValueError, 'No free model slot'):
            self.check('opus', 2)

    def test_unlisted_third_extraction_cannot_reset_the_same_pdf_budget(self):
        self.upgrades['upgrades'].append(dict(self.upgrades['upgrades'][0], document_id='document_0686'))
        self.state['tasks'].append(dict(self.first, packet_ids=['document_0685'], attempt=2))
        with patch('prepare_dispatch.read', side_effect=self.read):
            with self.assertRaisesRegex(ValueError, 'Attempt already registered'):
                prepare('document_0686', 'opus', 1)

    def initial_document_read(self, path):
        if path.name == 'dispatch_plan.json':
            return {'groups': [{'group_id': 'group_0028', 'document_ids': ['document_0061']}]}
        return self.read(path)

    def test_one_initial_document_can_be_compared_without_repeating_its_group(self):
        with patch('prepare_dispatch.read', side_effect=self.initial_document_read):
            with self.assertRaises(ReachedFrozenInputCheck):
                prepare('document_0061', 'sol', 1)

    def test_single_document_alias_cannot_repeat_a_completed_group_comparison(self):
        self.state['tasks'].append(dict(role='blind_comparison_coder', group_id='group_0028',
                                       packet_ids=['document_0061'], attempt=1,
                                       status='completed_parent_mechanically_validated'))
        with patch('prepare_dispatch.read', side_effect=self.initial_document_read):
            with self.assertRaisesRegex(ValueError, 'Already validated'):
                prepare('document_0061', 'sol', 1)

    def test_unregistered_single_document_is_rejected(self):
        with patch('prepare_dispatch.read', side_effect=self.initial_document_read):
            with self.assertRaisesRegex(ValueError, 'absent from parent registry'):
                prepare('document_9999', 'sol', 1)

    def test_lower_source_attempt_limit_blocks_a_second_attempt(self):
        self.upgrades['upgrades'][1]['max_attempts_per_role'] = 1
        with self.assertRaisesRegex(ValueError, 'Source-specific attempt budget exhausted'):
            self.check('opus', 2)

    def test_another_extraction_inherits_the_lowest_physical_source_limit(self):
        self.upgrades['upgrades'][0]['max_attempts_per_role'] = 1
        with self.assertRaisesRegex(ValueError, 'Source-specific attempt budget exhausted'):
            self.check('opus', 2)

    def test_invalid_source_attempt_limit_is_rejected(self):
        self.upgrades['upgrades'][1]['max_attempts_per_role'] = 0
        with self.assertRaisesRegex(ValueError, 'Invalid source-specific attempt limit'):
            self.check('opus', 1)


if __name__ == '__main__':
    unittest.main()
