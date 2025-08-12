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
    
    function renderMyTicketPage() {
        ticketDisplayArea.innerHTML = '';
        if (state.bookedTickets.length > 0) {
            state.bookedTickets.forEach(ticket => {
                const ticketHTML = `
                    <div class="ticket-card">
                        <div class="movie-poster">
                            <img src="${ticket.poster}" alt="Poster phim">
                        </div>
                        <div class="ticket-details">
                            <h3>${ticket.movieName}</h3>
                            <p><strong>Khách hàng:</strong> ${state.userName}</p>
                            <p><strong>Suất chiếu:</strong> ${ticket.showtime}</p>
                            <p><strong>Ghế đã đặt:</strong> ${ticket.seats.join(', ')}</p>
                        </div>
                        <div class="qr-code">
                            <div class="qr-code-placeholder"></div>
                            <p class="qr-code-text">Mã vé của bạn</p>
                        </div>
                    </div>
                `;
                ticketDisplayArea.insertAdjacentHTML('beforeend', ticketHTML);
            });
        } else {
            ticketDisplayArea.innerHTML = `<p style="text-align:center;">Bạn chưa đặt vé nào. Hãy chọn phim và đặt vé nhé!</p>`;
        }
    }

    function updateSelectedSeatsDisplay() {
        const sorted = Array.from(state.selectedSeats).sort();
        selectedSeatsDisplay.innerText = sorted.length > 0 ? sorted.join(', ') : 'Chưa chọn ghế';
    }


    // --- EVENT HANDLERS ---
    loginBtn.addEventListener('click', () => {
        const name = nameInput.value.trim();
        const phone = sdtInput.value.trim();
        if (!name || !phone) {
            alert('Vui lòng nhập đủ Tên và Số điện thoại.');
            return;
        }
        state.userName = name;
        state.userPhone = phone;
        
        // <<< THAY ĐỔI 2: Lưu thông tin đăng nhập vào Session Storage >>>
        sessionStorage.setItem('userName', state.userName);
        sessionStorage.setItem('userPhone', state.userPhone);
        
        // Tải vé từ Local Storage khi đăng nhập
        const userKey = `tickets_${state.userName}_${state.userPhone}`;
        const savedTickets = localStorage.getItem(userKey);
        if (savedTickets) {
            state.bookedTickets = JSON.parse(savedTickets);
        } else {
            state.bookedTickets = [];
        }

        userInfoDisplay.innerText = `Xin chào, ${state.userName}`;
        const today = new Date().toISOString().split('T')[0];
        datePicker.value = today;
        fetchShowtimes(today);
        navigateTo(selectionPage);
    });

    logoutBtn.addEventListener('click', () => {
        // <<< THAY ĐỔI 3: Xóa thông tin đăng nhập khỏi Session Storage >>>
        sessionStorage.removeItem('userName');
        sessionStorage.removeItem('userPhone');

        // Reset lại trạng thái
        state.userName = '';
        state.userPhone = '';
        nameInput.value = '';
        sdtInput.value = '';
        state.bookedTickets = [];
        navigateTo(loginPage);
    });

    datePicker.addEventListener('change', () => {
        fetchShowtimes(datePicker.value);
    });
    
    movieShowtimesContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('showtime-btn')) {
            const movieId = parseInt(e.target.dataset.movieId);
            const time = e.target.dataset.time;
            const date = datePicker.value;
            
            state.selectedMovie = state.movies.find(m => m.id === movieId);
            state.selectedShowtime = state.selectedMovie.suat_chieu.find(st => st.gio === time && st.ngay === date);
            
            movieTitleBooking.innerText = state.selectedMovie.ten;
            showtimeInfo.innerText = `Suất chiếu: ${state.selectedShowtime.gio} - Ngày: ${date}`;
            
            state.selectedSeats.clear();
            updateSelectedSeatsDisplay();
            renderSeats();
            navigateTo(bookingPage);
        }
    });
    
    backToSelectionFromBookingBtn.addEventListener('click', () => navigateTo(selectionPage));
    
    myTicketsBtn.addEventListener('click', () => {
        renderMyTicketPage();
        navigateTo(myTicketsPage);
    });
    
    backToSelectionBtn.addEventListener('click', () => navigateTo(selectionPage));


    seatMap.addEventListener('click', (e) => {
        if (e.target.classList.contains('available')) {
            const seatName = e.target.innerText;
            if (state.selectedSeats.has(seatName)) {
                state.selectedSeats.delete(seatName);
            } else {
                state.selectedSeats.add(seatName);
            }
            renderSeats();
            updateSelectedSeatsDisplay();
        }
    });

    bookTicketBtn.addEventListener('click', async () => {
        if (state.selectedSeats.size === 0) {
            alert('Vui lòng chọn ít nhất một ghế.');
            return;
        }
        const bookingData = {
            movie_id: state.selectedMovie.id,
            date: state.selectedShowtime.ngay,
            time: state.selectedShowtime.gio,
            seats: Array.from(state.selectedSeats),
            name: state.userName,
            sdt: state.userPhone
        };
        try {
            const response = await fetch('/api/book', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookingData)
            });
            const result = await response.json();
            
            if (result.status === 'success') {
                const newTicket = {
                    movieName: state.selectedMovie.ten,
                    poster: state.selectedMovie.poster,
                    showtime: `${state.selectedShowtime.gio} - ${state.selectedShowtime.ngay}`,
                    seats: Array.from(state.selectedSeats).sort()
                };
                state.bookedTickets.push(newTicket);

                const userKey = `tickets_${state.userName}_${state.userPhone}`;
                localStorage.setItem(userKey, JSON.stringify(state.bookedTickets));
                
                alert("Thành công: " + result.message);
                fetchShowtimes(datePicker.value);
                navigateTo(selectionPage);
                
            } else {
                alert("Thất bại: " + result.message);
            }
        } catch (error) {
            alert('Đã xảy ra lỗi khi đặt vé.');
            console.error("Booking Error:", error);
        }
    });

    // --- INITIALIZATION ---
    function initialize() {
        // <<< THAY ĐỔI 1: Kiểm tra Session Storage khi tải trang >>>
        const savedName = sessionStorage.getItem('userName');
        const savedPhone = sessionStorage.getItem('userPhone');

        if (savedName && savedPhone) {
            // Nếu có thông tin, tự động "đăng nhập"
            state.userName = savedName;
            state.userPhone = savedPhone;

            const userKey = `tickets_${state.userName}_${state.userPhone}`;
            const savedTickets = localStorage.getItem(userKey);
            if (savedTickets) {
                state.bookedTickets = JSON.parse(savedTickets);
            }

            userInfoDisplay.innerText = `Xin chào, ${state.userName}`;
            const today = new Date().toISOString().split('T')[0];
            datePicker.value = today;
            fetchShowtimes(today);
            navigateTo(selectionPage); // Chuyển thẳng vào trang chọn phim
        } else {
            // Nếu không có, hiển thị trang đăng nhập như cũ
            navigateTo(loginPage);
        }
    }

    initialize();
});