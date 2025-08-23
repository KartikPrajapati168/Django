// =================== TAB NAVIGATION (Section Switching) ===================
// Ye function tabs me navigate karne ke liye hai (Overview, Menu, Photos, Booking, etc.)
function showSection(section) {
    // Sab sections hide karo
    document.querySelectorAll('.tab-section').forEach(sec => sec.classList.add('d-none'));

    // Sab tab buttons se 'active' class remove karo
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    // Selected section show karo
    const targetSection = document.getElementById(`${section}-section`);
    if (targetSection) {
        targetSection.classList.remove('d-none');
    }

    // Selected tab ko active class do
    document.querySelectorAll('.tab-btn').forEach(btn => {
        if (btn.textContent.toLowerCase().includes(section)) {
            btn.classList.add('active');
        }
    });
}

// Page load hone par default 'overview' tab show karega
document.addEventListener('DOMContentLoaded', () => {
    showSection('overview');
});




// =================== CATEGORY SWITCHING (Order Section) ===================
// Menu category change karne ka kaam karta hai (Chefs Signature, Soups, etc.)
function selectCategory(element, categoryKey) {
    // Sab categories se active class remove
    document.querySelectorAll('#category-list .list-group-item').forEach(item => {
        item.classList.remove('active');
    });
    // Clicked category ko active bana do
    element.classList.add('active');

    // Heading change karo
    document.getElementById("category-title").innerText = element.innerText;

    // Items load karo
    const container = document.getElementById("food-items");
    container.innerHTML = "";

    // menuData se items insert karo
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

// Menu data (categories ke liye)
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

// Default category load karega jab page open hoga
document.addEventListener('DOMContentLoaded', () => {
    selectCategory(document.querySelector('#category-list .active'), 'chefs_signature');
});



// =================== PHOTO FILTERING ===================
// Gallery me photos filter karne ka kaam karta hai (All, Food, Ambience, etc.)
function filterPhotos(category) {
    // Buttons ka style update karo
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('btn-danger', 'active');
        btn.classList.add('btn-outline-secondary');
    });

    // Active button highlight karo
    const activeBtn = Array.from(document.querySelectorAll('.filter-btn')).find(btn =>
        btn.textContent.toLowerCase().includes(category)
    );
    if (activeBtn) {
        activeBtn.classList.add('btn-danger', 'active');
        activeBtn.classList.remove('btn-outline-secondary');
    }

    // Photos filter karo
    document.querySelectorAll('.photo-item').forEach(item => {
        item.style.display = (category === 'all' || item.classList.contains(category)) ? 'block' : 'none';
    });
}

// Page load hone par sab photos show karega
document.addEventListener('DOMContentLoaded', () => {
    filterPhotos('all');
});




// =================== QUANTITY MANAGEMENT (Cart Buttons) ===================
// Plus/Minus/Add button ka kaam
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('plus-btn')) {
        const quantityEl = e.target.closest('.d-flex').querySelector('.quantity');
        quantityEl.textContent = parseInt(quantityEl.textContent) + 1;
    }
    else if (e.target.classList.contains('minus-btn')) {
        const quantityEl = e.target.closest('.d-flex').querySelector('.quantity');
        const current = parseInt(quantityEl.textContent);
        if (current > 0) quantityEl.textContent = current - 1;
    }
    else if (e.target.classList.contains('add-btn')) {
        const quantity = parseInt(e.target.closest('.d-flex').querySelector('.quantity').textContent);
        if (quantity > 0) {
            alert(`Added ${quantity} items to cart!`);
        }
    }
});




// =================== SCROLL FUNCTIONS ===================
// Booking section par smooth scroll
function scrollToBooking() {
    document.querySelectorAll('.tab-section').forEach(sec => sec.classList.add('d-none'));
    document.getElementById('book-section').classList.remove('d-none');

    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => {
        if (btn.innerText.trim() === 'Book a Table') {
            btn.classList.add('active');
        }
    });

    setTimeout(() => {
        document.getElementById('book-section').scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

// Photos section par smooth scroll
function scrollToPhotos() {
    document.querySelectorAll('.tab-section').forEach(sec => sec.classList.add('d-none'));
    document.getElementById('photos-section').classList.remove('d-none');

    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => {
        if (btn.innerText.trim() === 'Photos') {
            btn.classList.add('active');
        }
    });

    setTimeout(() => {
        document.getElementById('photos-section').scrollIntoView({ behavior: 'smooth' });
    }, 100);
}




// =================== STAR RATING + REVIEW FORM ===================
// Star click logic
// document.addEventListener("DOMContentLoaded", function () {
//     document.querySelectorAll(".star-rating").forEach(function (group) {
//         const stars = group.querySelectorAll(".star");
//         const input = group.querySelector("input");

//         stars.forEach(function (star) {
//             star.addEventListener("click", function () {
//                 const value = this.dataset.value;
//                 input.value = value;

//                 stars.forEach(s => {
//                     s.classList.toggle("fa-star", s.dataset.value <= value);
//                     s.classList.toggle("fa-star-o", s.dataset.value > value);
//                 });
//             });
//         });
//     });

//     // Review form submit
//     document.getElementById("review-form").addEventListener("submit", function (e) {
//         e.preventDefault();
//         const form = e.target;
//         const formData = new FormData(form);

//         fetch("{% url 'restaurants:submit_review' restaurant.slug %}", {
//             method: "POST",
//             headers: {
//                 "X-Requested-With": "XMLHttpRequest",
//                 "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
//             },
//             body: formData,
//         })
//         .then((res) => res.json())
//         .then((data) => {
//             if (data.success) {
//                 form.reset();
//                 document.querySelectorAll(".star").forEach(star => {
//                     star.classList.remove("fa-star");
//                     star.classList.add("fa-star-o");
//                 });
//                 document.getElementById("submitted-reviews").insertAdjacentHTML("afterbegin", data.html);
//             } else {
//                 alert("Review failed. Try again.");
//             }
//         })
//         .catch((err) => {
//             console.error("Error:", err);
//         });
//     });
// });








