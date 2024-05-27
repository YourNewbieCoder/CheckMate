document.addEventListener('DOMContentLoaded', (event) => {
    const examSelect = document.getElementById('examSelect');
    const classSelect = document.getElementById('classSelect');
    const dataTableBody = document.getElementById('dataTable').querySelector('tbody');

    const data = {
        first: {
            sectionA: [
                { name: 'Alice', score: 85, date: '2024-06-20' },
                { name: 'Bob', score: 90, date: '2024-06-20' },
                { name: 'Charlie', score: 78, date: '2024-06-20' }
            ],
            sectionB: [
                { name: 'David', score: 80, date: '2024-06-20' },
                { name: 'Eva', score: 88, date: '2024-06-20' },
                { name: 'Frank', score: 85, date: '2024-06-20' }
            ]
        },
        second: {
            sectionA: [
                { name: 'Alice', score: 88, date: '2024-08-23' },
                { name: 'Bob', score: 92, date: '2024-08-23' },
                { name: 'Charlie', score: 81, date: '2024-08-23' }
            ],
            sectionB: [
                { name: 'David', score: 82, date: '2024-08-23' },
                { name: 'Eva', score: 90, date: '2024-08-23' },
                { name: 'Frank', score: 86, date: '2024-08-23' }
            ]
        },
        third: {
            sectionA: [
                { name: 'Alice', score: 90, date: '2024-12-16' },
                { name: 'Bob', score: 95, date: '2024-12-16' },
                { name: 'Charlie', score: 85, date: '2024-12-16' }
            ],
            sectionB: [
                { name: 'David', score: 84, date: '2024-12-16' },
                { name: 'Eva', score: 91, date: '2024-12-16' },
                { name: 'Frank', score: 88, date: '2024-12-16' }
            ]
        },
        fourth: {
            sectionA: [
                { name: 'Alice', score: 88, date: '2025-02-23' },
                { name: 'Bob', score: 92, date: '2025-02-23' },
                { name: 'Charlie', score: 81, date: '2025-02-23' }
            ],
            sectionB: [
                { name: 'David', score: 85, date: '2025-02-23' },
                { name: 'Eva', score: 93, date: '2025-02-23' },
                { name: 'Frank', score: 89, date: '2025-02-23' }
            ]
        }
    };

    function populateTable(exam, section) {
        // Clear existing rows
        dataTableBody.innerHTML = '';

        // Populate new rows
        data[exam][section].forEach(item => {
            const row = document.createElement('tr');
            const nameCell = document.createElement('td');
            const scoreCell = document.createElement('td');
            const dateCell = document.createElement('td');

            nameCell.textContent = item.name;
            scoreCell.textContent = item.score;
            dateCell.textContent = item.date;

            row.appendChild(nameCell);
            row.appendChild(scoreCell);
            row.appendChild(dateCell);

            dataTableBody.appendChild(row);
        });
    }

    // Initial population based on the first dropdown option
    populateTable(examSelect.value, classSelect.value);

    // Update table when dropdown selection changes
    examSelect.addEventListener('change', () => {
        populateTable(examSelect.value, classSelect.value);
    });

    classSelect.addEventListener('change', () => {
        populateTable(examSelect.value, classSelect.value);
    });
});
