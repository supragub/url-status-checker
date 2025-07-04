document.addEventListener("DOMContentLoaded", function () {
    let websites = [];
    let filteredWebsites = []; // Store the filtered data
    let currentSort = {
        column: null,
        direction: "asc",
    };

    loadUrlRegistry();

    document.getElementById("addUrlBtn").addEventListener("click", addUrl);
    document.getElementById("searchInput").addEventListener("keyup", filterTable);
    document.getElementById("importBtn").addEventListener("click", importJson);
    document.getElementById("exportBtn").addEventListener("click", exportJson);

    // Add event listeners for sorting
    document
        .querySelectorAll("th:not(#toggleActionsColumn)")
        .forEach((header, index) => {
            header.addEventListener("click", () => {
                sortTable(index);
            });
        });

    // Scroll behavior for the title
    document.addEventListener("scroll", function () {
        const scrollTitle = document.getElementById("scrollTitle");
        if (window.scrollY > 0) {
            scrollTitle.style.display = "block";
        } else {
            scrollTitle.style.display = "none";
        }
    });

    const actionsColumnHeader = document.getElementById("toggleActionsColumn");
    let actionsVisible = false;
    toggleActionsColumn(actionsVisible);

    actionsColumnHeader.addEventListener("click", function () {
        actionsVisible = !actionsVisible;
        toggleActionsColumn(actionsVisible);
        actionsColumnHeader.textContent = actionsVisible
            ? "Actions (-)"
            : "Actions (+)";
    });

    function toggleActionsColumn(show) {
        const actionColumns = document.querySelectorAll(".actions-column");
        actionColumns.forEach((col) => {
            col.style.display = show ? "flex" : "none";
        });
    }

    function loadUrlRegistry() {
        fetch("data/url_registry.json")
            .then((response) => response.json())
            .then((data) => {
                websites = data.map((item, index) => ({
                    id: item.id,
                    number: index + 1,
                    name: item.name,
                    url: item.url,
                    statuscd: item.statuscd,
                    statusmsg: item.statusmsg,
                    lastchange: item.lastchange,
                    totaldowntime: item.totaldowntime,
                }));
                filteredWebsites = websites; // By default, show all data
                renderTable(filteredWebsites);
            })
            .catch((error) => console.error("Error loading JSON data:", error));
    }

    function renderTable(websitesToRender) {
        const tableBody = document.querySelector("#statusTable tbody");
        tableBody.innerHTML = "";

        websitesToRender.forEach((website) => {
            const statusColumn = `
        <td class="status-column" style="background-color: ${getStatusColor(
                website.statuscd
            )}" 
            data-statusmsg="${website.statusmsg}">${website.statuscd}</td>
      `;
            const row = document.createElement("tr");
            row.innerHTML = `
          <td class="number-column">${website.number}</td>
          <td class="name-column">${website.name}</td>
          <td class="url-column"><a target="_blank" href="${website.url}">${website.url}</a></td>
          ${statusColumn}
          <td class="lastchange-column">${website.lastchange}</td>
          <td class="totaldowntime-column">${website.totaldowntime}</td>
          <td class="actions-column">
              <button class="resetBtn" data-id="${website.id}">Reset STATUS</button>
              <button id="editUrlBtn" onclick="editUrl(${website.id})">Edit URL</button>
              <button id="deleteUrlBtn" onclick="confirmDeleteUrl(${website.id}, '${website.name}')">Delete URL</button>
          </td>`;
            tableBody.appendChild(row);
        });

        document.querySelectorAll(".resetBtn").forEach((button) => {
            button.addEventListener("click", function () {
                const id = this.getAttribute("data-id");
                resetUrl(id);
            });
        });

        // Attach event listeners for tooltips
        const statusCells = document.querySelectorAll(".status-column");
        statusCells.forEach((cell) => {
            cell.addEventListener("mouseover", showTooltip);
            cell.addEventListener("mouseout", hideTooltip);
        });

        toggleActionsColumn(actionsVisible);
    }

    function sortTable(columnIndex) {
        const sortKey = [
            "number",
            "name",
            "url",
            "statuscd",
            "lastchange",
            "totaldowntime",
        ][columnIndex];

        // Toggle sort direction
        if (currentSort.column === sortKey) {
            currentSort.direction = currentSort.direction === "asc" ? "desc" : "asc";
        } else {
            currentSort.column = sortKey;
            currentSort.direction = "asc";
        }

        filteredWebsites.sort((a, b) => {
            const aValue = a[sortKey];
            const bValue = b[sortKey];

            if (typeof aValue === "string") {
                return currentSort.direction === "asc"
                    ? aValue.localeCompare(bValue)
                    : bValue.localeCompare(aValue);
            }
            return currentSort.direction === "asc"
                ? aValue - bValue
                : bValue - aValue;
        });

        renderTable(filteredWebsites);
    }

    function showTooltip(event) {
        const statusMsg = event.target.getAttribute("data-statusmsg");
        const tooltip = document.createElement("div");
        tooltip.className = "tooltip";
        tooltip.innerText = statusMsg;
        document.body.appendChild(tooltip);
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = `${rect.left + window.pageXOffset + rect.width / 2 - tooltip.offsetWidth / 2
            }px`;
        tooltip.style.top = `${rect.top + window.pageYOffset - tooltip.offsetHeight - 5
            }px`;
    }

    function hideTooltip() {
        const tooltip = document.querySelector(".tooltip");
        if (tooltip) {
            tooltip.remove();
        }
    }

    function resetUrl(id) {
        alert(`Reset button clicked for ID: ${id}`);
    }

    function importJson() {
        const input = document.createElement("input");
        input.type = "file";
        input.accept = ".json";
        input.onchange = (event) => {
            const file = event.target.files[0];
            const formData = new FormData();
            formData.append("file", file);

            fetch("/import_url_registry", {
                method: "POST",
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.error) {
                        alert("An error occurred: " + data.error);
                    } else {
                        alert("Import successful!");
                        loadUrlRegistry();
                    }
                })
                .catch((error) => console.error("Error:", error));
        };
        input.click();
    }

    function exportJson() {
        const exportData = websites.map(
            ({ id, name, url, statuscd, statusmsg, lastchange, totaldowntime }) => ({
                id,
                name,
                url,
                statuscd,
                statusmsg,
                lastchange,
                totaldowntime,
            })
        );
        const dataStr = JSON.stringify(exportData, null, 4);
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "url_registry.json";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function filterTable() {
        const searchTerm = document
            .getElementById("searchInput")
            .value.toLowerCase();

        if (searchTerm === "") {
            filteredWebsites = websites;
        } else {
            filteredWebsites = websites.filter(
                (website) =>
                    website.name.toLowerCase().includes(searchTerm) ||
                    website.url.toLowerCase().includes(searchTerm) ||
                    website.statuscd.toLowerCase().includes(searchTerm) ||
                    website.lastchange.toLowerCase().includes(searchTerm) ||
                    website.totaldowntime.toLowerCase().includes(searchTerm)
            );
        }

        renderTable(filteredWebsites);
    }

    function getStatusColor(statuscd) {
        switch (statuscd) {
            case "200":
                return "darkgreen";
            case "N/A":
                return "gray";
            default:
                return "darkred";
        }
    }

    function addUrl() {
        const name = prompt("Enter Website Name:");
        if (name === null) return alert("Website Name is required.");

        const url = prompt("Enter Website URL:");
        if (url === null) return alert("Website URL is required.");

        const id = websites.length ? Math.max(...websites.map((w) => w.id)) + 1 : 1;

        const newUrl = {
            id,
            name,
            url,
            statuscd: "N/A",
            statusmsg: "N/A",
            lastchange: "N/A",
            totaldowntime: "N/A",
        };

        websites.push(newUrl);
        location.reload();

        fetch("/add_url", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newUrl),
        })
            .then((response) => response.json())
            .then((data) => console.log("Success:", data))
            .catch((error) => console.error("Error:", error));
    }
});

function editUrl(id) {
    // Find the website with the given id in the DOM
    const row = document
        .querySelector(`button[onclick="editUrl(${id})"]`)
        .closest("tr");

    if (!row) return alert("Row not found");

    // The current name and URL are in the corresponding cells of the row
    const currentName = row.cells[1].textContent;
    const currentUrl = row.cells[2].textContent;

    // Pre-fill the prompts with the existing data
    const name = prompt("Edit Website Name:", currentName);
    // Check if the user closed the prompt (Cancel)
    if (name === null) return; // Exit if Cancel was clicked

    const url = prompt("Edit Website URL:", currentUrl);
    // Check if the user closed the prompt (Cancel)
    if (url === null) return; // Exit if Cancel was clicked

    if (!name || !url) return alert("Website Name and Website URL are required");

    // Create the updated object
    const updatedUrl = { id, name, url };

    // Send the data to the server
    fetch("/edit_url", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedUrl),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Success: " + data.message);
                location.reload(); // Refresh the page
            }
        })
        .catch((error) => console.error("Error:", error));
}

function confirmDeleteUrl(id, name) {
    const confirmation = confirm(
        `Are you sure you want to delete the website ${name}?`
    );
    if (confirmation) {
        deleteUrl(id);
    }
}

function deleteUrl(id) {
    fetch("/delete_url", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) alert("Error: " + data.error);
            else alert("Success: " + data.message);
            location.reload(); // Refresh the page
        })
        .catch((error) => console.error("Error:", error));
}
