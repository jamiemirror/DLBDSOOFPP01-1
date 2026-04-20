document.addEventListener("DOMContentLoaded", function() {
    fetchHabits();
});

function fetchHabits() {
    const searchQuery = document.getElementById("search").value.trim();
    const intervalFilter = document.getElementById("interval").value;
    const minStreak = document.getElementById("streak").value;
    const sortBy = document.getElementById("sort").value;
    const reverseSort = document.getElementById("reverseSort").checked; //reverse checkbox

    let url = `/api/habits?search=${encodeURIComponent(searchQuery)}`;

    if (intervalFilter !== "all") {
        url += `&interval=${encodeURIComponent(intervalFilter)}`;
    }

    if (minStreak) {
        url += `&streak=${encodeURIComponent(minStreak)}`;
    }
    
    if (sortBy !== "none") {
        url += `&sort=${encodeURIComponent(sortBy)}`;
    }
    if (reverseSort !== false) {
        url += `&reverse=${encodeURIComponent(reverseSort)}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(habits => displayHabits(habits)) 
        .catch(error => console.error("Error fetching habits:", error));
}

function displayHabits(habits) {
    const tableBody = document.getElementById("habitTableBody");
    tableBody.innerHTML = ""; 

    if (habits.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='5' style='text-align:center;'>No habits found</td></tr>";
        return;
    }

    habits.forEach(habit => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${habit.id}</td>
            <td>${habit.name}</td>
            <td>${habit.desc ? habit.desc : "Missing description"}</td>
            <td>${habit.interval}</td>
            <td>${habit.streak}</td>
        `;
        row.onclick = () => window.location.href = `/habit/${habit.id}`;
        tableBody.appendChild(row);
    });
}