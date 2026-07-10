// app/static/post-notify.js

let postNotifyRegistration = null;

const initPostNotify = async () => {
    if (!("serviceWorker" in navigator)) return null;

    try {
        postNotifyRegistration = await navigator.serviceWorker.register(
            "/static/post-notify-sw.js",
            { scope: "/" }
        );
        return postNotifyRegistration;
    } catch (error) {
        console.error("Service worker registration failed:", error);
        return null;
    }
};

const requestPostNotificationPermission = async () => {
    if (!("Notification" in window)) {
        return false;
    }

    if (Notification.permission === "granted") {
        return true;
    }

    if (Notification.permission === "denied") {
        return false;
    }

    const permission = await Notification.requestPermission();
    return permission === "granted";
};

const startCreatePost = async ({ onStart, onError } = {}) => {
    const hasPermission = await requestPostNotificationPermission();
    if (!hasPermission) {
        console.warn("Notification permission not granted, proceeding without notifications");
        // Don't return false - allow post creation even without notifications
    }

    if (!postNotifyRegistration?.active) {
        await initPostNotify();
    }

    const activeWorker =
        postNotifyRegistration?.active ||
        (await navigator.serviceWorker.ready).active;

    if (!activeWorker) {
        onError?.("Could not start post creation service");
        return false;
    }

    console.log("Sending CREATE_POST message to service worker");
    activeWorker.postMessage({ type: "CREATE_POST" });
    return true;
};

const fallbackCreatePost = async ({ onStart, onComplete, onError } = {}) => {
    onStart?.();

    try {
        const response = await fetch("/api/create_post", {
            method: "POST",
            credentials: "include",
        });
        const result = await response.json();

        if (!response.ok || !result.status) {
            throw new Error(result.data?.error || "Failed to create post");
        }

        onComplete?.(result.data.new_post);
        return result.data.new_post;
    } catch (error) {
        onError?.(error.message || "Failed to create post");
        return null;
    }
};

window.initPostNotify = initPostNotify;
window.startCreatePost = startCreatePost;
window.fallbackCreatePost = fallbackCreatePost;

document.addEventListener("DOMContentLoaded", () => {
    initPostNotify();

    // Handle messages from service worker
    navigator.serviceWorker?.addEventListener("message", (event) => {
        const { type, postId, error, message } = event.data || {};

        if (type === "LOG") {
            console.log(message);
        } else if (type === "CREATE_POST_STARTED") {
            console.log("Post creation started");
        } else if (type === "POST_CREATED") {
            console.log(`Post created successfully: ${postId}`);
            // Let page-specific handlers decide what to do (redirect, reload, etc.)
        } else if (type === "CREATE_POST_ERROR") {
            console.error("Post creation error:", error);
        } else if (type === "OPEN_POST" && postId) {
            window.location.href = `/${postId}`;
        }
    });
});