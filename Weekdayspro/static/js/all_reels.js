console.log("Pro Bytes Gallery Script Loaded");

let reelToDelete = null;

// Global Toast Function
window.showToast = function(message, success = true) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.innerText = message;
    toast.style.background = success ? '#1e293b' : '#ef4444';
    toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 3000);
}

// Global Toggle Dropdown
window.toggleDropdown = function (event, id) {
    console.log("Toggling dropdown for:", id);
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    const dropdown = document.getElementById('dropdown-' + id);
    
    // Close other dropdowns
    document.querySelectorAll('.dropdown-content').forEach(d => {
        if (d.id !== 'dropdown-' + id) d.style.display = 'none';
    });

    if (dropdown) {
        const isVisible = dropdown.style.display === 'flex';
        dropdown.style.display = isVisible ? 'none' : 'flex';
        console.log("Dropdown state:", dropdown.style.display);
    }
}

/* ✅ OPEN REEL POPUP */
window.openReel = function (url, likes, comments, views) {
    console.log("Opening reel:", url);
    const video = document.getElementById("popupVideo");
    const modal = document.getElementById("reelModal");
    if (!url || !video || !modal) {
        console.error("Missing elements for reel popup");
        return;
    }

    // Reset video
    video.pause();
    video.src = url;
    video.load();

    // Update Stats
    document.getElementById("viewCount").innerText = views || 0;
    document.getElementById("likeCount").innerText = likes || 0;
    document.getElementById("commentCount").innerText = comments || 0;

    // Show Modal
    modal.style.display = "flex";
    video.play().catch(err => console.log("Auto-play blocked:", err));
}

/* ✅ CLOSE REEL POPUP */
window.closeReel = function () {
    const video = document.getElementById("popupVideo");
    const modal = document.getElementById("reelModal");
    if (video) {
        video.pause();
        video.src = "";
    }
    if (modal) modal.style.display = "none";
}

/* ✅ EDIT REEL */
window.openEditPopup = function (id, videoUrl, description, link) {
    console.log("Opening edit popup for:", id);
    // Close dropdown first
    document.querySelectorAll('.dropdown-content').forEach(d => d.style.display = 'none');

    const modal = document.getElementById('editModal');
    const video = document.getElementById('editVideo');
    const descInput = document.getElementById('editDesc');
    const linkInput = document.getElementById('editLink');
    
    if (video) video.src = videoUrl;
    if (descInput) descInput.value = (description && description !== "None") ? description : "";
    if (linkInput) linkInput.value = (link && link !== "None") ? link : "";

    if (modal) modal.classList.add('active');
}

window.setEditFormAction = function(url) {
    const form = document.getElementById('editForm');
    if (form) form.action = url;
}

window.closeEditPopup = function () {
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.classList.remove('active');
        const video = document.getElementById('editVideo');
        if (video) video.pause();
    }
}

/* ✅ DELETE REEL */
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

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded: Initializing event listeners");
    
    const closeBtn = document.getElementById("closeBtn");
    if (closeBtn) {
        closeBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            closeReel();
        });
    }

    // Close dropdowns on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.more-menu')) {
            document.querySelectorAll('.dropdown-content').forEach(d => d.style.display = 'none');
        }
    });

    // Close modal on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeReel();
            closeEditPopup();
            closeDeletePopup();
        }
    });

    // Close modal on backdrop click
    const reelModal = document.getElementById("reelModal");
    if (reelModal) {
        reelModal.addEventListener("click", function (e) {
            if (e.target === this) closeReel();
        });
    }

    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function () {
            if (!reelToDelete) return;

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            const deleteUrlBase = document.body.dataset.deleteUrlBase;

            if (!deleteUrlBase) return;

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
                    showToast('Reel deleted successfully!');
                    const card = document.getElementById('reel-card-' + reelToDelete);
                    if (card) {
                        card.style.opacity = '0';
                        card.style.transform = 'scale(0.8)';
                        setTimeout(() => card.remove(), 400);
                    }
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

    // Edit form submission
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
                    showToast('Changes saved successfully!');
                    closeEditPopup();
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('Failed to save changes.', false);
                }
            })
            .catch(err => {
                showToast('Error saving changes.', false);
                console.error(err);
            });
        });
    }

    // Use event delegation for reel cards to be more robust
    const container = document.querySelector('.reels-container');
    if (container) {
        container.addEventListener('click', (e) => {
            const card = e.target.closest('.reel-card');
            if (!card) return;
            
            // If they clicked the menu or its children, ignore
            if (e.target.closest('.more-menu')) return;
            
            console.log("Card clicked, opening reel popup...");
            const videoElem = card.querySelector('.reel-video');
            if (videoElem) {
                const url = videoElem.dataset.url;
                const likes = videoElem.dataset.likes;
                const comments = videoElem.dataset.comments;
                const views = videoElem.dataset.views;
                openReel(url, likes, comments, views);
            }
        });
    } else {
        console.warn("Reels container not found");
    }
});
