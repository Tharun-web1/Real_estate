document.addEventListener('DOMContentLoaded', function() {
    const notifCards = document.querySelectorAll('.notif-card');
    
    notifCards.forEach(card => {
        card.addEventListener('click', function() {
            const link = this.getAttribute('data-link');
            if (link && link !== '#') {
                window.location.href = link;
            }
        });
    });
});
