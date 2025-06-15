window.onload = function () {
    const popup = document.getElementById('popup-message');
    document.getElementById('menu-toggle').addEventListener('click', function () {
        document.getElementById('menu-links').classList.toggle('hidden');
    });
};

function toggleQuantityPopup(id, name, maxQty) {
    document.getElementById('popup-item-id').value = id;
    document.getElementById('popup-item-name').textContent = name;
    document.getElementById('popup-item-quantity').textContent = maxQty;
    document.getElementById('quantity-input').max = maxQty;
    document.getElementById('quantity-input').value = 1;

    // Reset size select to default M
    const sizeSelect = document.getElementById('size-select');
    if (sizeSelect) {
        sizeSelect.value = 'S';
    }

    document.getElementById('quantity-popup').classList.remove('hidden');
}

function closeQuantityPopup() {
    document.getElementById('quantity-popup').classList.add('hidden');
}
