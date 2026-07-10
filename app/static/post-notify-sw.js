// app/static/post-notify-sw.js

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
    await notifyClients({ type: "LOG", message: "Starting fetch to /api/create_post" });

    try {
        const response = await fetch("/api/create_post", {
            method: "POST",
            credentials: "include",
            headers: {
                'Content-Type': 'application/json',
            },
        });

        await notifyClients({ type: "LOG", message: `Fetch response status: ${response.status}` });

        if (!response.ok) {
            const errorText = await response.text();
            await notifyClients({ type: "LOG", message: `Response not OK: ${errorText}` });
            await notifyClients({ type: "CREATE_POST_ERROR", error: `HTTP ${response.status}` });
            return;
        }

        const result = await response.json();
        await notifyClients({ type: "LOG", message: `Fetch result: ${JSON.stringify(result)}` });

        if (!result.status) {
            const error = result.data?.error || result.error || "Failed to create post";
            await notifyClients({ type: "LOG", message: `Error: ${error}` });
            await notifyClients({ type: "CREATE_POST_ERROR", error });
            return;
        }

        const postId = result.data?.new_post;
        if (!postId) {
            await notifyClients({ type: "LOG", message: "No postId in response" });
            await notifyClients({ type: "CREATE_POST_ERROR", error: "No post ID returned" });
            return;
        }
        
        location.reload();
        await notifyClients({ type: "LOG", message: `post id:${postId}` });

        await self.registration.showNotification("Your new post is ready", {
            body: "Tap to view your post",
            data: { postId },
            tag: `post-${postId}`,
        });

        await notifyClients({ type: "LOG", message: "Sending POST_CREATED message" });
        await notifyClients({ type: "POST_CREATED", postId });
    } catch (error) {
        await notifyClients({ type: "LOG", message: `Fetch error: ${error.message}` });
        await notifyClients({
            type: "CREATE_POST_ERROR",
            error: "Could not create post",
        });
    }
};

self.addEventListener("message", (event) => {
    if (event.data?.type !== "CREATE_POST") return;

    console.log("Service worker received CREATE_POST message");
    
    event.waitUntil(
        (async () => {
            try {
                await handleCreatePost();
            } catch (error) {
                console.error("Service worker error in handleCreatePost:", error);
                await notifyClients({
                    type: "CREATE_POST_ERROR",
                    error: `Service worker error: ${error.message}`,
                });
            }
        })()
    );
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
