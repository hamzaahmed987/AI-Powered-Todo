/**
 * Basic frontend tests for the AI-Powered Todo application
 */

// Mock the API service for testing
jest.mock('../src/services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

describe('Task Management Features', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  test('should create a new task successfully', async () => {
    // Mock the API response
    const mockTask = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      title: 'Test Task',
      description: 'Test Description',
      status: 'pending',
      priority: 'medium',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Import the service after mocking
    const { tasksService } = await import('../src/services/tasksService');
    
    // Mock the API call
    const api = await import('../src/services/api');
    api.default.post.mockResolvedValue({ data: mockTask });

    // Call the service function
    const result = await tasksService.createTask({
      title: 'Test Task',
      description: 'Test Description',
    });

    // Assertions
    expect(api.default.post).toHaveBeenCalledWith('tasks', {
      title: 'Test Task',
      description: 'Test Description',
    });
    expect(result).toEqual(mockTask);
  });

  test('should fetch tasks successfully', async () => {
    // Mock the API response
    const mockTasks = [{
      id: '123e4567-e89b-12d3-a456-426614174000',
      title: 'Test Task',
      status: 'pending',
      priority: 'medium',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }];

    // Import the service after mocking
    const { tasksService } = await import('../src/services/tasksService');
    
    // Mock the API call
    const api = await import('../src/services/api');
    api.default.get.mockResolvedValue({ 
      data: {
        items: mockTasks,
        total: 1,
        skip: 0,
        limit: 20
      }
    });

    // Call the service function
    const result = await tasksService.getTasks();

    // Assertions
    expect(api.default.get).toHaveBeenCalledWith('tasks', { params: { skip: 0, limit: 20 } });
    expect(result.tasks).toEqual(mockTasks);
    expect(result.total).toBe(1);
  });

  test('should update a task successfully', async () => {
    // Mock the API response
    const taskId = '123e4567-e89b-12d3-a456-426614174000';
    const updatedTask = {
      id: taskId,
      title: 'Updated Task',
      status: 'in_progress',
      priority: 'high',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Import the service after mocking
    const { tasksService } = await import('../src/services/tasksService');
    
    // Mock the API call
    const api = await import('../src/services/api');
    api.default.put.mockResolvedValue({ data: updatedTask });

    // Call the service function
    const result = await tasksService.updateTask(taskId, {
      title: 'Updated Task',
      status: 'in_progress',
    });

    // Assertions
    expect(api.default.put).toHaveBeenCalledWith(`tasks/${taskId}`, {
      title: 'Updated Task',
      status: 'in_progress',
    });
    expect(result).toEqual(updatedTask);
  });

  test('should delete a task successfully', async () => {
    // Mock the API response
    const taskId = '123e4567-e89b-12d3-a456-426614174000';

    // Import the service after mocking
    const { tasksService } = await import('../src/services/tasksService');
    
    // Mock the API call
    const api = await import('../src/services/api');
    api.default.delete.mockResolvedValue({});

    // Call the service function
    await tasksService.deleteTask(taskId);

    // Assertions
    expect(api.default.delete).toHaveBeenCalledWith(`tasks/${taskId}`);
  });
});

describe('AI Agent Features', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  test('should send message to AI agent and receive response', async () => {
    // Mock the API response
    const mockResponse = {
      message: "I've created a task called 'Buy groceries' with high priority.",
      success: true,
      action: 'create',
      task_data: {
        id: '123e4567-e89b-12d3-a456-426614174000',
        title: 'Buy groceries',
        status: 'pending',
        priority: 'high',
      }
    };

    // Import the service after mocking
    const agentService = await import('../src/services/agentService').then(mod => mod.default);
    
    // Mock the fetch call
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    // Call the service function
    const result = await agentService.sendMessage("Create a task called 'Buy groceries' with high priority");

    // Assertions
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/agent/chat'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
    expect(result).toEqual(mockResponse);
  });

  test('should handle AI agent errors gracefully', async () => {
    // Mock the API response with error
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: jest.fn().mockResolvedValue({
        detail: "AI service temporarily unavailable"
      }),
    });

    // Import the service after mocking
    const agentService = await import('../src/services/agentService').then(mod => mod.default);

    // Call the service function and expect it to throw
    await expect(agentService.sendMessage("Hello")).rejects.toThrow();
  });
});

describe('Redux Store Integration', () => {
  test('should initialize with empty tasks', () => {
    // Import the task slice
    const taskSlice = require('../src/redux/slices/taskSlice').default;
    const initialState = taskSlice(undefined, { type: '@@INIT' });

    expect(initialState.tasks).toEqual([]);
    expect(initialState.isLoading).toBe(false);
    expect(initialState.error).toBeNull();
  });

  test('should handle setTasks action', () => {
    // Import the task slice and action
    const taskSlice = require('../src/redux/slices/taskSlice').default;
    const { setTasks } = require('../src/redux/slices/taskSlice');

    const mockTasks = [
      {
        id: '123e4567-e89b-12d3-a456-426614174000',
        title: 'Test Task',
        status: 'pending',
        priority: 'medium',
      }
    ];

    const newState = taskSlice(
      { tasks: [], isLoading: false, error: null },
      setTasks(mockTasks)
    );

    expect(newState.tasks).toEqual(mockTasks);
  });
});