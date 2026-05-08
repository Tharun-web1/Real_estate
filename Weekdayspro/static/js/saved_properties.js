/* saved_properties.js */

function showTab(tabName) {
    // Sections
    const propSection = document.getElementById('properties-section');
    const projSection = document.getElementById('projects-section');
    
    // Buttons
    const btns = document.querySelectorAll('.tab-btn');
    
    if (tabName === 'properties') {
        propSection.style.display = 'block';
        projSection.style.display = 'none';
        btns[0].classList.add('active');
        btns[1].classList.remove('active');
    } else {
        propSection.style.display = 'none';
        projSection.style.display = 'block';
        btns[1].classList.add('active');
        btns[0].classList.remove('active');
    }
}

function removeSave(propertyId, btn) {
    if (!confirm('Are you sure you want to remove this property from saved?')) return;
    
    fetch(`/save/${propertyId}/`)
        .then(res => res.json())
        .then(data => {
            if (data.status === 'removed') {
                // Find the card and remove it
                const card = btn.closest('.card-container');
                card.style.opacity = '0';
                setTimeout(() => {
                    card.remove();
                    // Check if empty
                    const list = document.querySelector('#properties-section .right-list');
                    if (list.children.length === 0) {
                        list.innerHTML = '<p class="empty-msg">No saved properties</p>';
                    }
                }, 300);
            }
        })
        .catch(err => console.error('Error removing property:', err));
}

function removeProjectSave(projectId, btn) {
    if (!confirm('Are you sure you want to remove this project from saved?')) return;
    
    fetch(`/save-project/${projectId}/`)
        .then(res => res.json())
        .then(data => {
            if (data.status === 'removed') {
                const card = btn.closest('.card-container');
                card.style.opacity = '0';
                setTimeout(() => {
                    card.remove();
                    const list = document.querySelector('#projects-section .right-list');
                    if (list.children.length === 0) {
                        list.innerHTML = '<p class="empty-msg">No saved projects</p>';
                    }
                }, 300);
            }
        })
        .catch(err => console.error('Error removing project:', err));
}

// Pull to refresh
// Global pull-to-refresh variables are handled in NavBar.html. 
// We just use them here without redeclaring to avoid SyntaxErrors.
if (typeof startY === 'undefined') {
    window.startY = 0;
    window.isRefreshing = false;
}

document.addEventListener("touchstart", (e) => {
    startY = e.touches[0].clientY;
});

document.addEventListener("touchmove", (e) => {
    const currentY = e.touches[0].clientY;
    if (currentY - startY > 100 && !isRefreshing && window.scrollY === 0) {
        isRefreshing = true;
        const msg = document.getElementById("refreshMessage");
        if (msg) msg.style.display = "block";
        setTimeout(() => {
            location.reload();
        }, 300);
    }
});