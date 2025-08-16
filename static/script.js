document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    let state = {
        userName: '',
        userPhone: '',
        movies: [],
        selectedMovie: null,
        selectedShowtime: null,
        selectedSeats: new Set(),
        bookedTickets: [] 
    };

    // --- PAGE ELEMENTS ---
    const loginPage = document.getElementById('login-page');
    const selectionPage = document.getElementById('selection-page');
    const bookingPage = document.getElementById('booking-page');
    const myTicketsPage = document.getElementById('my-tickets-page');

    const nameInput = document.getElementById('name');
    const sdtInput = document.getElementById('sdt');
    const loginBtn = document.getElementById('login-btn');

    const userInfoDisplay = document.getElementById('user-info');
    const logoutBtn = document.getElementById('logout-btn');
    const datePicker = document.getElementById('date-picker');
    const movieShowtimesContainer = document.getElementById('movie-showtimes-container');
    const myTicketsBtn = document.getElementById('my-tickets-btn');

    const backToSelectionBtn = document.getElementById('back-to-selection-btn');
    const ticketDisplayArea = document.getElementById('ticket-display-area');

    const backToSelectionFromBookingBtn = document.getElementById('back-to-selection-from-booking-btn');
    const movieTitleBooking = document.getElementById('movie-title-booking');
    const showtimeInfo = document.getElementById('showtime-info');
    const seatMap = document.getElementById('seat-map');
    const selectedSeatsDisplay = document.getElementById('selected-seats-display');
    const bookTicketBtn = document.getElementById('book-ticket-btn');

    // --- PAGE NAVIGATION ---
    function navigateTo(page) {
        loginPage.classList.add('hidden');
        selectionPage.classList.add('hidden');
        bookingPage.classList.add('hidden');
        myTicketsPage.classList.add('hidden');
        page.classList.remove('hidden');
    }

    // --- API CALLS ---
    async function fetchShowtimes(date) {
        try {
            const response = await fetch(`/api/showtimes?date=${date}`);
            if (!response.ok) throw new Error('Không thể tải suất chiếu');
            state.movies = await response.json();
            renderMovieShowtimes();
        } catch (error) {
            alert(error.message);
            movieShowtimesContainer.innerHTML = `<p style="text-align:center;">Không có suất chiếu cho ngày này.</p>`;
        }
    }

    // --- RENDER FUNCTIONS ---
    function renderMovieShowtimes() {
        movieShowtimesContainer.innerHTML = '';
        if (state.movies.length === 0) {
            movieShowtimesContainer.innerHTML = `<p style="text-align:center;">Không có suất chiếu cho ngày này.</p>`;
            return;
        }
        state.movies.forEach(movie => {
            const movieCard = document.createElement('div');
            movieCard.className = 'movie-card';
            movieCard.innerHTML = `
                <div class="movie-poster">
                    <img src="${movie.poster}" alt="${movie.ten}">
                </div>
                <div class="movie-details">
                    <h3>${movie.ten}</h3>
                    <p class="movie-description">${movie.mo_ta}</p>
                    <div class="showtimes">
                        ${movie.suat_chieu.map(st => 
                            `<button class="showtime-btn" data-movie-id="${movie.id}" data-time="${st.gio}">${st.gio}</button>`
                        ).join('')}
                    </div>
                </div>
            `;
            movieShowtimesContainer.appendChild(movieCard);
        });
    }

    function renderSeats() {
        seatMap.innerHTML = '';
        const ghe = state.selectedShowtime.ghe;
        const seats = Object.entries(ghe);
        const groupedSeats = seats.reduce((acc, [seatName, status]) => {
            const rowLetter = seatName.match(/[A-Z]+/)[0];
            if (!acc[rowLetter]) acc[rowLetter] = [];
            acc[rowLetter].push({ name: seatName, status });
            return acc;
        }, {});

        const sortedRows = Object.keys(groupedSeats).sort();
        sortedRows.forEach(rowLetter => {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'seat-row';
            const sortedSeatsInRow = groupedSeats[rowLetter].sort((a, b) => parseInt(a.name.match(/\d+/)[0]) - parseInt(b.name.match(/\d+/)[0]));
            sortedSeatsInRow.forEach(({ name, status }) => {
                const seatDiv = document.createElement('div');
                seatDiv.className = 'seat';
                seatDiv.innerText = name;
                if (status !== 'trong') {
                    seatDiv.classList.add('booked');
                } else {
                    seatDiv.classList.add('available');
                    if (state.selectedSeats.has(name)) seatDiv.classList.add('selected');
                }
                rowDiv.appendChild(seatDiv);
            });
            seatMap.appendChild(rowDiv);
        });
    }
    
   