document.addEventListener('DOMContentLoaded', () => {
    let reelToDelete = null;

    function showToast(message, success = true) {
        const toast = document.getElementById('toast');
        if (!toast) return;
        toast.innerText = message;
        toast.style.background = success ? '#1f8ef1' : '#ff6b6b';
        toast.style.display = 'block';
        setTimeout(() => toast.style.display = 'none', 2000);
    }

    const closeBtn = document.getElementById("closeBtn");
    if (closeBtn) {
        closeBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            closeReel();
        });
    }

    const reelModalContent = document.querySelector("#reelModal > div");
    if (reelModalContent) {
        reelModalContent.addEventListener("click", function (e) {
            e.stopPropagation();
        });
    }

    window.toggleDropdown = function (id) {
        const dropdown = document.getElementById('dropdown-' + id);
        document.querySelectorAll('.dropdown-content').forEach(d => {
            if (d.id !== 'dropdown-' + id) d.style.display = 'none';
        });
        if (dropdown) {
            dropdown.style.display = dropdown.style.display === 'flex' ? 'none' : 'flex';
        }
    }

    /* ✅ NEW POPUP OPEN (REPLACES OLD MODAL) */
    window.openReel = function (url, likes, comments, views) {
        const video = document.getElementById("popupVideo");
        if (!url || !video) return;

        // ✅ FULL RESET (fixes 2nd click issue)
        video.pause();
        video.removeAttribute("src");   // 🔥 better than innerHTML
        video.load();

        // ✅ SET NEW VIDEO
        video.src = url;
        video.currentTime = 0;
        video.muted = true;
        video.autoplay = true;
        video.playsInline = true;
        video.load();

        // ✅ PLAY
        video.play().catch(err => console.log("Play error:", err));

        // ✅ STATS
        const viewCount = document.getElementById("viewCount");
        const likeCount = document.getElementById("likeCount");
        const commentCount = document.getElementById("commentCount");

        if (viewCount) viewCount.innerHTML = '<i class="bi bi-eye"></i> ' + (views || 0);
        if (likeCount) likeCount.innerHTML = '<i class="bi bi-heart"></i> ' + (likes || 0);
        if (commentCount) commentCount.innerHTML = '<i class="bi bi-chat"></i> ' + (comments || 0);

        // ✅ SHOW MODAL
        const reelModal = document.getElementById("reelModal");
        if (reelModal) reelModal.style.display = "flex";
    }

    /* ✅ CLOSE POPUP */
    window.closeReel = function () {
        const video = document.getElementById("popupVideo");
        if (video) {
            video.pause();
            video.removeAttribute("src");
            video.load();
        }
        const reelModal = document.getElementById("reelModal");
        if (reelModal) reelModal.style.display = "none";
    }

    const popupVideo = document.getElementById("popupVideo");
    if (popupVideo) {
        popupVideo.addEventListener("click", function (e) {
            e.stopPropagation();
        });
    }

    /* ✅ CLICK OUTSIDE CLOSE */
    const reelModal = document.getElementById("reelModal");
    if (reelModal) {
        reelModal.addEventListener("click", function (e) {
            if (e.target === this) {
                closeReel();
            }
        });
    }

    // ✅ EDIT
    window.openEditPopup = function (id, videoUrl, description, link) {
        document.querySelectorAll('.dropdown-content').forEach(d => d.style.display = 'none');

        const modal = document.getElementById('editModal');
        const video = document.getElementById('editVideo');
        const descInput = document.getElementById('editDesc');
        const linkInput = document.getElementById('editLink');
        const form = document.getElementById('editForm');

        if (video) video.src = videoUrl;
        if (descInput) descInput.value = description && description !== "None" ? description : "";
        if (linkInput) linkInput.value = link && link !== "None" ? link : "";

        if (form) {
            // Note: The URL template logic needs to be handled carefully in external JS
            // We expect a data attribute or a global variable if {% url %} is needed.
            // For now, we'll use a placeholder logic that assumes the URL structure.
            // However, it's safer to pass the actual URL from the HTML.
            // We'll update the HTML to pass the specific edit URL.
        }

        if (modal) modal.classList.add('active');
    }
    
    // Helper to set form action if passed from HTML
    window.setEditFormAction = function(url) {
        const form = document.getElementById('editForm');
        if (form) form.action = url;
    }

    window.closeEditPopup = function () {
        const modal = document.getElementById('editModal');
        if (modal) modal.classList.remove('active');
    }

    // ✅ DELETE
    window.openDeletePopup = function (id) {
        reelToDelete = id;
        const modal = document.getElementById('deleteModal');
        if (modal) modal.classList.add('active');
    }

    window.closeDeletePopup = function () {
        const modal = document.getElementById('deleteModal');
        if (modal) modal.classList.remove('active');
        reelToDelete = null;
    }

    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function () {
            if (!reelToDelete) return;

            // CSRF Token handling
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            // Again, we need the URL from the HTML or a consistent pattern.
            // We'll update the HTML to pass the delete URL when opening the popup.
            const deleteUrlBase = document.body.dataset.deleteUrlBase;
            if (!deleteUrlBase) {
                console.error("Delete URL base not found");
                return;
            }

            fetch(deleteUrlBase.replace('0', reelToDelete), {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        showToast('Reel deleted successfully!', true);
                        const card = document.getElementById('reel-card-' + reelToDelete);
                        if (card) card.remove();
                    } else {
                        showToast('Failed to delete reel.', false);
                    }
                    closeDeletePopup();
                })
                .catch(err => {
                    showToast('Error deleting reel.', false);
                    closeDeletePopup();
                    console.error(err);
                });
        });
    }

    // ✅ EDIT SUBMIT
    const editForm = document.getElementById('editForm');
    if (editForm) {
        editForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const form = e.target;
            const data = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: data,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        showToast('Reel updated successfully!', true);
                        closeEditPopup();
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showToast('Failed to update reel.', false);
                        console.log(data.errors);
                    }
                })
                .catch(err => {
                    showToast('Error updating reel.', false);
                    console.error(err);
                });
        });
    }

    /* ✅ CLICK REEL → OPEN NEW POPUP */
    document.querySelectorAll('.reel-video').forEach(videoElem => {
        videoElem.addEventListener('click', function () {
            const url = this.dataset.url;
            const likes = parseInt(this.dataset.likes) || 0;
            const comments = parseInt(this.dataset.comments) || 0;
            const views = parseInt(this.dataset.views) || 0;

            openReel(url, likes, comments, views);
        });
    });
});
