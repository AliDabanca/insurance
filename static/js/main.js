// Loading states
function showLoading(element) {
    element.classList.add('loading');
    element.setAttribute('disabled', 'disabled');
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.removeAttribute('disabled');
}

// Form submit loading
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoading(submitBtn);
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> İşleniyor...';
            }
        });
    });

    // Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                const closeBtn = alert.querySelector('.btn-close');
                if (closeBtn) closeBtn.click();
            }
        }, 5000);
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// main.js içinde
document.addEventListener('DOMContentLoaded', function () {
    const showMoreLink = document.getElementById('show-more-policies');
    const extraPolicies = document.querySelectorAll('.extra-policy');

    if (showMoreLink && extraPolicies.length > 0) {
        showMoreLink.style.display = 'inline'; // göster
    } else if (showMoreLink) {
        showMoreLink.style.display = 'none'; // gizle
    }

});

