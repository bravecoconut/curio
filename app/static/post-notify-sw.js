self.addEventListener("install", (event) => {
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(clients.claim());
});

const notifyClients = async (message) => {
    const allClients = await clients.matchAll({
        type: "window",
        includeUncontrolled: true,
    });

    for (const client of allClients) {
        client.postMessage(message);
    }
};

const handleCreatePost = async () => {
    await notifyClients({ type: "CREATE_POST_STARTED" });

    try {
        const response = await fetch("/api/create_post", {
            method: "POST",
            credentials: "include",
        });
        const result = await response.json();

        if (!response.ok || !result.status) {
            const error = result.data?.error || "Failed to create post";
            await notifyClients({ type: "CREATE_POST_ERROR", error });
            return;
        }

        const postId = result.data.new_post;

        await self.registration.showNotification("Your new post is ready", {
            body: "Tap to view your post",
            data: { postId },
            tag: `post-${postId}`,
        });

        await notifyClients({ type: "POST_CREATED", postId });
    } catch (error) {
        await notifyClients({
            type: "CREATE_POST_ERROR",
            error: "Could not create post",
        });
    }
};

self.addEventListener("message", (event) => {
    if (event.data?.type !== "CREATE_POST") return;

    event.waitUntil(handleCreatePost());
});

self.addEventListener("notificationclick", (event) => {
    event.notification.close();

    const postId = event.notification.data?.postId;
    if (!postId) return;

    event.waitUntil(
        (async () => {
            await fetch(`/api/get_one_post/${postId}`, {
                credentials: "include",
            });

            const url = `/${postId}`;
            const windowClients = await clients.matchAll({ type: "window" });

            for (const client of windowClients) {
                if ("focus" in client) {
                    if ("navigate" in client) {
                        await client.navigate(url);
                    } else {
                        client.postMessage({ type: "OPEN_POST", postId });
                    }
                    return client.focus();
                }
            }

            return clients.openWindow(url);
        })()
    );
});
