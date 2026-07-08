// app/static/nav.js

let user_account_id = null;
let user_username = null;
let post_result = false;

let navDOM = null;
let searchResultsModal = null;
let mainDOM = null;
let postResultToggle = null;
let searchInput = null;
let lastScrollY = window.scrollY;
let searchDebounceTimer = null;

const move_to_user_page = (username) => {
    window.location.href = `/${username}`;
};

const move_to_post_page = (postId) => {
    window.location.href = `/${postId}`;
};

window.togglePostResult = () => {
    if (!post_result) {
        post_result = true;
        postResultToggle.innerText = "posts";
    } else {
        post_result = false;
        postResultToggle.innerText = "users";
    }

    if (searchInput.value !== "") {
        runSearch(searchInput.value);
    }
};

const showNavToast = (message) => {
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

const get_userInfo = async () => {
    try {
        const response = await fetch("/api/get_user_all_info", {
            method: "GET",
            credentials: "include",
        });

        const result = await response.json();

        if (!response.ok || !result.status) {
            return { success: false, error: result.data?.error || "Something went wrong" };
        }

        return { success: true, data: result.data.user };
    } catch (error) {
        console.error("Network or unexpected error:", error);
        return { success: false, error: "Could not reach the server" };
    }
};

const profileViewTrigger = (username, account_id) => {
    if (document.getElementById("profileView")) return;

    const container = document.createElement("div");
    user_account_id = account_id;
    user_username = username;
    container.id = "profileView";
    container.title = username;
    container.onclick = () => move_to_user_page(username);
    container.innerHTML = `
        <div id="username">
            <span id="usernameTxt">${username}</span>
        </div>
        <div id="profileAvatar">
            <img src="/api/profile_image/${account_id}" alt="profile avatar">
        </div>
    `;

    navDOM.appendChild(container);
};

const populateSearchModalWithPost = (posts) => {
    posts.forEach((post) => {
        const postEl = document.createElement("div");
        postEl.className = "searchResultPost";
        postEl.innerHTML = `
            <div class="searchPostImg">
                <img src="/api/post_image/${post.id}" alt="post image">
            </div>
            <div class="searchPostTitle">
                <p>${post.post_fact}</p>
            </div>
        `;
        postEl.addEventListener("click", () => move_to_post_page(post.id));
        searchResultsModal.appendChild(postEl);
    });

    if (!searchResultsModal.innerHTML) {
        searchResultsModal.innerHTML = '<div class="no_post">no posts</div>';
    }
};

const populateSearchModalWithUsers = (users) => {
    users.forEach((user) => {
        const userEl = document.createElement("div");
        userEl.className = "searchResultUser";
        userEl.innerHTML = `
            <div class="searchUserImg">
                <img src="/api/profile_image/${user.account_id}" alt="profile avatar">
            </div>
            <div class="searchUserTitle">
                <p>${user.username}</p>
            </div>
        `;
        userEl.addEventListener("click", () => move_to_user_page(user.username));
        searchResultsModal.appendChild(userEl);
    });

    if (!searchResultsModal.innerHTML) {
        searchResultsModal.innerHTML = '<div class="no_post">no users</div>';
    }
};

const renderSearchResults = ({ users, posts }) => {
    searchResultsModal.innerHTML = "";

    if (post_result) {
        populateSearchModalWithPost(posts);
    } else {
        populateSearchModalWithUsers(users);
    }
};

const runSearch = async (keyword) => {
    try {
        const [profilesRes, postsRes] = await Promise.all([
            fetch("/api/search/profiles", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ keyword, start: 1, end: 10 }),
            }),
            fetch("/api/search/posts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ keyword, start: 1, end: 10 }),
            }),
        ]);

        const profilesResult = await profilesRes.json();
        const postsResult = await postsRes.json();

        if (!profilesRes.ok || !postsRes.ok) {
            showNavToast("sign in to search");
            return;
        }

        const users = profilesResult.status ? profilesResult.data.users : [];
        const posts = postsResult.status ? postsResult.data.posts : [];

        renderSearchResults({ users, posts });
        postResultToggle.classList.remove("hidden");
        searchResultsModal.classList.remove("hidden");
    } catch (error) {
        console.error("Search failed:", error);
    }
};

const handleSearchInput = (event) => {
    const keyword = event.target.value.trim();

    clearTimeout(searchDebounceTimer);
    if (mainDOM) {
        mainDOM.classList.add("disable");
    }
    document.body.classList.add("modal-open");

    if (!keyword) {
        renderSearchResults({ users: [], posts: [] });
        postResultToggle.classList.add("hidden");
        searchResultsModal.classList.add("hidden");

        if (mainDOM) {
            mainDOM.classList.remove("disable");
        }
        document.body.classList.remove("modal-open");
        return;
    }

    searchDebounceTimer = setTimeout(async () => {
        await runSearch(keyword);
    }, 300);
};

const initNavScroll = () => {
    const nav = document.getElementById("nav");
    if (!nav) return;

    window.addEventListener("scroll", () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > lastScrollY && currentScrollY > 50) {
            nav.classList.add("nav-hidden");
        } else {
            nav.classList.remove("nav-hidden");
        }

        lastScrollY = currentScrollY;
    });
};

window.initAppNav = async ({ contentSelector = "#main" } = {}) => {
    navDOM = document.getElementById("nav");
    searchResultsModal = document.getElementById("searchResultModal");
    postResultToggle = document.getElementById("postsToggle");
    searchInput = document.getElementById("search-input");
    mainDOM = document.querySelector(contentSelector);

    if (!navDOM || !searchInput) return;

    initNavScroll();
    searchInput.addEventListener("input", handleSearchInput);

    document.addEventListener("click", (event) => {
        if (
            mainDOM &&
            mainDOM.contains(event.target) &&
            !searchInput.contains(event.target) &&
            !searchResultsModal.contains(event.target)
        ) {
            mainDOM.classList.remove("disable");
            searchResultsModal.classList.add("hidden");
            postResultToggle.classList.add("hidden");
            document.body.classList.remove("modal-open");
        }
    });

    const result = await get_userInfo();
    if (result.success) {
        profileViewTrigger(result.data.username, result.data.account_id);
    }
};

window.move_to_user_page = move_to_user_page;
window.move_to_post_page = move_to_post_page;
window.showNavToast = showNavToast;
