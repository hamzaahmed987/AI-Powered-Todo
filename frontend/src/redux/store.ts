import { configureStore } from "@reduxjs/toolkit";
import { persistStore, persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage";
import authReducer from "./slices/authSlice";
import taskReducer from "./slices/taskSlice";

// Auth persist configuration - only persist auth reducer
const authPersistConfig = {
  key: "auth",
  storage,
  whitelist: ["accessToken", "user", "isAuthenticated"], // Only persist essential auth data
};

// Tasks persist configuration
const tasksPersistConfig = {
  key: "tasks",
  storage,
  whitelist: ["items"], // Only persist task items, not loading/error states
};

// Create persisted reducers
const persistedAuthReducer = persistReducer(authPersistConfig, authReducer);
const persistedTasksReducer = persistReducer(tasksPersistConfig, taskReducer);

// Configure store
export const store = configureStore({
  reducer: {
    auth: persistedAuthReducer,
    tasks: persistedTasksReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types for serialization check
        ignoredActions: ["persist/PERSIST", "persist/REHYDRATE"],
        // Ignore these paths in the state
        ignoredPaths: ["auth", "tasks"],
      },
    }),
});

// Create persistor
export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
