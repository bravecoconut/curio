let library_dom = document.getElementById("library");
let post_dom = document.getElementById("post");
let error_alert_dom = document.getElementById("error_alert");
let stage_1_dom = document.getElementById("stage_1"),
    stage_2_dom = document.getElementById("stage_2"),
    stage_3_dom = document.getElementById("stage_3"),
    stage_4_dom = document.getElementById("stage_4"),
    stage_5_dom = document.getElementById("stage_5"),
    stage_6_dom = document.getElementById("stage_6"),
    stage_7_dom = document.getElementById("stage_7");
    

function alert_by_error(error) {
    document.body.insertAdjacentHTML("beforeend", `
        <div id="error_alert">
            <p>${error}</p>
        </div>
    `);

    const error_alert_dom = document.getElementById("error_alert");

    setTimeout(() => {
        error_alert_dom.classList.add("fade_out");

        error_alert_dom.addEventListener("animationend", () => {
            error_alert_dom.remove();
        });
    }, 5000);
}

function set_library_data(block) {
    library_dom.style.pointerEvents = block ? 'none' : 'auto';
    library_dom.style.filter = block ? 'blur(5px)' : 'none';
}

function start_show_working() {
    let working = `
            <div id="working">
                <div id="status">
                    <div id="stage_1" class="status_indicator">Fetching latest data</div>
                    <div id="stage_2" class="status_indicator">Selecting optimal topic</div>
                    <div id="stage_3" class="status_indicator">Running deep research</div>
                    <div id="stage_4" class="status_indicator">Analyzing research data</div>
                    <div id="stage_5" class="status_indicator">Preparing image generation</div>
                    <div id="stage_6" class="status_indicator">Generating image</div>
                    <div id="stage_7" class="status_indicator">Finalizing post</div>
                </div>
            </div>
    `
    post_dom.innerHTML = working


    stage_1_dom = document.getElementById("stage_1");
    stage_2_dom = document.getElementById("stage_2");
    stage_3_dom = document.getElementById("stage_3");
    stage_4_dom = document.getElementById("stage_4");
    stage_5_dom = document.getElementById("stage_5");
    stage_6_dom = document.getElementById("stage_6");
    stage_7_dom = document.getElementById("stage_7");


}


function unblock_library_data() {
    if (block_library) {
        library_dom.style.pointerEvents = 'none';
        library_dom.style.opacity = 0.4;
        library_dom.style.filter = 'blur(2px)';
    }
}

function load_post_into_main(post) {
    console.log(post);
    post_image = post.image_path;
    post_topic = post.topic;
    post_description = post.description

    post_to_add = `
            <div id="post_image">
                <img src="/results_images/${post_image}.png" title="${post_topic}">
            </div>

            <div id="details">

                <div id="post_topic">
                    <p>${post_topic}</p>
                </div>

                <div id="post_description">
                    <p>${post_description}</p>
                </div>
            </div>
    `

    post_dom.innerHTML = post_to_add
}


function populate_library(posts) {
    library_dom.innerHTML = ''
    posts.forEach((post, index) => {
        post_topic = post.topic;
        post_poster = post.poster;

        library_dom.insertAdjacentHTML("afterbegin", `
            <div class="post_from_library" id="${index}" title="${post_topic}" onclick=startMan.get_post_index_to_load()>
                <img src="/poster_images/${post_poster}.png">
            </div>
        `);

    });
}

class StartMan {
    constructor() {
        this.posts = []
    }


    async start() {
        const res = await fetch("http://localhost:5000/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });


        const reader = res.body.getReader();
        const decoder = new TextDecoder();

        let buffer = "";

        start_show_working();

        set_library_data(true);

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split("\n\n");
            buffer = parts.pop();


            for (const part of parts) {
                const line = part.trim();

                if (!line.startsWith("data: ")) continue;

                try {
                    const payload = JSON.parse(line.slice(6));

                    console.log(payload);
                    

                    if (payload.starting_status) {
                        if (payload.starting_status.stage_1) {
                            console.log("stage 1");
                            stage_1_dom.classList.add('status_indicator_active');

                        }

                        if (payload.starting_status.stage_2) {
                            console.log("stage 2");
                            stage_1_dom.classList.add('status_indicator_finish');
                            stage_1_dom.classList.remove('status_indicator_active');

                            stage_2_dom.classList.add('status_indicator_active');

                        }

                        if (payload.starting_status.stage_3) {
                            console.log("stage 3");
                            stage_2_dom.classList.add('status_indicator_finish');
                            stage_2_dom.classList.remove('status_indicator_active');

                            stage_3_dom.classList.add('status_indicator_active');

                        }

                        if (payload.starting_status.stage_4) {
                            console.log("stage 4");
                            stage_3_dom.classList.add('status_indicator_finish');
                            stage_3_dom.classList.remove('status_indicator_active');

                            stage_4_dom.classList.add('status_indicator_active');
                        }

                        if (payload.starting_status.stage_5) {
                            console.log("stage 5");
                            stage_4_dom.classList.add('status_indicator_finish');
                            stage_4_dom.classList.remove('status_indicator_active');

                            stage_5_dom.classList.add('status_indicator_active');
                        }

                        if (payload.starting_status.stage_6) {
                            console.log("stage 6");
                            stage_5_dom.classList.add('status_indicator_finish');
                            stage_5_dom.classList.remove('status_indicator_active');

                            stage_6_dom.classList.add('status_indicator_active');
                        }

                        if (payload.starting_status.stage_7) {
                            console.log("stage 7");
                            stage_6_dom.classList.add('status_indicator_finish');
                            stage_6_dom.classList.remove('status_indicator_active');

                            stage_7_dom.classList.add('status_indicator_active');
                        }

                    }

                    if (payload.error_status) {
                        console.log(payload.error_status);
                        alert_by_error(payload.error_status)
                        break
                        
                    }

                    if (payload.new_post) {
                        let new_result_post = payload.new_post
                        console.log(new_result_post);

                        this.get_all_post()
                        set_library_data(false)
                        load_post_into_main(new_result_post)

                    }
                } catch (e) {
                    console.warn("Failed to parse SSE payload:", line, e);
                }

            }

        }
    }

    async get_all_post() {
        const res = await fetch("http://127.0.0.1:5000/get_all_posts", {
            method: "POST",
        });

        this.posts = await res.json();
        console.log(this.posts);
        populate_library(this.posts)
    }

    get_post_index_to_load() {
        const index = event.target.closest(".post_from_library").id;
        const post = this.posts[index];
        load_post_into_main(post);
    }
}

const startMan = new StartMan();

startMan.get_all_post()

