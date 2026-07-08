let feeds = [];
let renderedCount = 0;
let isLoadingExplore = false;

const contentDOM = document.getElementById("content");
const exploreTrigger = document.getElementById("explore_trigger");
const metaDOM = document.getElementById("meta_data");

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

const populate_meta = async (index) => {
    try {
        const post = feeds[index];
        const account_id = post.account_id;

        const userRes = await fetch(`/api/get_user_username/${account_id}`);
        const userResult = await userRes.json();
        const username = userResult.status ? userResult.data.user.username : "unknown";
        const researchHTML = marked.parse(post.post_research || "");
        const metaHTML = `
            <div id="postInfo">
                <div id="postProfileView" onclick="move_to_user_page('${username}')">
                    <div id="postProfileImage">
                        <img src="/api/profile_image/${account_id}" alt="profile avatar">
                    </div>
                    <div id="postProfileUsername">
                        <p>${username}</p>
                    </div>
                </div>

                <div id="postDetails">
                    <div id="postInfoViews">
                        <img src="/static/assets/views.svg" alt="views">${post.post_views}
                    </div>
                    <div id="posttimeAgo">
                        <img src="/static/assets/ago.svg" alt="posted">${timeAgo(post.date_created)}
                    </div>
                </div>
            </div>

            <div id="postFact">
                <p>${post.post_fact}</p>
            </div>

            <div id="postResearch">
                <p>${researchHTML}</p>
            </div>
        `;

        metaDOM.innerHTML = metaHTML;
    } catch (error) {
        console.error("Failed to load post details:", error);
    }
};

window.populate_meta = populate_meta;

let visibleIndices = new Set();

const observer = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            const index = parseInt(entry.target.id, 10);

            if (entry.isIntersecting) {
                visibleIndices.add(index);
            } else {
                visibleIndices.delete(index);
            }
        });

        if (visibleIndices.size > 0) {
            const activeIndex = Math.min(...visibleIndices);
            populate_meta(activeIndex);
        }
    },
    { threshold: 0.6 }
);

const populate_feeds = () => {
    for (let index = renderedCount; index < feeds.length; index++) {
        const post = feeds[index];
        const postEl = document.createElement("div");
        postEl.className = "contentBox";
        postEl.id = index;
        postEl.innerHTML = `
            <img src="/api/post_image/${post.id}" alt="post image">
        `;
        postEl.addEventListener("click", () => move_to_post_page(post.id));

        contentDOM.appendChild(postEl);
        observer.observe(postEl);
    }

    renderedCount = feeds.length;
};

const exploreObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                get_explore();
            }
        });
    },
    { threshold: 0.1 }
);

const get_explore = async () => {
    if (isLoadingExplore) {
        return { success: false, error: "already loading" };
    }
    isLoadingExplore = true;

    try {
        const start = feeds.length + 1;
        const end = feeds.length + 10;

        const response = await fetch("/api/get_explore_posts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ start, end }),
        });

        const result = await response.json();

        if (!response.ok || !result.status) {
            console.error("Explore fetch failed:", result.data?.error || "Unknown error");
            return { success: false, error: result.data?.error || "Something went wrong" };
        }

        const newPosts = result.data.posts || [];

        if (newPosts.length === 0) {
            let noMoreEl = document.getElementById("no_new_post");
            if (!noMoreEl) {
                noMoreEl = document.createElement("div");
                noMoreEl.id = "no_new_post";
                noMoreEl.textContent = "no new posts";
                contentDOM.appendChild(noMoreEl);
            }
            return { success: true, data: [] };
        }

        feeds = feeds.concat(newPosts);
        populate_feeds();

        return { success: true, data: newPosts };
    } catch (error) {
        console.error("Network or unexpected error:", error);
        return { success: false, error: "Could not reach the server" };
    } finally {
        isLoadingExplore = false;
    }
};

document.addEventListener("DOMContentLoaded", async () => {
    await initAppNav({ contentSelector: "#main" });
    exploreObserver.observe(exploreTrigger);

    const result = await get_explore();
    if (!result.success) {
        console.error(result.error);
    }
});
