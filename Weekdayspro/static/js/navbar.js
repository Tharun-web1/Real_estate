function openSearch() {
    document.getElementById('searchOverlay').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeSearch() {
    document.getElementById('searchOverlay').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function switchSearchTab(tabIndex, el) {
    document.querySelectorAll('.search-tab').forEach(tab => tab.classList.remove('active'));
    el.classList.add('active');

    document.getElementById('searchForm1').style.display = 'none';
    document.getElementById('searchForm2').style.display = 'none';
    document.getElementById('searchForm3').style.display = 'none';

    if (tabIndex === 1 || tabIndex === 2) {
        const form1 = document.getElementById('searchForm1');
        form1.style.display = 'block';
        const form = form1.querySelector('form');
        if (tabIndex === 1) {
            form.querySelector('button[type="submit"]').innerHTML = '<i class="bi bi-search"></i> Search Properties';
            form.onsubmit = function(e) {
                e.preventDefault();
                const propType = form.querySelector('[name="type_of_project"]').value || 'All';
                const params = new URLSearchParams();
                const fields = ['location', 'city', 'facing', 'name', 'minpricing', 'maxpricing', 'look', 'position', 'approval', 'extent'];
                fields.forEach(f => {
                    const el = form.querySelector('[name="' + f + '"]');
                    if (el && el.value) params.append(f, el.value);
                });
                const qs = params.toString();
                window.location.href = '/properties/' + encodeURIComponent(propType) + '/' + (qs ? '?' + qs : '');
            };
        } else {
            form.onsubmit = null;
            // Note: form.action is handled in switchSearchTab in original, but here we can set it via JS if needed
            // However, the original used {% url %} which we can't easily do in static JS unless we pass it.
            // I'll keep the logic that depends on Django variables in a small inline script or use data attributes.
            form.querySelector('button[type="submit"]').innerHTML = '<i class="bi bi-search"></i> Search Projects';
        }
    } else if (tabIndex === 3) {
        document.getElementById('searchForm2').style.display = 'block';
    } else if (tabIndex === 4 || tabIndex === 5) {
        document.getElementById('searchForm3').style.display = 'block';
        const catInput = document.getElementById('profCategory');
        const nameLabel = document.getElementById('profNameLabel');

        if (tabIndex === 4) {
            catInput.value = 'marketer';
            nameLabel.innerText = 'Agent Name';
        } else {
            catInput.value = 'professional';
            nameLabel.innerText = 'Professional Name';
        }
    }
}

function closeStatusModal() {
    const modal = document.getElementById("statusModal");
    if (!modal) return;
    modal.classList.remove("active");
    setTimeout(() => { 
        modal.style.display = "none"; 
        document.getElementById("modalLoading").style.display = "block";
        document.getElementById("modalSuccess").style.display = "none";
    }, 300);
}

function showSuccessModal(message) {
    const modal = document.getElementById("statusModal");
    if (!modal) return;
    document.getElementById("modalLoading").style.display = "none";
    document.getElementById("modalSuccess").style.display = "block";
    document.getElementById("successModalText").innerText = message;
    modal.style.display = "flex";
    setTimeout(() => { modal.classList.add("active"); }, 10);

    setTimeout(() => {
        closeStatusModal();
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    // Escape key to close search
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeSearch();
    });

    // Property search intercept
    const form = document.getElementById('propertiesSearchForm');
    if (form) {
        form.onsubmit = function(e) {
            e.preventDefault();
            const propType = form.querySelector('[name="type_of_project"]').value || 'All';
            const params = new URLSearchParams();
            const fields = ['location', 'city', 'facing', 'name', 'minpricing', 'maxpricing', 'look', 'position', 'approval', 'extent'];
            fields.forEach(f => {
                const el = form.querySelector('[name="' + f + '"]');
                if (el && el.value) params.append(f, el.value);
            });
            const qs = params.toString();
            window.location.href = '/properties/' + encodeURIComponent(propType) + '/' + (qs ? '?' + qs : '');
        };
    }
});
