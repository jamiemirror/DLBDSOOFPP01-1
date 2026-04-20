async function fetchHabits() {
    const searchQuery = document.getElementById("search-bar").value;
    const intervalFilter = document.getElementById("interval-filter").value;
    const minStreakFilter = document.getElementById("min-streak-filter").value;
    let url = `/api/habits?name=${searchQuery}&interval=${intervalFilter}&min_streak=${minStreakFilter}`;
    const response = await fetch(url);
    const habits = await response.json();
    
    renderHabits(habits);
}

function renderHabits(habits) {
    const tableBody = document.getElementById("habit-table-body");
    tableBody.innerHTML = "";  

    habits.forEach(habit => {
        let row = `<tr>
            <td>${habit.id}</td>
            <td>${habit.name}</td>
            <td>${habit.description || "No description"}</td>
            <td>${habit.interval}</td>
            <td>${habit.streak}</td>
        </tr>`;
        tableBody.innerHTML += row;
    });
}

document.addEventListener("DOMContentLoaded", () => {
    fetchHabits(); //habits loadingfrom scratch
    document.getElementById("search-bar").addEventListener("input", fetchHabits);
    document.getElementById("interval-filter").addEventListener("change", fetchHabits);
    document.getElementById("min-streak-filter").addEventListener("change", fetchHabits);
});