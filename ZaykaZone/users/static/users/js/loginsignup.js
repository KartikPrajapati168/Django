function toggleForm() {
        document.getElementById("signupForm").classList.toggle("hidden");
        document.getElementById("loginForm").classList.toggle("hidden");
      }

      function toggleCountryDropdown(form) {
        document.getElementById(`${form}CountryDropdown`).style.display =
          "block";
      }

      function selectCountry(form, code, flagUrl) {
        document.getElementById(`${form}DialCode`).textContent = code;
        document.getElementById(`${form}FlagImg`).src = flagUrl;
        document.getElementById(`${form}CountryDropdown`).style.display =
          "none";
      }

      document.addEventListener("click", function (e) {
        ["signup", "login"].forEach((form) => {
          const dropdown = document.getElementById(`${form}CountryDropdown`);
          const prefix = document.getElementById(`${form}Prefix`);
          if (dropdown && prefix && !prefix.contains(e.target)) {
            dropdown.style.display = "none";
          }
        });
      });