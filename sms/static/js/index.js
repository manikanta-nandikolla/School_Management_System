function goToLogin() {
        const selectedUrl = document.getElementById('roleSelect').value;
        if (selectedUrl) {
            window.location.href = selectedUrl;
        } else {
            alert("Please select a role to continue.");
        }
    }