document.addEventListener('DOMContentLoaded', function () {
    // Collapse toggle ikonları sadece tıklanan kart için
    document.querySelectorAll('.toggle-details-btn').forEach(button => {
        const targetSelector = button.getAttribute('data-bs-target');
        const collapseTarget = document.querySelector(targetSelector);
        const icon = button.querySelector('i');

        // Bootstrap collapse instance oluştur
        const bsCollapse = bootstrap.Collapse.getOrCreateInstance(collapseTarget, { toggle: false });

        // Butona tıklayınca collapse toggle
        button.addEventListener('click', function () {
            bsCollapse.toggle();
        });

        // Gösterildiğinde ikon güncelle
        collapseTarget.addEventListener('shown.bs.collapse', function () {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        });

        // Gizlendiğinde ikon güncelle
        collapseTarget.addEventListener('hidden.bs.collapse', function () {
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        });
    });

    // Arama formu auto-submit (1.5 saniye sonra)
    let searchTimeout;
    const searchInput = document.getElementById('search_name');

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Auto submit istersen aktif et
                // this.form.submit();
            }, 1500);
        });
    }
});
