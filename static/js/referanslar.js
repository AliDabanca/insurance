const input = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');

input.addEventListener('input', function () {
    const query = this.value.trim();

    // Eğer 3 karakterden azsa sonuçları temizle ve geri dön
    if (query.length < 3) {
        resultsDiv.innerHTML = '';
        return;
    }

    fetch(`/referanslar/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            resultsDiv.innerHTML = '';
            if (data.data.length === 0) {
                resultsDiv.innerHTML = '<p class="text-muted text-center mt-3">Aramanıza uygun referans bulunamadı.</p>';
                return;
            }

            data.data.forEach(item => {
                let colorClass = '';
                const adet = parseInt(item.police_adet) || 0;
                if (adet <= 2) colorClass = 'bg-low';
                else if (adet <= 5) colorClass = 'bg-medium';
                else colorClass = 'bg-high';

                const card = document.createElement('div');
                card.className = `col-md-4 mb-4`;
                card.innerHTML = `
                    <div class="card h-100 card-custom ${colorClass}">
                        <div class="card-body">
                            <h5 class="card-title">${item.ad_soyadi}</h5>
                            <p class="card-text"><strong>Poliçe Adet:</strong> ${item.police_adet}</p>
                            <p class="card-text"><strong>Referans:</strong> ${item.referans}</p>
                            <p class="card-text"><strong>Açıklama:</strong> ${item.aciklama || '-'}</p>
                        </div>
                    </div>
                `;
                resultsDiv.appendChild(card);
            });
        });
});
