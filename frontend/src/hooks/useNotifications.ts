/**
 * Hook for managing browser push notifications.
 */

import { useState, useEffect, useCallback } from 'react';

interface NotificationState {
  supported: boolean;
  permission: NotificationPermission;
  subscription: PushSubscription | null;
}

export function useNotifications() {
  const [state, setState] = useState<NotificationState>({
    supported: false,
    permission: 'default',
    subscription: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if notifications are supported
    const supported = 'Notification' in window && 'serviceWorker' in navigator;
    setState((prev) => ({
      ...prev,
      supported,
      permission: supported ? Notification.permission : 'denied',
    }));

    // Register service worker
    if (supported) {
      registerServiceWorker();
    }
  }, []);

  const registerServiceWorker = async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker registered:', registration.scope);

      // Check for existing subscription
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        setState((prev) => ({ ...prev, subscription }));
      }
    } catch (err) {
      console.error('Service Worker registration failed:', err);
    }
  };

  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!state.supported) {
      setError('Notifications not supported in this browser');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const permission = await Notification.requestPermission();
      setState((prev) => ({ ...prev, permission }));

      if (permission === 'granted') {
        return true;
      } else {
        setError('Notification permission denied');
        return false;
      }
    } catch (err) {
      setError('Failed to request notification permission');
      return false;
    } finally {
      setLoading(false);
    }
  }, [state.supported]);

  const subscribe = useCallback(async (): Promise<PushSubscription | null> => {
    if (!state.supported || state.permission !== 'granted') {
      const granted = await requestPermission();
      if (!granted) return null;
    }

    setLoading(true);
    setError(null);

    try {
      const registration = await navigator.serviceWorker.ready;

      // Get VAPID key from backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/notifications/vapid-key`);
      const { vapid_public_key } = await response.json();

      if (!vapid_public_key) {
        throw new Error('VAPID key not configured');
      }

      // Convert VAPID key to Uint8Array
      const applicationServerKey = urlBase64ToUint8Array(vapid_public_key);

      // Subscribe to push notifications
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey,
      });

      // Send subscription to backend
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/notifications/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          endpoint: subscription.endpoint,
          keys: {
            p256dh: arrayBufferToBase64(subscription.getKey('p256dh')),
            auth: arrayBufferToBase64(subscription.getKey('auth')),
          },
        }),
      });

      setState((prev) => ({ ...prev, subscription }));
      return subscription;
    } catch (err) {
      setError('Failed to subscribe to notifications');
      console.error('Subscription error:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [state.supported, state.permission, requestPermission]);

  const unsubscribe = useCallback(async (): Promise<boolean> => {
    if (!state.subscription) return true;

    setLoading(true);
    setError(null);

    try {
      await state.subscription.unsubscribe();

      // Notify backend
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/notifications/unsubscribe`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      setState((prev) => ({ ...prev, subscription: null }));
      return true;
    } catch (err) {
      setError('Failed to unsubscribe from notifications');
      return false;
    } finally {
      setLoading(false);
    }
  }, [state.subscription]);

  const sendTestNotification = useCallback(async () => {
    if (!state.subscription) {
      setError('Not subscribed to notifications');
      return;
    }

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/notifications/test`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
    } catch (err) {
      setError('Failed to send test notification');
    }
  }, [state.subscription]);

  return {
    ...state,
    loading,
    error,
    requestPermission,
    subscribe,
    unsubscribe,
    sendTestNotification,
    isSubscribed: !!state.subscription,
  };
}

// Helper functions
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function arrayBufferToBase64(buffer: ArrayBuffer | null): string {
  if (!buffer) return '';
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

export default useNotifications;
