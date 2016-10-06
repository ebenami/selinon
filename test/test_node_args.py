#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ####################################################################
# Copyright (C) 2016  Fridolin Pokorny, fpokorny@redhat.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# ####################################################################

from selinon import SystemState
from selinonTestCase import SelinonTestCase


class TestNodeArgs(SelinonTestCase):
    def test_task2task(self):
        #
        # flow1:
        #
        #     Task1
        #       |
        #       |
        #     Task2
        #
        # Note:
        #    Result of Task1 is propagated to Task2 as node_args
        #
        edge_table = {
            'flow1': [{'from': ['Task1'], 'to': ['Task2'], 'condition': self.cond_true},
                      {'from': [], 'to': ['Task1'], 'condition': self.cond_true}]
        }
        self.init(edge_table, node_args_from_first={'flow1': True})

        system_state = SystemState(id(self), 'flow1')
        retry = system_state.update()
        state_dict = system_state.to_dict()

        # Run without change at first
        system_state = SystemState(id(self), 'flow1', state=state_dict, node_args=system_state.node_args)
        retry = system_state.update()
        state_dict = system_state.to_dict()

        self.assertIsNone(system_state.node_args)
        self.assertIsNotNone(retry)
        self.assertIn('Task1', self.instantiated_tasks)

        # Task1 has finished
        task1 = self.get_task('Task1')
        task1_result = "propagated result of Task1"
        self.set_finished(task1, task1_result)

        system_state = SystemState(id(self), 'flow1', state=state_dict, node_args=system_state.node_args)
        retry = system_state.update()
        system_state.to_dict()

        task2 = self.get_task('Task2')
        self.assertIn('Task2', self.instantiated_tasks)
        self.assertEqual(task2.node_args, task1_result)
        self.assertIsNotNone(retry)

    def test_task2flow(self):
        #
        # flow1:
        #
        #     Task1
        #       |
        #       |
        #     flow2
        #
        # Note:
        #    Result of Task1 is not propagated to flow2 as even node_args_from_first is set - but propagate_node_args
        #    is not set
        #
        edge_table = {
            'flow1': [{'from': ['Task1'], 'to': ['flow2'], 'condition': self.cond_true},
                      {'from': [], 'to': ['Task1'], 'condition': self.cond_true}],
            'flow2': []
        }
        self.init(edge_table, node_args_from_first={'flow1': True})

        system_state = SystemState(id(self), 'flow1')
        retry = system_state.update()
        state_dict = system_state.to_dict()

        self.assertIsNotNone(retry)
        self.assertIsNone(system_state.node_args)
        self.assertIn('Task1', self.instantiated_tasks)

        # Run without change at first
        system_state = SystemState(id(self), 'flow1', state=state_dict, node_args=system_state.node_args)
        retry = system_state.update()
        state_dict = system_state.to_dict()

        self.assertIsNone(system_state.node_args)
        self.assertIsNotNone(retry)
        self.assertIn('Task1', self.instantiated_tasks)

        # Task1 has finished
        task1 = self.get_task('Task1')
        task1_result = "propagated result of Task1"
        self.set_finished(task1, task1_result)

        system_state = SystemState(id(self), 'flow1', state=state_dict, node_args=system_state.node_args)
        retry = system_state.update()

        flow2 = self.get_flow('flow2')
        self.assertIn('flow2', self.instantiated_flows)
        self.assertIsNone(flow2.node_args)
        self.assertIsNotNone(retry)

    def test_task2flow_propagate(self):
        #
        # flow1:
        #
        #     Task1
        #       |
        #       |
        #     flow2
        #
        # Note:
        #    Result of Task1 is not propagated to flow2 as even node_args_from_first is set - but propagate_node_args
        #    is not set
        #
        edge_table = {
            'flow1': [{'from': ['Task1'], 'to': ['flow2'], 'condition': self.cond_true},
                      {'from': [], 'to': ['Task1'], 'condition': self.cond_true}],
            'flow2': []
        }
        self.init(edge_table, node_args_from_first={'flow1': True}, propagate_node_args={'flow1': True})

        system_state = SystemState(id(self), 'flow1')
        retry = system_state.update()
        state_dict = system_state.to_dict()

        self.assertIsNotNone(retry)
        self.assertIsNone(system_state.node_args)
        self.assertIn('Task1', self.instantiated_tasks)

        # Task1 has finished
        task1 = self.get_task('Task1')
        task1_result = "propagated result of Task1"
        self.set_finished(task1, task1_result)

        system_state = SystemState(id(self), 'flow1', state=state_dict, node_args=system_state.node_args)
        retry = system_state.update()

        flow2 = self.get_flow('flow2')
        self.assertIn('flow2', self.instantiated_flows)
        self.assertEqual(flow2.node_args, task1_result)
        self.assertIsNotNone(retry)

    def test_task2tasks(self):
        #
        # flow1:
        #
        #     Task1
        #       |
        #    --------
        #   |        |
        # Task2    Task3
        #
        # Note:
        #    Result of Task1 is propagated to flow1 as node_args
        #
        edge_table = {
            'flow1': [{'from': ['Task1'], 'to': ['Task2', 'Task3'], 'condition': self.cond_true},
                      {'from': [], 'to': ['Task1'], 'condition': self.cond_true}]
        }
        self.init(edge_table, node_args_from_first={'flow1': True})

        system_state = SystemState(id(self), 'flow1')
        retry = system_state.update()
        state_dict = system_state.to_dict()

        self.assertIsNotNone(retry)
        self.assertIsNone(system_state.node_args)
        self.assertIn('Task1', self.instantiated_tasks)

        # Task1 has finished
        task1 = self.get_task('Task1')
        task1_result = "propagated result of Task1"
        self.set_finished(task1, task1_result)

        system_state = SystemState(id(self), 'flow1', state=state_dict, node_args=system_state.node_args)
        retry = system_state.update()

        self.assertIsNotNone(retry)
        self.assertIn('Task2', self.instantiated_tasks)
        self.assertIn('Task3', self.instantiated_tasks)

        task2 = self.get_task('Task2')
        task3 = self.get_task('Task3')

        self.assertEqual(task2.node_args, task1_result)
        self.assertEqual(task3.node_args, task1_result)

    def test_recurse(self):
        #
        # flow1:
        #
        #     Task1 <----
        #       |       |
        #       |       |
        #       ---------
        #
        # Note:
        #    Result of Task1 is propagated to flow1 as node_args
        #
        edge_table = {
            'flow1': [{'from': ['Task1'], 'to': ['Task1'], 'condition': self.cond_true},
                      {'from': [], 'to': ['Task1'], 'condition': self.cond_true}]
        }
        self.init(edge_table, node_args_from_first={'flow1': True})

        system_state = SystemState(id(self), 'flow1')
        retry = system_state.update()
        state_dict = system_state.to_dict()

        self.assertIsNotNone(retry)
        self.assertIsNone(system_state.node_args)
        self.assertIn('Task1', self.instantiated_tasks)

        # Task1 has finished
        task1_1 = self.get_task('Task1')
        task1_result = "propagated result of Task1"
        self.set_finished(task1_1, task1_result)

        system_state = SystemState(id(self), 'flow1', state=state_dict, node_args=system_state.node_args)
        retry = system_state.update()

        self.assertIn('Task1', self.instantiated_tasks)
        task1_2 = self.get_task('Task1')
        self.assertEqual(task1_2.node_args, task1_result)
        self.assertIsNotNone(retry)
