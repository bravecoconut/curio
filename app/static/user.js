const username = window.PROFILE_USERNAME;
const isOwnProfile = window.IS_OWN_PROFILE;
const postsGrid = document.getElementById("postsGrid");
const postsTrigger = document.getElementById("postsTrigger");
const noPostsEl = document.getElementById("noPosts");
const shareLinkBtn = document.getElementById("shareLinkBtn");
const logoutBtn = document.getElementById("logoutBtn");
const profileUsernameEl = document.getElementById("profileUsername");
const profileNameEl = document.getElementById("profileName");
const avatarImgEl = document.getElementById("avatarImg");
const headerProfileAvatarEl = document.getElementById("headerProfileAvatar");
const createPostBtn = document.getElementById("createNewPostButton");

let posts = [];
let renderedCount = 0;
let isLoadingPosts = false;
let hasMorePosts = true;
let profileAccountId = null;
let isCreatingPost = false;

const timeAgo = (unixSeconds) => {
    const diffSeconds = (Date.now() - unixSeconds * 1000) / 1000;
    const minutes = Math.floor(diffSeconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const months = Math.floor(days / 30);
    const years = Math.floor(days / 365);
    const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

    if (years > 0) return rtf.format(-years, "year");
    if (months > 0) return rtf.format(-months, "month");
    if (days > 0) return rtf.format(-days, "day");
    if (hours > 0) return rtf.format(-hours, "hour");
    if (minutes > 0) return rtf.format(-minutes, "minute");
    return rtf.format(-Math.floor(diffSeconds), "second");
};

const showToast = (message) => {
    if (typeof showNavToast === "function") {
        showNavToast(message);
        return;
    }

    const existing = document.getElementById("toast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.id = "toast";
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("hidden");
        setTimeout(() => toast.remove(), 300);
    }, 2500);
};

const closeProfileModal = () => {
    const overlay = document.getElementById("profileModalOverlay");
    if (overlay) overlay.remove();
    document.body.classList.remove("modal-open");
};

const showProfileModal = ({ title, bodyHTML, submitLabel = "save", onSubmit }) => {
    closeProfileModal();

    const overlay = document.createElement("div");
    overlay.id = "profileModalOverlay";
    overlay.innerHTML = `
        <div id="profileModal" role="dialog" aria-modal="true">
            <h3>${title}</h3>
            <div id="profileModalBody">${bodyHTML}</div>
            <div id="profileModalActions">
                <button type="button" id="profileModalCancel">cancel</button>
                <button type="button" id="profileModalSubmit">${submitLabel}</button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.classList.add("modal-open");

    const submitBtn = document.getElementById("profileModalSubmit");
    const cancelBtn = document.getElementById("profileModalCancel");

    cancelBtn.addEventListener("click", closeProfileModal);
    overlay.addEventListener("click", (event) => {
        if (event.target === overlay) closeProfileModal();
    });

    submitBtn.addEventListener("click", async () => {
        submitBtn.disabled = true;
        submitBtn.textContent = "saving...";

        try {
            const shouldClose = await onSubmit();
            if (shouldClose !== false) {
                closeProfileModal();
            }
        } catch (error) {
            showToast(error.message || "Something went wrong");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = submitLabel;
        }
    });
};

const refreshNavAvatar = () => {
    if (!profileAccountId) return;

    const cacheBust = `?t=${Date.now()}`;
    const navAvatar = document.querySelector("#profileView #profileAvatar img");
    if (navAvatar) {
        navAvatar.src = `/api/profile_image/${profileAccountId}${cacheBust}`;
    }
};

const openChangeUsernameModal = () => {
    showProfileModal({
        title: "change username",
        bodyHTML: `
            <label for="newUsernameInput">new username</label>
            <input id="newUsernameInput" type="text" value="${profileUsernameEl.textContent}" autocomplete="username">
        `,
        onSubmit: async () => {
            const newUsername = document.getElementById("newUsernameInput").value.trim();
            if (!newUsername) {
                showToast("username cannot be empty");
                return false;
            }

            const response = await fetch("/api/change_username", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ new_username: newUsername }),
            });
            const result = await response.json();

            if (!response.ok || !result.status) {
                showToast(result.data?.error || "Could not change username");
                return false;
            }

            window.location.href = `/${result.data.username}`;
        },
    });
};

const openChangeNameModal = () => {
    showProfileModal({
        title: "change name",
        bodyHTML: `
            <label for="newNameInput">new name</label>
            <input id="newNameInput" type="text" value="${profileNameEl.textContent}" autocomplete="name">
        `,
        onSubmit: async () => {
            const newName = document.getElementById("newNameInput").value.trim();
            if (!newName) {
                showToast("name cannot be empty");
                return false;
            }

            const response = await fetch("/api/change_name", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ new_name: newName }),
            });
            const result = await response.json();

            if (!response.ok || !result.status) {
                showToast(result.data?.error || "Could not change name");
                return false;
            }

            profileNameEl.textContent = result.data.user_name;
            showToast("name updated");
        },
    });
};

const openChangeAvatarModal = () => {
    showProfileModal({
        title: "change avatar",
        submitLabel: "upload",
        bodyHTML: `
            <label for="newAvatarInput">choose image</label>
            <input id="newAvatarInput" type="file" accept="image/*">
        `,
        onSubmit: async () => {
            const fileInput = document.getElementById("newAvatarInput");
            const file = fileInput.files?.[0];

            if (!file) {
                showToast("choose an image first");
                return false;
            }

            const formData = new FormData();
            formData.append("image", file);

            const response = await fetch("/api/change_profile_image", {
                method: "POST",
                credentials: "include",
                body: formData,
            });
            const result = await response.json();

            if (!response.ok || !result.status) {
                showToast(result.data?.error || "Could not change avatar");
                return false;
            }

            const cacheBust = `?t=${Date.now()}`;
            avatarImgEl.src = `/api/profile_image/${profileAccountId}${cacheBust}`;
            refreshNavAvatar();
            showToast("avatar updated");
        },
    });
};

const setupOwnProfileActions = () => {
    profileUsernameEl.classList.add("profile-editable");
    profileNameEl.classList.add("profile-editable");
    headerProfileAvatarEl.classList.add("profile-editable");

    profileUsernameEl.addEventListener("click", openChangeUsernameModal);
    profileNameEl.addEventListener("click", openChangeNameModal);
    headerProfileAvatarEl.addEventListener("click", openChangeAvatarModal);

    if (createPostBtn) {
        createPostBtn.addEventListener("click", createNewPost);
    }

    navigator.serviceWorker?.addEventListener("message", handlePostServiceMessage);
};

const handlePostCreated = (postId) => {
    if (postId) {
        // Show notification with click handler
        if ("Notification" in window && Notification.permission === "granted") {
            const currentUrl = window.location.href;
            // window.location.href = currentUrl;
            window.location.href = `/${postId}`;
            new Notification("Your new post is ready", {
                body: "ready creation post",
                icon: "/static/assets/views.svg",
                tag: `post-${postId}`,
            }).onclick = () => {
                window.location.href = `/${postId}`;
            };
        } else {
            // Fallback: redirect directly if no notification permission
            window.location.href = `/${postId}`;
        }
        // Refresh posts grid to show new post
        if (isOwnProfile) {
            refreshPosts();
            console.log(currentUrl); 
            // Output: "https://example.com"
        }
    } else if (isOwnProfile) {
        // Fallback: reload if no postId but on own profile
        window.location.reload();
    }
};

const handlePostServiceMessage = (event) => {
    const { type, error, postId } = event.data || {};

    if (type === "CREATE_POST_STARTED") {
        isCreatingPost = true;
        if (createPostBtn) {
            createPostBtn.disabled = true;
            createPostBtn.textContent = "creating post...";
        }
        showToast("creating post...");
        return;
    }

    if (type === "CREATE_POST_ERROR") {
        isCreatingPost = false;
        if (createPostBtn) {
            createPostBtn.disabled = false;
            createPostBtn.textContent = "create new post";
        }
        showToast(error || "Failed to create post");
        return;
    }

    if (type === "POST_CREATED") {
        isCreatingPost = false;
        if (createPostBtn) {
            createPostBtn.disabled = false;
            createPostBtn.textContent = "create new post";
        }
        handlePostCreated(postId);
    }
};

const createNewPost = async () => {
    if (isCreatingPost) return;

    const onStart = () => {
        isCreatingPost = true;
        if (createPostBtn) {
            createPostBtn.disabled = true;
            createPostBtn.textContent = "creating post...";
        }
        showToast("creating post...");
    };

    const onError = (message) => {
        showToast(message);
    };

    const onComplete = (postId) => {
        handlePostCreated(postId);
    };

    const resetCreateButton = () => {
        isCreatingPost = false;
        if (createPostBtn) {
            createPostBtn.disabled = false;
            createPostBtn.textContent = "create new post";
        }
    };

    // Use fallback direct fetch instead of service worker for reliability
    if (typeof fallbackCreatePost === "function") {
        await fallbackCreatePost({
            onStart,
            onComplete: (postId) => {
                resetCreateButton();
                onComplete(postId);
            },
            onError: (message) => {
                resetCreateButton();
                onError(message);
            },
        });
    }
};

const copyShareLink = async () => {
    const link = `${window.location.origin}/${username}`;
    try {
        await navigator.clipboard.writeText(link);
        showToast("profile link copied");
    } catch {
        showToast(link);
    }
};

const loadProfile = async () => {
    const response = await fetch(`/api/user/${encodeURIComponent(username)}`);
    const result = await response.json();

    if (!response.ok || !result.status) {
        throw new Error(result.data?.error || "Could not load profile");
    }

    const user = result.data.user;
    profileAccountId = user.account_id;
    profileUsernameEl.textContent = user.username;
    profileNameEl.textContent = user.user_name;
    avatarImgEl.src = `/api/profile_image/${user.account_id}`;
    document.title = `${user.username} — CURIO`;
};

const renderPosts = () => {
    for (let index = renderedCount; index < posts.length; index++) {
        const post = posts[index];
        const postEl = document.createElement("div");
        postEl.className = "postCard";
        postEl.innerHTML = `
            <img src="/api/post_image/${post.id}" alt="post image">
            <div class="postCardMeta">
                <span>${timeAgo(post.date_created)}</span>
                <span>${post.post_views} views${window.IS_OWN_PROFILE && post.post_private ? " · private" : ""}</span>
            </div>
        `;

        postEl.addEventListener("click", () => {
            window.location.href = `/${post.id}`;
        });

        postsGrid.appendChild(postEl);
    }

    renderedCount = posts.length;
};

const loadPosts = async () => {
    if (isLoadingPosts || !hasMorePosts) return;

    isLoadingPosts = true;
    const start = posts.length + 1;
    const end = posts.length + 12;

    try {
        const response = await fetch(
            `/api/user/${encodeURIComponent(username)}/posts?start=${start}&end=${end}`,
            { credentials: "include" }
        );
        const result = await response.json();

        if (!response.ok || !result.status) {
            throw new Error(result.data?.error || "Could not load posts");
        }

        const fetchedPosts = result.data.posts || [];
        if (fetchedPosts.length === 0) {
            hasMorePosts = false;
            if (posts.length === 0) {
                noPostsEl.classList.remove("hidden");
            }
            return;
        }

        posts = posts.concat(fetchedPosts);
        renderPosts();

        if (fetchedPosts.length < end - start + 1) {
            hasMorePosts = false;
            if (posts.length === 0) {
                noPostsEl.classList.remove("hidden");
            }
        }
    } catch (error) {
        console.error(error);
        showToast(error.message || "Failed to load posts");
    } finally {
        isLoadingPosts = false;
    }
};

const refreshPosts = async () => {
    posts = [];
    renderedCount = 0;
    hasMorePosts = true;
    isLoadingPosts = false;
    noPostsEl.classList.add("hidden");
    await loadPosts();
};

const postsObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                loadPosts();
            }
        });
    },
    { threshold: 0.1 }
);

document.addEventListener("DOMContentLoaded", async () => {
    await initAppNav({ contentSelector: "#container" });

    shareLinkBtn.addEventListener("click", copyShareLink);

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            window.location.href = "/logout";
        });
    }

    if (isOwnProfile) {
        setupOwnProfileActions();
    }

    postsObserver.observe(postsTrigger);

    try {
        await loadProfile();
        await loadPosts();
    } catch (error) {
        console.error(error);
        showToast(error.message || "Failed to load profile");
    }
});
