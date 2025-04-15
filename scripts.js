// Script principal pour les interactions de l'application

// Affichage dynamique des sections en fonction de l'option sélectionnée
document.addEventListener("DOMContentLoaded", function () {
    const roomTypeSelect = document.getElementById("type");
    const codeGroup = document.getElementById("code_group");
    const costGroup = document.getElementById("cost_group");

    if (roomTypeSelect) {
        roomTypeSelect.addEventListener("change", function () {
            if (this.value === "prive") {
                codeGroup.style.display = "block";
                costGroup.style.display = "none";
            } else if (this.value === "payant") {
                codeGroup.style.display = "none";
                costGroup.style.display = "block";
            } else {
                codeGroup.style.display = "none";
                costGroup.style.display = "none";
            }
        });
    }
});

// Confirmation avant la suppression
function confirmDelete(message) {
    return confirm(message || "Êtes-vous sûr de vouloir supprimer cet élément ?");
}

// Notification d'action réussie
function showNotification(message, type = "success") {
    const notification = document.createElement("div");
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.textContent = message;

    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "btn-close";
    closeButton.setAttribute("data-bs-dismiss", "alert");
    closeButton.setAttribute("aria-label", "Close");

    notification.appendChild(closeButton);
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Exemple : Appel de la notification
// showNotification("Bienvenue dans l'application !");

// Gestion des actions dynamiques pour les boutons
document.querySelectorAll(".btn-delete").forEach((button) => {
    button.addEventListener("click", function () {
        if (!confirmDelete("Voulez-vous vraiment supprimer cet élément ?")) {
            event.preventDefault();
        }
    });
});
