// order-section category switching
// This JavaScript assumes Bootstrap and jQuery might be available or you have custom JS for tab switching.
    function selectCategory(element, categoryId) {
        // Remove 'active' class from all list items
        document.querySelectorAll('#category-list .list-group-item').forEach(item => {
            item.classList.remove('active');
        });
        // Add 'active' class to the clicked item
        element.classList.add('active');

        // Hide all category sections
        document.querySelectorAll('.category-section').forEach(section => {
            section.classList.add('d-none');
        });
        // Show the selected category section
        document.getElementById(categoryId).classList.remove('d-none');
    }

    // Optional: Initialize the first category as active and visible on page load
    document.addEventListener('DOMContentLoaded', function() {
        const firstCategoryItem = document.querySelector('#category-list .list-group-item');
        if (firstCategoryItem) {
            firstCategoryItem.click(); // Simulate a click on the first item
        }
    });

    // Add event listeners for plus/minus/add buttons (simplified example)
    document.querySelectorAll('.card').forEach(card => {
        const minusBtn = card.querySelector('.minus-btn');
        const plusBtn = card.querySelector('.plus-btn');
        const quantitySpan = card.querySelector('.quantity');
        const addBtn = card.querySelector('.add-btn');

        let quantity = 0;

        minusBtn.addEventListener('click', () => {
            if (quantity > 0) {
                quantity--;
                quantitySpan.textContent = quantity;
            }
        });

        plusBtn.addEventListener('click', () => {
            quantity++;
            quantitySpan.textContent = quantity;
        });

        addBtn.addEventListener('click', () => {
            // Implement add to cart logic here
            alert(`Added ${quantity} of ${card.querySelector('.card-title').textContent} to cart.`);
            // Reset quantity after adding to cart if desired
            quantity = 0; 
            quantitySpan.textContent = quantity;
        });
    });



    // order-section category switching
    /*
    function selectCategory(element, categoryId) {
        // Remove active class from all list items
        document.querySelectorAll('#category-list .list-group-item').forEach(el => el.classList.remove('active'));
        element.classList.add('active');

        // Hide all category sections
        document.querySelectorAll('.category-section').forEach(div => div.classList.add('d-none'));

        // Show selected category
        document.getElementById(categoryId).classList.remove('d-none');
    }*/


    



// ------------------------------------------------------------------------------------------------

// Tab navigation
        function showSection(section) {
            // Hide all sections
            document.querySelectorAll('.tab-section').forEach(sec => sec.classList.add('d-none'));

            // Remove 'active' class from all tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

            // Show the selected section
            const targetSection = document.getElementById(`${section}-section`);
            if (targetSection) {
                targetSection.classList.remove('d-none');
            }

            // Activate the corresponding tab button
            document.querySelectorAll('.tab-btn').forEach(btn => {
                if (btn.textContent.toLowerCase().includes(section)) {
                    btn.classList.add('active');
                }
            });
        }

        // Load default section on page load
        showSection('overview');

        /* Category navigation
         function selectCategory(element) {
            document.querySelectorAll('#category-list .list-group-item').forEach(item => {
                item.classList.remove('active');
            });
            element.classList.add('active');
        }*/

        // Menu data
        const menuData = {
            chefs_signature: [
                { name: "Smoky Veg Bisque", price: 420 },
                { name: "TMC Signature Broccoli Cheddar", price: 462 }
            ],
            shuruvat: [
                { name: "Paneer Tikka", price: 310 },
                { name: "Hara Bhara Kebab", price: 290 }
            ],
            dil_hindustani: [
                { name: "Dal Makhani", price: 270 },
                { name: "Paneer Butter Masala", price: 320 }
            ],
            chaat: [
                { name: "Papdi Chaat", price: 160 },
                { name: "Dahi Puri", price: 150 },
                { name: "Raj Kachori", price: 180 }
            ],
            soup: [
                { name: "Tomato Soup", price: 140 },
                { name: "Sweet Corn Soup", price: 150 }
            ],
            pesh: [
                { name: "Stuffed Mushroom", price: 290 },
                { name: "Paneer Peshawari", price: 340 }
            ],
            angaron: [
                { name: "Tandoori Paneer Tikka", price: 330 },
                { name: "Malai Soya Chaap", price: 310 }
            ],
            baked: [
                { name: "Baked Macaroni", price: 280 },
                { name: "Baked Lasagna", price: 300 }
            ]
        };

        function selectCategory(element, categoryKey) {
            // Update active class
            document.querySelectorAll('#category-list .list-group-item').forEach(item => {
                item.classList.remove('active');
            });
            element.classList.add('active');

            // Update heading
            document.getElementById("category-title").innerText = element.innerText;

            // Load items
            const container = document.getElementById("food-items");
            container.innerHTML = ""; // clear previous

            menuData[categoryKey].forEach(item => {
                container.innerHTML += `
                    <div class="d-flex mb-4">
                        <img src="assets/img/about.jpg" alt="${item.name}" class="rounded" 
                            style="width: 80px; height: 80px; object-fit: cover;" />
                        <div class="ms-3">
                            <h6 class="mb-1">${item.name}</h6>
                            <p class="mb-0">₹${item.price}</p>
                        </div>
                    </div>
                `;
            });
        }

        // Load default
        window.onload = function () {
            selectCategory(document.querySelector('#category-list .active'), 'chefs_signature');
        };

        // Photo filtering
        function filterPhotos(category) {
            // Toggle button styles
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('btn-danger', 'active');
                btn.classList.add('btn-outline-secondary');
            });

            // Highlight active button
            const activeBtn = Array.from(document.querySelectorAll('.filter-btn')).find(btn =>
                btn.textContent.toLowerCase().includes(category)
            );
            if (activeBtn) {
                activeBtn.classList.add('btn-danger', 'active');
                activeBtn.classList.remove('btn-outline-secondary');
            }

            // Filter images
            document.querySelectorAll('.photo-item').forEach(item => {
                item.style.display = (category === 'all' || item.classList.contains(category)) ? 'block' : 'none';
            });
        }

        window.onload = () => {
            filterPhotos('all');
        };

        // Scroll functions
        function scrollToBooking() {
            // Hide all sections
            document.querySelectorAll('.tab-section').forEach(sec => sec.classList.add('d-none'));

            // Show only book-section
            document.getElementById('book-section').classList.remove('d-none');

            // Remove active class from all tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

            // Add active class to "Book a Table" tab button
            document.querySelectorAll('.tab-btn').forEach(btn => {
                if (btn.innerText.trim() === 'Book a Table') {
                    btn.classList.add('active');
                }
            });

            // Scroll to book-section smoothly
            setTimeout(() => {
                document.getElementById('book-section').scrollIntoView({ behavior: 'smooth' });
            }, 100);
        }

        function scrollToPhotos() {
            // Hide all tab sections
            document.querySelectorAll('.tab-section').forEach(sec => sec.classList.add('d-none'));

            // Show only the photos section
            document.getElementById('photos-section').classList.remove('d-none');

            // Remove active class from all tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

            // Add active class to the Photos tab
            document.querySelectorAll('.tab-btn').forEach(btn => {
                if (btn.innerText.trim() === 'Photos') {
                    btn.classList.add('active');
                }
            });

            // Smooth scroll to photos section
            setTimeout(() => {
                document.getElementById('photos-section').scrollIntoView({ behavior: 'smooth' });
            }, 100);
        }

        // Fancy booking form functionality
        document.addEventListener('DOMContentLoaded', function() {
            // Set today as default date
            const today = new Date();
            const formattedDate = today.toISOString().split('T')[0];
            document.getElementById('date').value = formattedDate;
            
            // Slot selection functionality
            const slots = document.querySelectorAll('.fancy-booking-form .slot');
            slots.forEach(slot => {
                slot.addEventListener('click', () => {
                    // Remove active class from all slots
                    slots.forEach(s => s.classList.remove('active'));
                    // Add active class to clicked slot
                    slot.classList.add('active');
                    
                    // Update the time input
                    document.getElementById('time').value = slot.getAttribute('data-time');
                });
            });
        });
    

    
    // Set carousel interval to 1 hour (3600000 ms)
    document.addEventListener('DOMContentLoaded', function() {
        const today = new Date();
        document.getElementById('date').value = today.toISOString().split('T')[0];
        
        const carousel = new bootstrap.Carousel('#ambience-carousel', {
            interval: 3600000, // 1 hour rotation
            wrap: true
        });
    });



// select category function in order-section

// NEW: Category switching function
        function selectCategory(element, categoryId) {
            // Remove active class from all categories
            document.querySelectorAll('#category-list .list-group-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Add active class to selected category
            element.classList.add('active');
            
            // Hide all category sections
            document.querySelectorAll('.category-section').forEach(section => {
                section.classList.add('d-none');
            });
            
            // Show selected category
            document.getElementById(categoryId).classList.remove('d-none');
        }

        // NEW: Quantity management
        document.addEventListener('click', function(e) {
            if(e.target.classList.contains('plus-btn')) {
                const quantityEl = e.target.closest('.d-flex').querySelector('.quantity');
                quantityEl.textContent = parseInt(quantityEl.textContent) + 1;
            }
            else if(e.target.classList.contains('minus-btn')) {
                const quantityEl = e.target.closest('.d-flex').querySelector('.quantity');
                const current = parseInt(quantityEl.textContent);
                if(current > 0) quantityEl.textContent = current - 1;
            }
            else if(e.target.classList.contains('add-btn')) {
                const quantity = parseInt(e.target.closest('.d-flex').querySelector('.quantity').textContent);
                if(quantity > 0) {
                    alert(`Added ${quantity} items to cart!`);
                    // Here you would typically update cart state
                }
            }
        });



// js for reviews section

  // Handle Star Rating Click
//   document.addEventListener("DOMContentLoaded", function () {
//     // Star rating click logic
//     document.querySelectorAll('.star-rating').forEach(ratingBox => {
//       const stars = ratingBox.querySelectorAll('.star');
//       const hiddenInput = ratingBox.querySelector('input[type="hidden"]');
//       stars.forEach(star => {
//         star.addEventListener('click', function () {
//           const value = this.getAttribute('data-value');
//           hiddenInput.value = value;

//           // Fill/unfill stars
//           stars.forEach(s => {
//             s.classList.remove('fa-star');
//             s.classList.add('fa-star-o');
//           });
//           for (let i = 0; i < value; i++) {
//             stars[i].classList.remove('fa-star-o');
//             stars[i].classList.add('fa-star');
//           }
//         });
//       });
//     });

//     // AJAX review submission
//     const form = document.getElementById("review-form");
//     form.addEventListener("submit", function (e) {
//       e.preventDefault();

//       const formData = new FormData(form);
//       fetch("{% url 'restaurants:submit_review' restaurant.slug %}", {
//         method: "POST",
//         headers: {
//           "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
//         },
//         body: formData,
//       })
//         .then(response => response.json())
//         .then(data => {
//           if (data.success) {
//             // Clear form
//             form.reset();
//             form.querySelectorAll('.fa-star').forEach(star => {
//               star.classList.remove('fa-star');
//               star.classList.add('fa-star-o');
//             });

//             // Append new review
//             document.getElementById("submitted-reviews").insertAdjacentHTML('afterbegin', data.html);
//           } else {
//             alert("Error submitting review.");
//           }
//         })
//         .catch(error => {
//           console.error("Error:", error);
//         });
//     });
//   });

// document.querySelector('#review-form').addEventListener('submit', function (e) {
//     e.preventDefault();

//     const form = this;
//     const data = new FormData(form);

//     fetch("{% url 'submit-review' slug=restaurant.slug %}", {
//       method: 'POST',
//       headers: {
//         'X-Requested-With': 'XMLHttpRequest',
//         'X-CSRFToken': data.get('csrfmiddlewaretoken'),
//       },
//       body: data,
//     })
//     .then(res => res.json())
//     .then(json => {
//       if (json.success) {
//         document.querySelector('#submitted-reviews').insertAdjacentHTML('afterbegin', json.html);
//         form.reset();
//         document.querySelectorAll('.star').forEach(star => star.classList.remove('fa-star'));
//         document.querySelectorAll('.star').forEach(star => star.classList.add('fa-star-o'));
//       }
//     });
//   });

//   // Star rating logic
// //   document.querySelectorAll('.star-rating').forEach(group => {
// //     group.addEventListener('click', function (e) {
// //       if (e.target.classList.contains('star')) {
// //         const value = e.target.dataset.value;
// //         const field = group.dataset.field;
// //         group.querySelector('input').value = value;

// //         group.querySelectorAll('.star').forEach(star => {
// //           const starVal = star.dataset.value;
// //           star.classList.toggle('fa-star', starVal <= value);
// //           star.classList.toggle('fa-star-o', starVal > value);
// //         });
// //       }
// //     });
// //   });
// document.addEventListener('DOMContentLoaded', function () {
//   // For each star rating container
//   document.querySelectorAll('.star-rating').forEach(function (container) {
//     const fieldName = container.getAttribute('data-field');
//     const input = container.querySelector('input[name="' + fieldName + '"]');
//     const stars = container.querySelectorAll('.star');

//     stars.forEach(star => {
//       star.addEventListener('click', function () {
//         const value = this.getAttribute('data-value');
//         input.value = value;

//         // Remove active from all
//         stars.forEach(s => s.classList.remove('fa-star'));
//         stars.forEach(s => s.classList.add('fa-star-o'));

//         // Add active to selected stars
//         for (let i = 0; i < value; i++) {
//           stars[i].classList.remove('fa-star-o');
//           stars[i].classList.add('fa-star');
//         }
//       });
//     });
//   });
// });


// document.addEventListener('DOMContentLoaded', function () {
//   // Handle Star Clicks
//   document.querySelectorAll('.star-rating').forEach(function (group) {
//     const input = group.querySelector('input');
//     const stars = group.querySelectorAll('.star');

//     stars.forEach(star => {
//       star.addEventListener('click', function () {
//         const value = this.dataset.value;
//         input.value = value;

//         stars.forEach(s => {
//           const starVal = s.dataset.value;
//           s.classList.toggle('fa-star', starVal <= value);
//           s.classList.toggle('fa-star-o', starVal > value);
//         });
//       });
//     });
//   });

//   // Handle AJAX form submission
//   document.querySelector('#review-form').addEventListener('submit', function (e) {
//     e.preventDefault();
//     const form = this;
//     const data = new FormData(form);

//     fetch("{% url 'restaurants:submit_review' restaurant.slug %}", {
//       method: 'POST',
//       headers: {
//         'X-Requested-With': 'XMLHttpRequest',
//         'X-CSRFToken': data.get('csrfmiddlewaretoken')
//       },
//       body: data
//     })
//     .then(response => response.json())
//     .then(json => {
//       if (json.success) {
//         // Reset form
//         form.reset();

//         // Reset star icons
//         document.querySelectorAll('.star').forEach(star => {
//           star.classList.remove('fa-star');
//           star.classList.add('fa-star-o');
//         });

//         // Append new review to top
//         document.getElementById("submitted-reviews").insertAdjacentHTML('afterbegin', json.html);
//       } else {
//         alert("Error submitting review.");
//       }
//     })
//     .catch(error => {
//       console.error("Submission error:", error);
//     });
//   });
// });




document.addEventListener("DOMContentLoaded", function () {
  // Star click logic
  document.querySelectorAll(".star-rating").forEach(function (group) {
    const stars = group.querySelectorAll(".star");
    const input = group.querySelector("input");

    stars.forEach(function (star) {
      star.addEventListener("click", function () {
        const value = this.dataset.value;
        input.value = value;

        stars.forEach(s => {
          s.classList.toggle("fa-star", s.dataset.value <= value);
          s.classList.toggle("fa-star-o", s.dataset.value > value);
        });
      });
    });
  });

  // AJAX Form Submit
  document.getElementById("review-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    fetch("{% url 'restaurants:submit_review' restaurant.slug %}", {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
      },
      body: formData,
    })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        form.reset();
        document.querySelectorAll(".star").forEach(star => {
          star.classList.remove("fa-star");
          star.classList.add("fa-star-o");
        });

        // Prepend new review
        document.getElementById("submitted-reviews").insertAdjacentHTML("afterbegin", data.html);
      } else {
        alert("Review failed. Try again.");
      }
    })
    .catch((err) => {
      console.error("Error:", err);
    });
  });
});



document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.star-rating').forEach(function (ratingBox) {
      const stars = ratingBox.querySelectorAll('.star');
      const hiddenInput = ratingBox.querySelector('input[type="hidden"]');

      stars.forEach(function (star) {
        star.addEventListener('click', function () {
          const value = this.getAttribute('data-value');
          hiddenInput.value = value;

          stars.forEach(s => {
            s.classList.remove('fa-star');
            s.classList.add('fa-star-o');
          });

          for (let i = 0; i < value; i++) {
            stars[i].classList.remove('fa-star-o');
            stars[i].classList.add('fa-star');
          }
        });
      });
    });
  });

  




// ================ Core Functions ================
// Tab switching functionality
// function showSection(sectionId) {
//     // Hide all sections
//     document.querySelectorAll('.tab-section').forEach(section => {
//         section.classList.add('d-none');
//     });
    
//     // Show selected section
//     document.getElementById(`${sectionId}-section`).classList.remove('d-none');
    
//     // Update active tab button
//     document.querySelectorAll('.tab-btn').forEach(btn => {
//         btn.classList.remove('active');
//     });
//     event.target.classList.add('active');
// }

// // Category switching functionality
// function selectCategory(element, categoryId) {
//     // Update active category in list
//     document.querySelectorAll('#category-list .list-group-item').forEach(item => {
//         item.classList.remove('active');
//     });
//     element.classList.add('active');
    
//     // Show selected category
//     document.querySelectorAll('.category-section').forEach(section => {
//         section.classList.add('d-none');
//     });
//     document.getElementById(categoryId).classList.remove('d-none');
// }

// Photo filtering functionality
// function filterPhotos(category) {
//     // Update active filter button
//     document.querySelectorAll('.filter-btn').forEach(btn => {
//         btn.classList.remove('active', 'btn-danger');
//         btn.classList.add('btn-outline-secondary');
//     });
//     event.target.classList.add('active', 'btn-danger');
//     event.target.classList.remove('btn-outline-secondary');
    
//     // Filter photos
//     const allPhotos = document.querySelectorAll('.photo-item');
//     allPhotos.forEach(photo => {
//         if (category === 'all' || photo.classList.contains(category)) {
//             photo.style.display = 'block';
//         } else {
//             photo.style.display = 'none';
//         }
//     });
// }

// // Scroll to booking section
// function scrollToBooking() {
//     showSection('book');
//     document.getElementById('book-section').scrollIntoView({ behavior: 'smooth' });
// }

// // Scroll to photos section
// function scrollToPhotos() {
//     showSection('photos');
//     document.getElementById('photos-section').scrollIntoView({ behavior: 'smooth' });
// }

// // ================ Menu Data ================
// const menuData = {
//     chefs_signature: [
//         { name: "Smoky Veg Bisque", price: 420 },
//         { name: "TMC Signature Broccoli Cheddar", price: 462 }
//     ],
//     shuruvat: [
//         { name: "Paneer Tikka", price: 310 },
//         { name: "Hara Bhara Kebab", price: 290 }
//     ],
//     dil_hindustani: [
//         { name: "Dal Makhani", price: 270 },
//         { name: "Paneer Butter Masala", price: 320 }
//     ],
//     chaat: [
//         { name: "Papdi Chaat", price: 160 },
//         { name: "Dahi Puri", price: 150 },
//         { name: "Raj Kachori", price: 180 }
//     ],
//     soup: [
//         { name: "Tomato Soup", price: 140 },
//         { name: "Sweet Corn Soup", price: 150 }
//     ],
//     pesh: [
//         { name: "Stuffed Mushroom", price: 290 },
//         { name: "Paneer Peshawari", price: 340 }
//     ],
//     angaron: [
//         { name: "Tandoori Paneer Tikka", price: 330 },
//         { name: "Malai Soya Chaap", price: 310 }
//     ],
//     baked: [
//         { name: "Baked Macaroni", price: 280 },
//         { name: "Baked Lasagna", price: 300 }
//     ]
// };

// // ================ Event Listeners ================
// document.addEventListener('DOMContentLoaded', function() {
//     // Initialize page
//     showSection('overview');
//     filterPhotos('all');
    
//     // Set today as default date
//     const today = new Date();
//     document.getElementById('date').value = today.toISOString().split('T')[0];
    
//     // Initialize carousel
//     const carousel = new bootstrap.Carousel('#ambience-carousel', {
//         interval: 3600000, // 1 hour rotation
//         wrap: true
//     });
    
//     // Time slot selection
//     const slots = document.querySelectorAll('.fancy-booking-form .slot');
//     slots.forEach(slot => {
//         slot.addEventListener('click', () => {
//             slots.forEach(s => s.classList.remove('active'));
//             slot.classList.add('active');
//             document.getElementById('time').value = slot.getAttribute('data-time');
//         });
//     });
    
//     // Event delegation for quantity controls
//     document.addEventListener('click', function(e) {
//         // Plus button
//         if(e.target.classList.contains('plus-btn')) {
//             const quantityEl = e.target.closest('.d-flex').querySelector('.quantity');
//             quantityEl.textContent = parseInt(quantityEl.textContent) + 1;
//         }
//         // Minus button
//         else if(e.target.classList.contains('minus-btn')) {
//             const quantityEl = e.target.closest('.d-flex').querySelector('.quantity');
//             const current = parseInt(quantityEl.textContent);
//             if(current > 0) quantityEl.textContent = current - 1;
//         }
//         // Add to cart button
//         else if(e.target.classList.contains('add-btn')) {
//             const quantity = parseInt(e.target.closest('.d-flex').querySelector('.quantity').textContent);
//             if(quantity > 0) {
//                 alert(`Added ${quantity} items to cart!`);
//                 // Reset quantity after adding
//                 e.target.closest('.d-flex').querySelector('.quantity').textContent = 0;
//             }
//         }
//     });
    
//     // Star rating functionality
//     document.querySelectorAll('.star-rating').forEach(function(ratingBox) {
//         const stars = ratingBox.querySelectorAll('.star');
//         const hiddenInput = ratingBox.querySelector('input[type="hidden"]');
        
//         stars.forEach(function(star) {
//             star.addEventListener('click', function() {
//                 const value = this.getAttribute('data-value');
//                 hiddenInput.value = value;
                
//                 // Update star display
//                 stars.forEach(s => {
//                     s.classList.remove('fa-star');
//                     s.classList.add('fa-star-o');
//                 });
//                 for (let i = 0; i < value; i++) {
//                     stars[i].classList.remove('fa-star-o');
//                     stars[i].classList.add('fa-star');
//                 }
//             });
//         });
//     });
    
//     // Review form submission
//     const reviewForm = document.getElementById("review-form");
//     if (reviewForm) {
//         reviewForm.addEventListener("submit", function(e) {
//             e.preventDefault();
//             const form = e.target;
//             const formData = new FormData(form);
            
//             // AJAX submission would go here
//             console.log("Form submitted with data:", Object.fromEntries(formData));
            
//             // Reset form and stars
//             form.reset();
//             document.querySelectorAll('.star').forEach(star => {
//                 star.classList.remove('fa-star');
//                 star.classList.add('fa-star-o');
//             });
            
//             // Success message
//             alert("Review submitted successfully!");
//         });
//     }
// });

// // ================ Helper Functions ================
// // Menu category selection
// function loadMenuCategory(element, categoryKey) {
//     // Update active class
//     document.querySelectorAll('#category-list .list-group-item').forEach(item => {
//         item.classList.remove('active');
//     });
//     element.classList.add('active');
    
//     // Update heading
//     document.getElementById("category-title").innerText = element.innerText;
    
//     // Load items
//     const container = document.getElementById("food-items");
//     container.innerHTML = "";
    
//     menuData[categoryKey].forEach(item => {
//         container.innerHTML += `
//             <div class="d-flex mb-4">
//                 <img src="assets/img/about.jpg" alt="${item.name}" class="rounded" 
//                     style="width: 80px; height: 80px; object-fit: cover;" />
//                 <div class="ms-3">
//                     <h6 class="mb-1">${item.name}</h6>
//                     <p class="mb-0">₹${item.price}</p>
//                 </div>
//             </div>
//         `;
//     });
// }