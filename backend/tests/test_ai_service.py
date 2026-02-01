"""
Unit tests for AI service.

Tests AI-powered task analysis, priority suggestions, and natural language processing.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from typing import List

from app.models.task import Task, TaskStatus, TaskPriority
from app.services.ai_service import (
    generate_priority_and_duration,
    generate_task_insights,
    generate_productivity_insights,
    get_task_analyzer_agent
)


class TestAIService:
    """Test cases for AI service functions."""

    @pytest.mark.asyncio
    async def test_generate_priority_and_duration_with_mock(self):
        """Test generating priority and duration with mocked agent."""
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Create a mock agent
            mock_agent = Mock()
            mock_runner = AsyncMock()
            mock_result = Mock()
            mock_result.final_output = '{"priority": "high", "estimated_hours": 3}'
            
            # Mock the Runner.run method
            with patch('app.services.ai_service.Runner') as mock_runner_class:
                mock_instance = Mock()
                mock_instance.run = AsyncMock(return_value=mock_result)
                mock_runner_class.run = mock_instance.run
                
                # Set up the agent mock
                mock_get_agent.return_value = mock_agent
                
                # Call the function
                priority, hours = await generate_priority_and_duration(
                    "Complete the project documentation by Friday"
                )
                
                # Assertions
                assert priority == "high"
                assert hours == 3
                mock_instance.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_priority_and_duration_invalid_json(self):
        """Test handling of invalid JSON response from AI."""
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Create a mock agent
            mock_agent = Mock()
            mock_runner = AsyncMock()
            mock_result = Mock()
            mock_result.final_output = 'invalid json response'
            
            # Mock the Runner.run method
            with patch('app.services.ai_service.Runner') as mock_runner_class:
                mock_instance = Mock()
                mock_instance.run = AsyncMock(return_value=mock_result)
                mock_runner_class.run = mock_instance.run
                
                # Set up the agent mock
                mock_get_agent.return_value = mock_agent
                
                # Call the function
                priority, hours = await generate_priority_and_duration(
                    "Complete the project documentation by Friday"
                )
                
                # Should return None for both values due to invalid JSON
                assert priority is None
                assert hours is None

    @pytest.mark.asyncio
    async def test_generate_priority_and_duration_invalid_values(self):
        """Test handling of invalid priority/duration values from AI."""
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Create a mock agent
            mock_agent = Mock()
            mock_runner = AsyncMock()
            mock_result = Mock()
            mock_result.final_output = '{"priority": "invalid_priority", "estimated_hours": 0}'
            
            # Mock the Runner.run method
            with patch('app.services.ai_service.Runner') as mock_runner_class:
                mock_instance = Mock()
                mock_instance.run = AsyncMock(return_value=mock_result)
                mock_runner_class.run = mock_instance.run
                
                # Set up the agent mock
                mock_get_agent.return_value = mock_agent
                
                # Call the function
                priority, hours = await generate_priority_and_duration(
                    "Complete the project documentation by Friday"
                )
                
                # Should return None for both values due to invalid values
                assert priority is None
                assert hours is None

    @pytest.mark.asyncio
    async def test_generate_priority_and_duration_no_agent(self):
        """Test behavior when no AI agent is available."""
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Mock no agent available
            mock_get_agent.return_value = None
            
            # Call the function
            priority, hours = await generate_priority_and_duration(
                "Complete the project documentation by Friday"
            )
            
            # Should return None for both values
            assert priority is None
            assert hours is None

    @pytest.mark.asyncio
    async def test_generate_priority_and_duration_exception(self):
        """Test handling of exceptions during AI processing."""
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Create a mock agent that raises an exception
            mock_agent = Mock()
            
            # Mock the Runner.run method to raise an exception
            with patch('app.services.ai_service.Runner') as mock_runner_class:
                mock_instance = Mock()
                mock_instance.run = AsyncMock(side_effect=Exception("AI service error"))
                mock_runner_class.run = mock_instance.run
                
                # Set up the agent mock
                mock_get_agent.return_value = mock_agent
                
                # Call the function
                priority, hours = await generate_priority_and_duration(
                    "Complete the project documentation by Friday"
                )
                
                # Should return None for both values due to exception
                assert priority is None
                assert hours is None

    @pytest.mark.asyncio
    async def test_generate_task_insights_with_mock(self):
        """Test generating task insights with mocked agent."""
        # Create a mock task
        mock_task = Mock(spec=Task)
        mock_task.title = "Test Task"
        mock_task.description = "Test Description"
        mock_task.status = TaskStatus.PENDING
        mock_task.priority = TaskPriority.MEDIUM
        mock_task.deadline = datetime.now()
        mock_task.estimated_duration = 60
        mock_task.ai_priority = TaskPriority.HIGH
        mock_task.ai_estimated_duration = 90
        mock_task.owner_id = "test-owner-id"
        
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Create a mock agent
            mock_agent = Mock()
            mock_runner = AsyncMock()
            mock_result = Mock()
            mock_result.final_output = "This is a test insight response"
            
            # Mock the Runner.run method
            with patch('app.services.ai_service.Runner') as mock_runner_class:
                mock_instance = Mock()
                mock_instance.run = AsyncMock(return_value=mock_result)
                mock_runner_class.run = mock_instance.run
                
                # Set up the agent mock
                mock_get_agent.return_value = mock_agent
                
                # Call the function
                insights = await generate_task_insights(mock_task)
                
                # Assertions
                assert insights == "This is a test insight response"
                mock_instance.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_task_insights_no_agent(self):
        """Test behavior when no AI agent is available for task insights."""
        # Create a mock task
        mock_task = Mock(spec=Task)
        mock_task.title = "Test Task"
        mock_task.description = "Test Description"
        mock_task.status = TaskStatus.PENDING
        mock_task.priority = TaskPriority.MEDIUM
        mock_task.owner_id = "test-owner-id"
        
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Mock no agent available
            mock_get_agent.return_value = None
            
            # Call the function
            insights = await generate_task_insights(mock_task)
            
            # Should return generic insights
            assert "Consider prioritizing this task" in insights

    @pytest.mark.asyncio
    async def test_generate_productivity_insights_with_mock(self):
        """Test generating productivity insights with mocked agent."""
        # Create mock tasks
        mock_task1 = Mock(spec=Task)
        mock_task1.title = "Task 1"
        mock_task1.status = TaskStatus.PENDING
        mock_task1.priority = TaskPriority.HIGH
        mock_task1.owner_id = "test-owner-id"
        
        mock_task2 = Mock(spec=Task)
        mock_task2.title = "Task 2"
        mock_task2.status = TaskStatus.IN_PROGRESS
        mock_task2.priority = TaskPriority.MEDIUM
        mock_task2.owner_id = "test-owner-id"
        
        mock_tasks = [mock_task1, mock_task2]
        
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Create a mock agent
            mock_agent = Mock()
            mock_runner = AsyncMock()
            mock_result = Mock()
            mock_result.final_output = "These are test productivity insights"
            
            # Mock the Runner.run method
            with patch('app.services.ai_service.Runner') as mock_runner_class:
                mock_instance = Mock()
                mock_instance.run = AsyncMock(return_value=mock_result)
                mock_runner_class.run = mock_instance.run
                
                # Set up the agent mock
                mock_get_agent.return_value = mock_agent
                
                # Call the function
                insights = await generate_productivity_insights(mock_tasks)
                
                # Assertions
                assert insights == "These are test productivity insights"
                mock_instance.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_productivity_insights_no_agent(self):
        """Test behavior when no AI agent is available for productivity insights."""
        # Create mock tasks
        mock_task1 = Mock(spec=Task)
        mock_task1.title = "Task 1"
        mock_task1.status = TaskStatus.PENDING
        mock_task1.priority = TaskPriority.HIGH
        mock_task1.owner_id = "test-owner-id"
        
        mock_tasks = [mock_task1]
        
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Mock no agent available
            mock_get_agent.return_value = None
            
            # Call the function
            insights = await generate_productivity_insights(mock_tasks)
            
            # Should return generic insights
            assert "Review your tasks regularly" in insights

    @pytest.mark.asyncio
    async def test_generate_productivity_insights_empty_tasks(self):
        """Test behavior when no tasks are provided for productivity insights."""
        with patch('app.services.ai_service.get_task_analyzer_agent') as mock_get_agent:
            # Create a mock agent
            mock_agent = Mock()
            mock_runner = AsyncMock()
            mock_result = Mock()
            mock_result.final_output = "These are test productivity insights"
            
            # Mock the Runner.run method
            with patch('app.services.ai_service.Runner') as mock_runner_class:
                mock_instance = Mock()
                mock_instance.run = AsyncMock(return_value=mock_result)
                mock_runner_class.run = mock_instance.run
                
                # Set up the agent mock
                mock_get_agent.return_value = mock_agent
                
                # Call the function with empty list
                insights = await generate_productivity_insights([])
                
                # Should still call the AI service
                mock_instance.run.assert_called_once()

    def test_get_task_analyzer_agent(self):
        """Test getting the task analyzer agent."""
        # This test checks if the function returns an agent when properly configured
        # Since the actual agent creation depends on environment variables,
        # we'll test the logic path
        agent = get_task_analyzer_agent()
        # The agent could be None if API keys are not set, which is acceptable
        # Just verify the function doesn't crash
        assert agent is None or callable(getattr(agent, 'run', None))