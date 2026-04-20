document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ checkboxes.js loaded!");

    let isProcessing = false; //multiple requests preventing

    document.querySelectorAll(".h_check").forEach((checkbox) => {
        console.log(`Found checkbox with ID: ${checkbox.value}`);

        checkbox.addEventListener("click", async function (event) {
            if (isProcessing) {
                console.warn("🚧 Request in progress...");
                return;
            }

            isProcessing = true; //new request locking
            console.log(`Clicked: Habit ID ${this.value}, Checked: ${this.checked}`);

            try {
                let response = await fetch(`/check/${this.value}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ checked: this.checked }),
                });

                if (!response.ok) throw new Error(`HTTP error, status: ${response.status}`);

                let result = await response.json();
                console.log("✅ Update successful:", result);

                if (result.success) {
                    setTimeout(() => location.reload(), 10);
                }
            } catch (error) {
                console.error("❌ Error updating habit:", error);
            } finally {
                setTimeout(() => { isProcessing = false; }, 500); //flag reset
            }
        });
    });
});