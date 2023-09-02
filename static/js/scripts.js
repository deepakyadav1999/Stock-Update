document.addEventListener("DOMContentLoaded", () => {
    const submitButton = document.getElementById("submit-button");
    const outputTable = document.getElementById("output-table");

    submitButton.addEventListener("click", async () => {
        // Your code for handling the form submission goes here

        // Show the output table
        outputTable.style.display = "table";
    });
});

