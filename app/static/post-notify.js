let postNotifyRegistration = null;

const initPostNotify = async () => {
    if (!("serviceWorker" in navigator)) return null;

    try {
        postNotifyRegistration = await navigator.serviceWorker.register(
            "/post-notify-sw.js",
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
        onError?.("Allow notifications to get alerted when your post is ready");
        return false;
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

    navigator.serviceWorker?.addEventListener("message", (event) => {
        if (event.data?.type === "OPEN_POST" && event.data.postId) {
            window.location.href = `/${event.data.postId}`;
        }
    });
});
