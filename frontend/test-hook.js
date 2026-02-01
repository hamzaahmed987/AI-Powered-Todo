// Simple test to verify the useAuth hook export
import { useAuth } from './src/hooks/useAuth';

console.log('useAuth function is available:', typeof useAuth === 'function');

export { useAuth }; // Re-export for testing