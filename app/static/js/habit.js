document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ checkboxes.js loaded!");
    addButtonListener(); // Attach event listener when page loads
});

function addButtonListener() {
    const button = document.getElementById('check-btn');

    // Check Habit
    button.addEventListener('click', async function () {
        const habitId = this.value;  // Get value from button
        console.log(`🟢 Button clicked! Habit ID: ${habitId}`);

        try {
            const response = await fetch(`/check/${habitId}`, {  // Fixed fetch URL
                method: 'POST',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ checked: true }) // Example body
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const result = await response.json();
            console.log("✅ Completed!", result);

            if (result.success) {
                setTimeout(() => location.reload(), 100); // Slight delay before reload
            }

        } catch (err) {
            console.error(`❌ Error: ${err}`);
        }
    });

    // Edit Habit
    document.getElementById("edit-btn")?.addEventListener("click", function () {
        const habitId = this.value;
        console.log(`✏️ Editing habit ID: ${habitId}`);
        window.location.href = `/edit/${habitId}`; // Redirect to edit page
    });

    // Delete Habit
    document.getElementById("delete-btn")?.addEventListener("click", async function () {
        const habitId = this.value;
        console.log(`🗑️ Deleting habit ID: ${habitId}`);

        if (!confirm("Please confirm the habit deletion")) return;

        try {
            const response = await fetch(`/delete/${habitId}`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
            });
    
            if (!response.ok) {
                console.error(`❌ Failed to delete habit: ${response.status}`);
                alert("Failed to delete habit. Please try again.");
                return;
            }
            let result;
            try {
                result = await response.json();
                console.log("✅ Habit deleted!", result);
            } catch (jsonError) {
                console.warn("⚠️ No JSON response received. Redirecting...");
            }
    
            // Redirect to home page after deletion
            window.location.href = "/";
        } catch (err) {
            console.error(`❌ Error deleting habit: ${err}`);
            alert("An error occurred while deleting the habit.");
        }
    });
}