"use client";

import { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setTasks, clearError, updateTask, deleteTask } from "@/redux/slices/taskSlice";
import agentService from "@/services/agentService";
import { tasksService } from "@/services/tasksService";
import { showToast } from "@/utils/toastUtils";
import type { Task } from "@/redux/slices/taskSlice";
import type { AppDispatch, RootState } from "@/redux/store";

// Extend the Window interface to include SpeechRecognition
declare global {
  interface Window {
    webkitSpeechRecognition: any; // eslint-disable-line @typescript-eslint/no-explicit-any
  }
}

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  isError?: boolean;
}

export default function ChatBot() {
  const dispatch = useDispatch<AppDispatch>();
  const currentTasks = useSelector((state: RootState) => state.tasks.items);
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Hello! 👋 I'm your AI Task Manager Assistant. I can help you:\n• Create tasks\n• Update tasks\n• Delete tasks\n• Get task details\n\nJust describe what you'd like to do! You can also use voice commands 🎤",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const inputValueRef = useRef<string>("");

  // Keep input value ref in sync with state
  useEffect(() => {
    inputValueRef.current = inputValue;
  }, [inputValue]);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize Speech Recognition API
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition; // eslint-disable-line @typescript-eslint/no-explicit-any

      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = "en-US";

        recognitionRef.current.onstart = () => {
          setIsListening(true);
          setTranscript("");
        };

        recognitionRef.current.onresult = (event: SpeechRecognitionEvent) => {
          let interim = "";
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcriptSegment = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              setInputValue((prev) => prev + transcriptSegment + " ");
            } else {
              interim += transcriptSegment;
            }
          }
          setTranscript(interim);
        };

        recognitionRef.current.onerror = (event: SpeechRecognitionErrorEvent) => {
          console.error("Speech recognition error:", event.error);
          const errorMsg =
            event.error === "not-allowed"
              ? "Microphone permission denied"
              : `Voice error: ${event.error}`;
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              text: `❌ ${errorMsg}`,
              sender: "bot",
              timestamp: new Date(),
              isError: true,
            },
          ]);
        };

        recognitionRef.current.onend = () => {
          setIsListening(false);
          setTranscript("");
        };
      }
    }
  }, []);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = () => {
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("accessToken");
        setIsAuthenticated(!!token);
      }
    };

    checkAuth();

    // Listen for storage changes (login/logout in other tabs)
    window.addEventListener("storage", checkAuth);
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  // Close modal when escape key is pressed, toggle voice with spacebar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape to close chat
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }

      // Spacebar to toggle voice recording (when chat is open and not typing in input)
      if (e.code === "Space" && isOpen && !isLoading && e.target === document.body) {
        e.preventDefault();
        handleVoiceCommand();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, isLoading]);

  // Core message sending logic (used by both form submit and voice auto-submit)
  const processMessage = async (userInput: string) => {
    if (!userInput.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: userInput,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Check if user is authenticated
      if (!isAuthenticated) {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: "⚠️ Please log in to use the task manager. The agent needs authentication to manage your tasks.",
          sender: "bot",
          timestamp: new Date(),
          isError: true,
        };
        setMessages((prev) => [...prev, errorMessage]);
        setIsLoading(false);
        return;
      }

      // Check if message is task-related, otherwise use simple response
      if (agentService.isTaskRelated(userInput)) {
        // Send to agent API for task management
        try {
          const response = await agentService.sendMessage(userInput);

          const botResponse: Message = {
            id: (Date.now() + 1).toString(),
            text: response.message,
            sender: "bot",
            timestamp: new Date(),
            isError: !response.success,
          };
          setMessages((prev) => [...prev, botResponse]);

          // Show toast notification based on action
          if (response.success) {
            switch (response.action) {
              case "create":
                showToast.taskCreated(response.task_data?.title || "task");
                break;
              case "update":
                showToast.taskUpdated(response.task_data?.title || "task");
                break;
              case "delete":
                showToast.taskDeleted(response.task_data?.title || "task");
                break;
              case "get":
              case "insights":
                showToast.chatSuccess("Task insights retrieved");
                break;
              case "productivity":
                showToast.chatSuccess("Productivity insights retrieved");
                break;
              default:
                showToast.chatSuccess("Operation completed");
            }
          }

          // Refresh task list from API after every successful agent response
          // This ensures we have the latest data from the backend
          if (response.success) {
            try {
              const tasksResponse = await tasksService.getTasks();
              const tasksList = tasksResponse.tasks;

              // Update Redux with fresh task list for real-time UI updates
              if (tasksList.length > 0) {
                dispatch(setTasks(tasksList));
              } else if (response.action === "delete") {
                // If delete action, task list might be empty, still update to reflect deletion
                dispatch(setTasks(tasksList));
              }
              dispatch(clearError());
            } catch (fetchError: unknown) {
              console.error("Failed to refresh task list:", fetchError);
              // Fallback: Try to parse action from response and update Redux directly
              try {
                if (response.action === "delete" && response.task_data?.id) {
                  // Delete from Redux if API refresh fails
                  dispatch(deleteTask(response.task_data.id));
                } else if (response.action === "update" && response.task_data?.id) {
                  // Update Redux if API refresh fails
                  const updatedTask: Task = {
                    id: response.task_data.id,
                    owner_id: currentTasks[0]?.owner_id || "",
                    title: response.task_data.title || "",
                    status: response.task_data.status || "pending",
                    priority: response.task_data.priority || "medium",
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                  };
                  dispatch(updateTask(updatedTask));
                }
              } catch (fallbackError) {
                console.error("Fallback Redux update also failed:", fallbackError);
              }
            }
          }
        } catch (error: unknown) {
          // Handle API errors gracefully
          const errorMessage =
            (error as Record<string, unknown>)?.response?.data?.detail ||
            (error as Record<string, unknown>)?.message ||
            "Failed to process your request. Please try again.";
          showToast.chatError(errorMessage);
          const botResponse: Message = {
            id: (Date.now() + 1).toString(),
            text: `❌ ${errorMessage}`,
            sender: "bot",
            timestamp: new Date(),
            isError: true,
          };
          setMessages((prev) => [...prev, botResponse]);
        }
      } else {
        // Use simple response for general questions
        const simpleResponse = generateSimpleResponse(userInput);
        const botResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: simpleResponse,
          sender: "bot",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botResponse]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userInput = inputValue;
    setInputValue("");
    await processMessage(userInput);
  };

  // Set up voice auto-submit handler after processMessage is available
  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.onend = () => {
        setIsListening(false);
        setTranscript("");

        // Auto-submit message if there's text in input field
        if (inputValueRef.current.trim()) {
          processMessage(inputValueRef.current.trim());
          setInputValue(""); // Clear input after sending
        }
      };
    }
  }, [processMessage]);

  const handleVoiceCommand = () => {
    if (!recognitionRef.current) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: "❌ Speech recognition not supported in your browser. Please use Chrome, Edge, or Safari.",
          sender: "bot",
          timestamp: new Date(),
          isError: true,
        },
      ]);
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error("Error starting speech recognition:", error);
      }
    }
  };

  const generateSimpleResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();

    // Greetings
    if (input.includes("hello") || input.includes("hi") || input.includes("hey")) {
      return "Hello! 👋 How can I assist you with your tasks today?";
    }

    // Help requests
    if (input.includes("help") || input.includes("what can you do") || input.includes("capabilities")) {
      return "I'm your Task Manager Assistant! I can:\n• ✅ Create new tasks with details\n• ✏️ Update existing tasks\n• 🗑️ Delete tasks\n• 📋 Get task information\n\n💡 Keyboard Shortcut: Press SPACEBAR to use voice commands!\n\nTry asking me things like:\n'Add a task called Buy groceries with high priority'\n'Mark my project as completed'\n'Delete the old task'";
    }

    // Thank you
    if (input.includes("thank") || input.includes("thanks")) {
      return "You're welcome! Feel free to ask if you need help with anything else. 😊";
    }

    // Default response for general questions
    return "I'm here to help you manage your tasks! Try asking me to:\n• Create a new task\n• Update a task\n• Delete a task\n• Get task details\n\n💡 Tip: Click the 🎤 button or press SPACEBAR for voice commands!\n\nWhat would you like to do?";
  };

  return (
    <>
      {/* Chat Window - Floating Position */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 w-96 bg-white rounded-lg shadow-2xl flex flex-col z-40 max-sm:w-80 max-sm:bottom-2 max-sm:right-2" style={{ height: '80vh', maxHeight: 'calc(100vh - 2rem)' }}>
          {/* Header */}
          <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-t-lg flex justify-between items-center">
            <div>
              <h3 className="font-semibold text-lg">AI Assistant</h3>
              <p className="text-xs text-green-100">Always here to help</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-green-700 rounded-full p-1 transition"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50 space-y-3">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    message.sender === "user"
                      ? "bg-green-500 text-white rounded-br-none"
                      : message.isError
                      ? "bg-red-50 text-red-800 border border-red-200 rounded-bl-none"
                      : "bg-white text-gray-800 border border-gray-200 rounded-bl-none"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap break-words">
                    {message.text}
                  </p>
                  <p
                    className={`text-xs mt-1 ${
                      message.sender === "user"
                        ? "text-green-100"
                        : message.isError
                        ? "text-red-600"
                        : "text-gray-500"
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg rounded-bl-none px-4 py-2">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4 bg-white rounded-b-lg">
            {/* Transcription Display */}
            {isListening && transcript && (
              <div className="mb-2 p-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-700 italic">
                🎤 {transcript}
              </div>
            )}
            <form ref={formRef} onSubmit={handleSendMessage} className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={isListening ? "Listening... 🎤" : "Type or speak..."}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-green-500"
                disabled={isLoading}
              />
              {/* Voice Button */}
              <button
                type="button"
                onClick={handleVoiceCommand}
                disabled={isLoading}
                title={isListening ? "Stop listening" : "Start voice command"}
                className={`px-3 py-2 rounded-lg transition font-medium text-sm flex items-center gap-1 ${
                  isListening
                    ? "bg-red-500 hover:bg-red-600 text-white"
                    : "bg-blue-500 hover:bg-blue-600 text-white"
                } disabled:opacity-50`}
              >
                <svg
                  className={`w-5 h-5 ${isListening ? "animate-pulse" : ""}`}
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z" />
                </svg>
              </button>
              {/* Send Button */}
              <button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition font-medium text-sm"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Floating Toggle Button - Only show when chat is closed */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="fixed bottom-6 right-6 w-16 h-16 rounded-full shadow-lg hover:shadow-xl transition transform hover:scale-110 z-50 flex items-center justify-center bg-green-500 hover:bg-green-600 text-white"
          title="Open chat"
        >
          <svg
            className="w-8 h-8"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M16.6915026,12.4744748 L3.50612381,13.2599618 C3.19218622,13.2599618 3.03521743,13.4170592 3.03521743,13.5741566 L1.15159189,20.0151496 C0.8376543,20.8006365 0.99,21.89 1.77946707,22.52 C2.41,22.99 3.50612381,23.1 4.13399899,22.8429026 L21.714504,14.0454487 C22.6563168,13.5741566 23.1272231,12.6315722 22.9702544,11.6889879 L4.13399899,1.16151496 C3.34915502,0.9 2.40734225,0.9 1.77946707,1.4429026 C0.994623095,2.08535412 0.837654326,3.01492849 1.15159189,3.97751279 L3.03521743,10.4184309 C3.03521743,10.5755283 3.34915502,10.7326256 3.50612381,10.7326256 L16.6915026,11.5181125 C16.6915026,11.5181125 17.1624089,11.5181125 17.1624089,12.0609051 C17.1624089,12.4744748 16.6915026,12.4744748 16.6915026,12.4744748 Z" />
          </svg>
        </button>
      )}
    </>
  );
}
