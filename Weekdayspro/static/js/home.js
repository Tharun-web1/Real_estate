let currentGroupIndex = 0;
let currentStoryIndex = 0;
let activeStoryList = [];
let storyTimer = null;
const IMAGE_DURATION = 10000; // 10 seconds for images

function initStories(stories, userStories, currentUserId) {
    window.storiesData = stories;
    window.userStories = userStories;
    window.currentUserId = currentUserId;
    activeStoryList = stories;
}

function openStoryViewer(groupIndex) {
    activeStoryList = window.storiesData;
    currentGroupIndex = groupIndex;
    currentStoryIndex = 0;
    const viewer = document.getElementById('story-viewer');
    if (viewer) viewer.style.display = 'flex';
    showStory();
}

function openYourStory() {
    if (!window.userStories) return;
    activeStoryList = [window.userStories];
    currentGroupIndex = 0;
    currentStoryIndex = 0;
    const viewer = document.getElementById('story-viewer');
    if (viewer) viewer.style.display = 'flex';
    showStory();
}

function closeStoryViewer() {
    const viewer = document.getElementById('story-viewer');
    if (viewer) viewer.style.display = 'none';
    const video = document.getElementById('story-video');
    if (video) video.pause();
    clearTimeout(storyTimer);
}

function showStory() {
    const group = activeStoryList[currentGroupIndex];
    const story = group.posts[currentStoryIndex];
    const user = group.user;

    // Update UI
    const nameEl = document.getElementById('story-user-name');
    const imgEl = document.getElementById('story-user-img');
    const timeEl = document.getElementById('story-time');
    const textEl = document.getElementById('story-text');

    if (nameEl) nameEl.innerText = user.company_name || user.username;
    if (imgEl) imgEl.src = user.company_logo_path || user.profile_image_path || '/static/default.jpg';
    if (timeEl) timeEl.innerText = story.created_at;
    if (textEl) textEl.innerText = story.content;

    clearTimeout(storyTimer);
    const mediaImg = document.getElementById('story-img');
    const mediaVideo = document.getElementById('story-video');

    if (story.media_type === 'video') {
        if (mediaImg) mediaImg.style.display = 'none';
        if (mediaVideo) {
            mediaVideo.style.display = 'block';
            mediaVideo.src = story.video_url;
            mediaVideo.onended = () => nextStory();
            mediaVideo.play().catch(e => console.error("Story video play failed:", e));
            mediaVideo.onloadedmetadata = () => {
                updateProgressBars(mediaVideo.duration * 1000);
            };
        }
    } else {
        if (mediaImg) {
            mediaImg.style.display = 'block';
            mediaImg.src = story.image_url;
            mediaImg.onerror = function() { this.src = '/static/default.jpg'; };
        }
        if (mediaVideo) mediaVideo.style.display = 'none';
        updateProgressBars(IMAGE_DURATION);
        storyTimer = setTimeout(nextStory, IMAGE_DURATION);
    }

    // Mark as seen
    if (window.currentUserId && story.id) {
        fetch(`/story/mark-seen/${story.id}/`, { method: 'POST' });
    }

    // Owner Menu
    const ownerMenu = document.getElementById('story-owner-menu');
    const editLink = document.getElementById('story-edit-link');
    if (ownerMenu && window.currentUserId && story.user_id === window.currentUserId) {
        ownerMenu.style.display = 'block';
        if (editLink) editLink.href = `/news/edit/${story.id}/`;
    } else if (ownerMenu) {
        ownerMenu.style.display = 'none';
    }
    const dropdown = document.getElementById('story-menu-dropdown');
    if (dropdown) dropdown.classList.remove('active');
}

function toggleStoryMenu(event) {
    event.stopPropagation();
    const dropdown = document.getElementById('story-menu-dropdown');
    if (dropdown) dropdown.classList.toggle('active');
}

function deleteCurrentStory(event, csrfToken) {
    event.stopPropagation();
    if (!confirm("Delete this story?")) return;
    const story = activeStoryList[currentGroupIndex].posts[currentStoryIndex];
    fetch(`/news/delete/${story.id}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken }
    }).then(res => { if(res.ok) location.reload(); });
}

function updateProgressBars(duration) {
    const group = activeStoryList[currentGroupIndex];
    const progressContainer = document.getElementById('story-progress-container');
    if (!progressContainer) return;
    progressContainer.innerHTML = '';
    group.posts.forEach((_, idx) => {
        const bar = document.createElement('div');
        bar.className = 'progress-bar';
        const fill = document.createElement('div');
        fill.className = 'progress-fill';
        if (idx < currentStoryIndex) fill.style.width = '100%';
        if (idx === currentStoryIndex) {
            setTimeout(() => fill.style.width = '100%', 50);
            fill.style.transitionDuration = duration + 'ms';
        }
        bar.appendChild(fill);
        progressContainer.appendChild(bar);
    });
}

function nextStory(event) {
    if (event) {
        const clickX = event.clientX || (event.touches && event.touches[0].clientX);
        const screenWidth = window.innerWidth;
        if (clickX < screenWidth / 3) {
            prevStory();
            return;
        }
    }

    currentStoryIndex++;
    if (currentStoryIndex >= activeStoryList[currentGroupIndex].posts.length) {
        currentStoryIndex = 0;
        currentGroupIndex++;
        if (currentGroupIndex >= activeStoryList.length) {
            closeStoryViewer();
            return;
        }
    }
    showStory();
}

function prevStory() {
    currentStoryIndex--;
    if (currentStoryIndex < 0) {
        currentGroupIndex--;
        if (currentGroupIndex < 0) {
            currentGroupIndex = 0;
            currentStoryIndex = 0;
        } else {
            currentStoryIndex = activeStoryList[currentGroupIndex].posts.length - 1;
        }
    }
    showStory();
}

document.addEventListener('DOMContentLoaded', function() {
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeStoryViewer();
    });

    // Auto-play reels when in view
    const reels = document.querySelectorAll('.autoplay-reel');
    const observerOptions = { threshold: 0.7 };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.play().catch(e => console.error("Reel autoplay failed:", e));
            } else {
                entry.target.pause();
            }
        });
    }, observerOptions);
    reels.forEach(reel => observer.observe(reel));
});

function scrollTrack(trackId, direction) {
    const track = document.getElementById(trackId);
    if (!track) return;
    const scrollAmount = track.offsetWidth * 0.8; 
    track.scrollBy({
        left: direction * scrollAmount,
        behavior: 'smooth'
    });
}

function scrollExperts(direction) { scrollTrack('experts-track', direction); }
function scrollPro(direction) { scrollTrack('pro-track', direction); }
function scrollRecent(direction) { scrollTrack('recent-track', direction); }
function scrollBuilders(direction) { scrollTrack('builders-track', direction); }
function scrollFeed(direction) { scrollTrack('feed-track', direction); }
function scrollReels(direction) { scrollTrack('reels-track', direction); }

function toggleProjectSave(event, id, btn) {
    event.stopPropagation();
    fetch(`/save-project/${id}/`)
        .then(res => res.json())
        .then(data => {
            let icon = btn.querySelector("i");
            if (data.status === "saved") {
                icon.classList.remove("bi-bookmark");
                icon.classList.add("bi-bookmark-fill");
            } else {
                icon.classList.remove("bi-bookmark-fill");
                icon.classList.add("bi-bookmark");
            }
        });
}

function redirectToLogin() {
    // Note: This function relies on window.loginUrl which should be set in the HTML
    window.location.href = window.loginUrl || '/login/';
}

function shareProject(title, address, price, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: `${title} at ${address} for ₹${price}`,
            url: window.location.origin + url
        });
    } else {
        navigator.clipboard.writeText(window.location.origin + url);
        alert("Link copied to clipboard!");
    }
}

function shareProfile(userId) {
    const url = window.location.origin + `/user/${userId}/`;
    if (navigator.share) {
        navigator.share({
            title: 'Check out this profile',
            url: url
        });
    } else {
        navigator.clipboard.writeText(url);
        alert("Profile link copied to clipboard!");
    }
}

