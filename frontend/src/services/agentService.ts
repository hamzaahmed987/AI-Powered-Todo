/**
 * Agent API Service
 *
 * Service for communicating with the OpenAI Agents SDK backend.
 * Handles task management through natural language conversations.
 */

export interface AgentChatRequest {
  message: string;
}

export interface AgentChatResponse {
  message: string;
  success: boolean;
  action: string; // Action type: create, update, delete, get, insights, productivity, none
  task_data?: {
    id: string;
    title: string;
    status: string;
    priority: string;
  };
}

export interface AgentCapabilities {
  agent_name: string;
  capabilities: {
    action: string;
    description: string;
    examples: string[];
  }[];
  supported_statuses: string[];
  supported_priorities: string[];
  instructions: string;
}

// Always construct the agent URL with /agent prefix
const API_BASE_URL = (() => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api/v1";
  // Remove /api/v1 if it's there, then add it back with /agent
  const cleanBase = baseUrl.replace(/\/api\/v1\/?$/, "");
  return `${cleanBase}/api/v1/agent`;
})();

/**
 * Agent API service for task management conversations
 */
export const agentService = {
  /**
   * Send a message to the task management agent
   * The agent will process the message and execute appropriate tools
   *
   * @param message - Natural language request for task management
   * @returns Promise with agent response
   *
   * @example
   * const response = await agentService.sendMessage("Add a task called 'Buy groceries' with high priority");
   * console.log(response.message); // "Task 'Buy groceries' created successfully..."
   */
  sendMessage: async (message: string): Promise<AgentChatResponse> => {
    if (!message || message.trim().length === 0) {
      throw new Error("Message cannot be empty");
    }

    try {
      let token = null;
      try {
        token = typeof window !== "undefined" ? localStorage.getItem("accessToken") : null;
      } catch (error) {
        console.warn("Could not access localStorage for token");
      }

      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token && token.trim()) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers,
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.message || `Agent API error: ${response.statusText}`;

        // Log the error for debugging
        console.error("Agent API error:", errorMessage);
        throw new Error(errorMessage);
      }

      const result = await response.json();

      // Validate response structure
      if (!result.message || typeof result.success !== 'boolean') {
        throw new Error("Invalid response format from agent API");
      }

      return result;
    } catch (error) {
      console.error("Agent API error:", error);
      // Re-throw with more context if it's a known error
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error("Network error: Unable to connect to the AI service. Please check your internet connection.");
      }
      throw error;
    }
  },

  /**
   * Get the agent's capabilities and supported operations
   * Useful for showing users what the agent can do
   *
   * @returns Promise with agent capabilities
   *
   * @example
   * const capabilities = await agentService.getCapabilities();
   * console.log(capabilities.agent_name); // "Task Manager Assistant"
   */
  getCapabilities: async (): Promise<AgentCapabilities> => {
    try {
      let token = null;
      try {
        token = typeof window !== "undefined" ? localStorage.getItem("accessToken") : null;
      } catch (error) {
        console.warn("Could not access localStorage for token");
      }

      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token && token.trim()) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/capabilities`, {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || errorData.message || `Failed to get capabilities: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Failed to get agent capabilities:", error);
      throw error;
    }
  },

  /**
   * Detect if a message is task-related and should be sent to the agent
   *
   * @param message - User message to check
   * @returns true if message appears to be task-related
   */
  isTaskRelated: (message: string): boolean => {
    const taskKeywords = [
      "task",
      "add",
      "create",
      "delete",
      "remove",
      "update",
      "change",
      "mark",
      "completed",
      "pending",
      "priority",
      "urgent",
      "deadline",
      "due",
      "finish",
      "complete",
      "status",
      "project",
      "meeting",
    ];

    const lowerMessage = message.toLowerCase();
    return taskKeywords.some((keyword) => lowerMessage.includes(keyword));
  },
};

export default agentService;
