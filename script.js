// Globalne zmienne
let allEvents = [];
let filteredEvents = [];
let selectedCategory = 'Wszystkie';
let selectedFilter = 'Wszystkie';
let searchTerm = '';

// Kategorie i filtry
const categories = ['Wszystkie', 'HR', 'AI w HR', 'HR Tech', 'Konkursy', 'Wellbeing'];
const filters = ['Wszystkie', 'Nowe', 'Pilne deadline\'y', 'Aktywne zgłoszenia', 'Darmowe', 'Płatne', 'Możliwości sponsoringu'];

// Inicjalizacja aplikacji
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        showLoading(true);
        await loadEvents();
        setupEventListeners();
        renderFilters();
        updateStats();
        renderEvents();
        showLoading(false);
    } catch (error) {
        console.error('Błąd inicjalizacji:', error);
        showError(true);
        showLoading(false);
    }
}

// Ładowanie danych
async function loadEvents() {
    try {
        const response = await fetch('../data/events.json');
        if (!response.ok) {
            throw new Error('Nie można załadować danych');
        }
        const data = await response.json();
        allEvents = data.events || [];
        filteredEvents = [...allEvents];
        
        // Aktualizacja daty ostatniej aktualizacji
        if (data.lastUpdate) {
            const lastUpdate = new Date(data.lastUpdate);
            document.getElementById('lastUpdate').textContent = 
                `Ostatnia aktualizacja: ${lastUpdate.toLocaleDateString('pl-PL')} ${lastUpdate.toLocaleTimeString('pl-PL', {hour: '2-digit', minute: '2-digit'})}`;
        }
        
        // Sortowanie wydarzeń chronologicznie
        allEvents.sort((a, b) => new Date(a.date) - new Date(b.date));
        filteredEvents = [...allEvents];
        
    } catch (error) {
        console.error('Błąd ładowania wydarzeń:', error);
        throw error;
    }
}

// Event listeners
function setupEventListeners() {
    // Wyszukiwanie
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function(e) {
        searchTerm = e.target.value.toLowerCase();
        filterEvents();
    });
    
    // Przycisk "Zobacz wszystkie nowe wydarzenia"
    document.getElementById('showAllNewBtn').addEventListener('click', function() {
        selectedFilter = 'Nowe';
        updateFilterButtons();
        filterEvents();
        document.querySelector('.events-section').scrollIntoView({ behavior: 'smooth' });
    });
}

// Renderowanie filtrów
function renderFilters() {
    // Kategorie
    const categoryFilters = document.getElementById('categoryFilters');
    categoryFilters.innerHTML = categories.map(category => 
        `<button class="filter-btn ${category === selectedCategory ? 'active' : ''}" 
                 onclick="selectCategory('${category}')">${category}</button>`
    ).join('');
    
    // Filtry
    const typeFilters = document.getElementById('typeFilters');
    typeFilters.innerHTML = filters.map(filter => 
        `<button class="filter-btn ${filter === selectedFilter ? 'active' : ''}" 
                 onclick="selectFilter('${filter}')">${filter}</button>`
    ).join('');
}

// Wybór kategorii
function selectCategory(category) {
    selectedCategory = category;
    updateFilterButtons();
    filterEvents();
}

// Wybór filtru
function selectFilter(filter) {
    selectedFilter = filter;
    updateFilterButtons();
    filterEvents();
}

// Aktualizacja przycisków filtrów
function updateFilterButtons() {
    // Kategorie
    document.querySelectorAll('#categoryFilters .filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.textContent === selectedCategory);
    });
    
    // Filtry
    document.querySelectorAll('#typeFilters .filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.textContent === selectedFilter);
    });
}

// Filtrowanie wydarzeń
function filterEvents() {
    filteredEvents = allEvents.filter(event => {
        // Filtr wyszukiwania
        const matchesSearch = !searchTerm || 
            event.title.toLowerCase().includes(searchTerm) ||
            event.description.toLowerCase().includes(searchTerm) ||
            event.tags.some(tag => tag.toLowerCase().includes(searchTerm)) ||
            event.location.toLowerCase().includes(searchTerm);
        
        // Filtr kategorii
        const matchesCategory = selectedCategory === 'Wszystkie' || event.category === selectedCategory;
        
        // Filtr typu
        const matchesFilter = selectedFilter === 'Wszystkie' ||
            (selectedFilter === 'Nowe' && event.isNew) ||
            (selectedFilter === 'Pilne deadline\'y' && isUrgentDeadline(event)) ||
            (selectedFilter === 'Darmowe' && event.pricing === 'Darmowy') ||
            (selectedFilter === 'Płatne' && event.pricing !== 'Darmowy' && event.pricing !== 'Do sprawdzenia');
        
        return matchesSearch && matchesCategory && matchesFilter;
    });
    
    renderEvents();
    updateEventsCount();
}

// Sprawdzenie czy deadline jest pilny (mniej niż 7 dni)
function isUrgentDeadline(event) {
    if (!event.hasDeadline || !event.deadline) return false;
    
    const deadlineDate = new Date(event.deadline);
    const today = new Date();
    const diffTime = deadlineDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays <= 7 && diffDays >= 0;
}

// Obliczanie dni do deadline
function getDaysToDeadline(deadline) {
    const deadlineDate = new Date(deadline);
    const today = new Date();
    const diffTime = deadlineDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
}

// Aktualizacja statystyk
function updateStats() {
    const newEvents = allEvents.filter(e => e.isNew);
    const eventsWithDeadlines = allEvents.filter(e => e.hasDeadline);
    const urgentEvents = allEvents.filter(e => isUrgentDeadline(e));
    
    document.getElementById('totalEvents').textContent = allEvents.length;
    document.getElementById('newEventsStats').textContent = newEvents.length;
    document.getElementById('deadlineEvents').textContent = eventsWithDeadlines.length;
    document.getElementById('urgentEvents').textContent = urgentEvents.length;
    
    // Aktualizacja sekcji najnowszych dodatków
    document.getElementById('newEventsCount').textContent = `${newEvents.length} nowych wydarzeń`;
    document.getElementById('newEventsTotal').textContent = newEvents.length;
    
    renderNewEvents(newEvents.slice(0, 3));
}

// Renderowanie nowych wydarzeń
function renderNewEvents(newEvents) {
    const grid = document.getElementById('newEventsGrid');
    grid.innerHTML = newEvents.map(event => `
        <div class="new-event-card">
            <div class="event-badges">
                <span class="event-badge category">${event.category}</span>
                ${event.isNew ? '<span class="event-badge new">NOWE</span>' : ''}
            </div>
            <div class="event-title">${event.title}</div>
            <div class="event-meta">
                <span><i class="fas fa-calendar"></i> ${formatDate(event.date)}</span>
                <span><i class="fas fa-map-marker-alt"></i> ${event.location}</span>
            </div>
            <button class="btn btn-outline" onclick="scrollToEvent('${event.id}')">
                Zobacz szczegóły →
            </button>
        </div>
    `).join('');
}

// Renderowanie wszystkich wydarzeń
function renderEvents() {
    const eventsList = document.getElementById('eventsList');
    eventsList.innerHTML = filteredEvents.map(event => `
        <div class="event-card" id="event-${event.id}">
            <div class="event-header">
                <div class="event-badges">
                    <span class="event-badge category">${event.category}</span>
                    <span class="event-badge">${event.status}</span>
                    ${event.isNew ? '<span class="event-badge new">NOWE</span>' : ''}
                </div>
                <div class="event-title">${event.title}</div>
                <div class="event-meta">
                    <span><i class="fas fa-calendar"></i> ${formatDate(event.date)}</span>
                    <span><i class="fas fa-map-marker-alt"></i> ${event.location}</span>
                </div>
            </div>
            
            <div class="event-description">${event.description}</div>
            
            <div class="event-tags">
                ${event.tags.map(tag => `<span class="event-tag">${tag}</span>`).join('')}
            </div>
            
            ${event.hasDeadline ? `
                <div class="deadline-info">
                    <h4>Deadline zgłoszeń</h4>
                    <div class="deadline-details">
                        <span><strong>Termin:</strong> ${formatDate(event.deadline)}</span>
                        <span><strong>Status:</strong> ${getDaysToDeadline(event.deadline)} dni pozostało</span>
                    </div>
                </div>
            ` : ''}
            
            <div class="pricing-info">
                <h4>Cennik</h4>
                <div class="pricing-details">
                    <div><strong>Uczestnictwo:</strong> ${event.pricing}</div>
                    ${event.regularPrice ? `<div class="text-muted">Cena regularna: ${event.regularPrice}</div>` : ''}
                    ${event.earlyBird ? `<div class="early-bird"><strong>Early Bird:</strong> ${event.earlyBird}</div>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

// Aktualizacja liczby wydarzeń
function updateEventsCount() {
    document.getElementById('eventsCount').textContent = `${filteredEvents.length} wydarzeń`;
}

// Formatowanie daty
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pl-PL', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
}

// Przewijanie do wydarzenia
function scrollToEvent(eventId) {
    const element = document.getElementById(`event-${eventId}`);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        element.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.5)';
        setTimeout(() => {
            element.style.boxShadow = '';
        }, 2000);
    }
}

// Pokazywanie/ukrywanie loading
function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'block' : 'none';
}

// Pokazywanie/ukrywanie błędu
function showError(show) {
    const error = document.getElementById('error');
    error.style.display = show ? 'block' : 'none';
}

// Eksport funkcji dla użycia w HTML
window.selectCategory = selectCategory;
window.selectFilter = selectFilter;
window.scrollToEvent = scrollToEvent;
