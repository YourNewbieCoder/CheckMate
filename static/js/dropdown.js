// script.js
document.addEventListener('DOMContentLoaded', (event) => {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    const card = document.getElementById('droplist');
    const selectedExamInput = document.getElementById('selectedExam');

    dropdownToggle.addEventListener('click', () => {
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
        card.style.height = dropdownMenu.style.display === 'block' ? card.scrollHeight + 'px' : 'auto';
    });

    // Close the dropdown if the user clicks outside of it
    window.addEventListener('click', (event) => {
        if (!event.target.matches('.dropdown-toggle')) {
            if (dropdownMenu.style.display === 'block') {
                dropdownMenu.style.display = 'none';
                card.style.height = 'auto';
            }
        }
    });

    // Add event listeners to dropdown items
    const dropdownItems = document.querySelectorAll('.dropdown-menu a');
    dropdownItems.forEach(item => {
        item.addEventListener('click', (event) => {
            event.preventDefault();
            const selectedValue = item.getAttribute('data-value');
            dropdownToggle.textContent = selectedValue;
            selectedExamInput.value = selectedValue;
            dropdownMenu.style.display = 'none';
            card.style.height = 'auto';
        });
    });
});
