// app/static/post.js

const postId = window.POST_ID;
const isOwnPost = window.IS_OWN_POST;
const postNotFound = window.POST_NOT_FOUND;

const postImage = document.getElementById("postImage");
const ownerAvatar = document.getElementById("ownerAvatar");
const ownerUsername = document.getElementById("ownerUsername");
const postProfileView = document.getElementById("postProfileView");
const postViews = document.getElementById("postViews");
const postTimeAgo = document.getElementById("postTimeAgo");
const postFactText = document.getElementById("postFactText");
const postResearchText = document.getElementById("postResearchText");
const shareLinkBtn = document.getElementById("shareLinkBtn");
const privacyToggle = document.getElementById("privacyToggle");

let currentPost = null;

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

const updatePrivacyLabel = (isPrivate) => {
    if (!privacyToggle) return;
    privacyToggle.textContent = `${isPrivate ? "private" : "public"}`;
};

const copyShareLink = async () => {
    const link = `${window.location.origin}/${postId}`;
    try {
        await navigator.clipboard.writeText(link);
        showToast("post link copied");
    } catch {
        showToast(link);
    }
};

const loadOwner = async (accountId) => {
    const response = await fetch(`/api/get_user_username/${accountId}`);
    const result = await response.json();
    const username = result.status ? result.data.user.username : "unknown";

    ownerUsername.textContent = username;
    ownerAvatar.src = `/api/profile_image/${accountId}`;
    postProfileView.onclick = () => move_to_user_page(username);
};

const loadPost = async () => {
    if (postNotFound) {
        postImage.style.display = "none";
        return;
    }

    const response = await fetch(`/api/get_one_post/${postId}`, {
        credentials: "include",
    });
    const result = await response.json();

    if (!response.ok || !result.status) {
        throw new Error(result.data?.error || "Could not load post");
    }

    currentPost = result.data.post;

    postImage.src = `/api/post_image/${currentPost.id}`;
    postViews.textContent = currentPost.post_views;
    postTimeAgo.textContent = timeAgo(currentPost.date_created);
    postFactText.textContent = currentPost.post_fact;
    postResearchText.innerHTML = marked.parse(currentPost.post_research || "");

    await loadOwner(currentPost.account_id);
    updatePrivacyLabel(currentPost.post_private);
};

const togglePrivacy = async () => {
    if (!privacyToggle) return;

    privacyToggle.disabled = true;

    try {
        const response = await fetch(`/api/toggle_private/${postId}`, {
            credentials: "include",
        });
        const result = await response.json();

        if (!response.ok || !result.status) {
            throw new Error(result.data?.error || "Could not update privacy");
        }

        updatePrivacyLabel(result.data.post_private);
        showToast(`post is now ${result.data.post_private ? "private" : "public"}`);
    } catch (error) {
        console.error(error);
        showToast(error.message || "Failed to toggle privacy");
    } finally {
        privacyToggle.disabled = false;
    }
};

document.addEventListener("DOMContentLoaded", async () => {
    await initAppNav({ contentSelector: "#main" });

    shareLinkBtn.addEventListener("click", copyShareLink);

    if (privacyToggle) {
        privacyToggle.addEventListener("click", togglePrivacy);
    }

    try {
        await loadPost();
    } catch (error) {
        console.error(error);
        showToast(error.message || "Failed to load post");
        postImage.style.display = "none";
    }
});
