function toggleClearButton(input) {
        const clearIcon = input.parentElement.querySelector(".clear-icon");
        clearIcon.style.display = input.value.trim() !== "" ? "block" : "none";
      }

      function clearSearch(icon) {
        const input = icon.parentElement.querySelector(".search-input");
        input.value = "";
        icon.style.display = "none";
        input.focus();
      }

      function toggleSidebar() {
        document.getElementById("sidebar").classList.toggle("collapsed");
      }

      lucide.createIcons();