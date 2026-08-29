# app.py - Complete Flask App with Render Hosted API Integration

import os
import requests
import json
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sir_athelstan_secret_key_2025'

# ============================================
# 🔐 RENDER HOSTED API CONFIGURATION
# ============================================
API_BASE_URL = "https://book-db-1-ng4g.onrender.com"

# ============================================
# 📚 API FUNCTIONS
# ============================================

def api_get_books():
    """Get all books from Render API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/books", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data', {})
        return None
    except Exception as e:
        print(f"API Get error: {str(e)}")
        return None

def api_get_book(book_id):
    """Get single book from Render API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/book/{book_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data')
        return None
    except Exception as e:
        print(f"API Get Book error: {str(e)}")
        return None

def api_add_book(book_data):
    """Add book via Render API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/add",
            json=book_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"API Add error: {str(e)}")
        return None

def api_edit_book(book_id, book_data):
    """Edit book via Render API"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/edit/{book_id}",
            json=book_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"API Edit error: {str(e)}")
        return None

def api_delete_book(book_id):
    """Delete book via Render API"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/delete/{book_id}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"API Delete error: {str(e)}")
        return None

# Admin credentials
ADMIN_USERNAME = 'sirathelstan'
ADMIN_PASSWORD = '@UPLUS237c'

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# 🎨 HTML TEMPLATES
# ============================================

INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sir Athelstan · Adil Raza — Author & Philosopher</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        cream: '#f5f3ef',
                        ivory: '#fcfbf9',
                        ink: '#1c1c1c',
                        gold: '#a0743c',
                        stone: '#e3ded5'
                    },
                    fontFamily: {
                        serif: ['Cormorant Garamond', 'Times New Roman', 'serif'],
                        sans: ['Inter', 'Helvetica Neue', 'Segoe UI', 'sans-serif']
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-cream text-ink font-sans min-h-screen flex justify-center p-4 md:p-10">
    <div class="max-w-6xl w-full bg-ivory border border-stone p-8 md:p-12">

        <!-- HEADER -->
        <header class="border-b-2 border-ink pb-5 mb-6 flex flex-wrap items-end justify-between">
            <div>
                <h1 class="text-4xl md:text-5xl font-serif font-light tracking-widest">SIR ATHELSTAN</h1>
                <p class="text-sm text-gray-600 mt-2">Adil Raza · Siwan, Bihar · independent author</p>
            </div>
            <a href="/admin" class="text-xs text-gray-500 hover:text-gold transition">Admin Login →</a>
        </header>

        <!-- NAV -->
        <nav class="mb-8 border-b border-stone pb-4 flex flex-wrap gap-6">
            <a href="#about" class="text-xs uppercase tracking-wider font-medium hover:text-gold transition">About</a>
            <a href="#books" class="text-xs uppercase tracking-wider font-medium hover:text-gold transition">Books</a>
            <a href="#details" class="text-xs uppercase tracking-wider font-medium hover:text-gold transition">Details</a>
            <a href="#contact" class="text-xs uppercase tracking-wider font-medium hover:text-gold transition">Contact</a>
            <a href="#comments" class="text-xs uppercase tracking-wider font-medium hover:text-gold transition">Comments</a>
        </nav>

        <!-- ABOUT -->
        <section id="about" class="mb-12">
            <h2 class="text-2xl font-serif uppercase border-b border-stone pb-2 mb-6">About</h2>
            <div class="bg-cream border-l-4 border-gold p-6">
                <p class="mb-2"><strong>Sir Athelstan</strong> is the pen name of <strong>Adil Raza</strong>, an independent author and thinker from <strong>Siwan, Bihar, India</strong>.</p>
                <p>He writes on human psychology, cognition, and psychological sovereignty. His work blends philosophy, behavioural insight, and practical wisdom.</p>
                <span class="inline-block mt-3 bg-stone px-4 py-1 text-xs uppercase tracking-wide">📍 Siwan · Bihar · India</span>
            </div>
        </section>

        <!-- BOOKS - FIXED -->
        <section id="books" class="mb-12">
            <h2 class="text-2xl font-serif uppercase border-b border-stone pb-2 mb-6 flex items-baseline justify-between">
                Books
                <span class="text-xs text-gold uppercase tracking-widest font-sans">Available on Google Play</span>
            </h2>

            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6" id="bookContainer">
                {% if books and books.books %}
                    {% for book in books.books %}
                    <div class="book-card cursor-pointer group" data-book-id="{{ book.id }}">
                        <div class="aspect-[2/3] bg-ink overflow-hidden shadow-lg transition-transform group-hover:-translate-y-1 relative">
                            {% if book.cover_image %}
                                <img src="{{ book.cover_image }}" alt="{{ book.title }}" class="w-full h-full object-cover">
                            {% else %}
                                <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-black text-5xl text-gold font-serif">{{ book.title[0] if book.title else '?' }}</div>
                            {% endif %}
                            <div class="absolute top-2 right-2 w-6 h-6 bg-white bg-opacity-90 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity">↗</div>
                        </div>
                        <h4 class="mt-3 font-serif text-lg font-semibold">{{ book.title }}</h4>
                        <p class="text-xs text-gray-500 uppercase tracking-wide">{{ book.author|default('Sir Athelstan') }}</p>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="col-span-full text-center text-gray-500 py-12">No books found. Add your first book!</p>
                {% endif %}
            </div>
        </section>

        <!-- DETAILS -->
        <section id="details" class="mb-12">
            <h2 class="text-2xl font-serif uppercase border-b border-stone pb-2 mb-6">Author Details</h2>
            <div class="bg-cream border-l-4 border-gold p-6">
                <p><strong>Full name:</strong> {{ books.author_info.real_name|default('Adil Raza') if books and books.author_info else 'Adil Raza' }}</p>
                <p><strong>Pen name:</strong> {{ books.author_info.name|default('Sir Athelstan') if books and books.author_info else 'Sir Athelstan' }}</p>
                <p><strong>Location:</strong> {{ books.author_info.location|default('Siwan, Bihar, India') if books and books.author_info else 'Siwan, Bihar, India' }}</p>
                <p><strong>Profession:</strong> Independent author, philosophy writer</p>
                <p><strong>Focus:</strong> Psychology, cognition, sovereignty</p>
                <span class="inline-block mt-3 bg-stone px-4 py-1 text-xs uppercase tracking-wide">📚 {{ books.books|length if books and books.books else 0 }}+ books on Google Play</span>
            </div>
        </section>

        <!-- CONTACT -->
        <section id="contact" class="mb-12">
            <h2 class="text-2xl font-serif uppercase border-b border-stone pb-2 mb-6">Contact</h2>
            <div class="bg-cream border-l-4 border-gold p-6">
                <p><strong>Email:</strong> <a href="mailto:sirathelstan0@gmail.com" class="hover:text-gold transition">sirathelstan0@gmail.com</a></p>
                <p><strong>YouTube:</strong> <a href="https://youtube.com/@sirathelstanyt" target="_blank" class="hover:text-gold transition">@sirathelstanyt</a></p>
                <p><strong>Instagram:</strong> <a href="https://instagram.com/sirathelstan" target="_blank" class="hover:text-gold transition">@sirathelstan</a></p>
                <p><strong>Twitter / X:</strong> <a href="https://twitter.com/Athelstx" target="_blank" class="hover:text-gold transition">@Athelstx</a></p>
            </div>
        </section>

        <!-- COMMENTS -->
        <section id="comments" class="mb-12">
            <h2 class="text-2xl font-serif uppercase border-b border-stone pb-2 mb-6">Leave a Comment</h2>
            <div class="bg-cream border border-stone p-8 max-w-2xl">
                <form id="commentForm">
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Full name</label>
                    <input type="text" id="commentName" required class="w-full p-3 border border-stone mb-4 focus:border-gold outline-none" />
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Subject</label>
                    <input type="text" id="commentSubject" required class="w-full p-3 border border-stone mb-4 focus:border-gold outline-none" />
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Email address</label>
                    <input type="email" id="commentEmail" required class="w-full p-3 border border-stone mb-4 focus:border-gold outline-none" />
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Your comment</label>
                    <textarea id="commentMessage" rows="5" required class="w-full p-3 border border-stone mb-4 focus:border-gold outline-none"></textarea>
                    <div id="formStatus" class="text-sm mb-4"></div>
                    <button type="submit" class="bg-ink text-ivory px-8 py-3 text-xs uppercase tracking-widest hover:bg-gold transition">Submit Comment</button>
                </form>
            </div>
        </section>

        <!-- FOOTER -->
        <footer class="mt-12 border-t border-stone pt-8 flex flex-wrap justify-between text-sm">
            <div class="flex gap-6">
                <a href="#about" class="text-xs uppercase tracking-wide hover:text-gold transition">About</a>
                <a href="#books" class="text-xs uppercase tracking-wide hover:text-gold transition">Books</a>
                <a href="#contact" class="text-xs uppercase tracking-wide hover:text-gold transition">Contact</a>
            </div>
            <p class="mt-4">© 2026 Sir Athelstan (Adil Raza) · Siwan, Bihar · India</p>
        </footer>

    </div>

    <!-- BOOK MODAL - FIXED -->
    <div id="bookModal" class="hidden fixed inset-0 bg-black bg-opacity-70 z-50 flex items-center justify-center p-4">
        <div class="bg-ivory border border-stone max-w-2xl w-full max-h-[90vh] overflow-y-auto flex relative">
            <button id="modalClose" class="absolute top-4 right-4 w-8 h-8 border border-stone bg-ivory flex items-center justify-center hover:bg-ink hover:text-ivory transition z-10">✕</button>
            <div class="w-2/5 bg-ink" id="modalCover"></div>
            <div class="flex-1 p-8">
                <p class="text-xs text-gold uppercase tracking-widest mb-2">{{ books.author_info.name|default('Sir Athelstan') if books and books.author_info else 'Sir Athelstan' }}</p>
                <h3 class="text-3xl font-serif mb-2" id="modalTitle"></h3>
                <p class="text-sm italic text-gray-600 mb-4" id="modalMeta"></p>
                <p class="text-sm text-gray-800 mb-6" id="modalDesc"></p>
                <a href="#" target="_blank" id="modalPurchase" class="inline-block bg-ink text-ivory px-6 py-3 text-xs uppercase tracking-widest hover:bg-gold transition">Purchase on Google Play ↗</a>
            </div>
        </div>
    </div>

    <script>
        const bookData = {{ books.books|tojson if books and books.books else [] }};

        function openModal(bookId) {
            const book = bookData.find(b => b.id === bookId);
            if (!book) return;

            document.getElementById('modalCover').innerHTML = book.cover_image ?
                `<img src="${book.cover_image}" alt="${book.title}" class="w-full h-full object-cover">` :
                `<div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-black text-6xl text-gold font-serif">${book.title ? book.title[0] : '?'}</div>`;

            document.getElementById('modalTitle').textContent = book.title || 'Untitled';
            document.getElementById('modalMeta').textContent = `${book.author || 'Sir Athelstan'} · ${book.published_year || ''}`;
            document.getElementById('modalDesc').textContent = book.description || '';
            document.getElementById('modalPurchase').href = book.google_play_link || '#';

            document.getElementById('bookModal').classList.remove('hidden');
        }

        document.querySelectorAll('.book-card').forEach(card => {
            card.addEventListener('click', function() {
                const bookId = parseInt(this.dataset.bookId);
                openModal(bookId);
            });
        });

        document.getElementById('modalClose').addEventListener('click', () => {
            document.getElementById('bookModal').classList.add('hidden');
        });

        document.getElementById('bookModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                document.getElementById('bookModal').classList.add('hidden');
            }
        });

        document.getElementById('commentForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const name = document.getElementById('commentName').value.trim();
            const subject = document.getElementById('commentSubject').value.trim();
            const email = document.getElementById('commentEmail').value.trim();
            const comment = document.getElementById('commentMessage').value.trim();

            if (!name || !subject || !email || !comment) {
                document.getElementById('formStatus').innerHTML = '<span class="text-red-600">⚠️ All fields are required.</span>';
                return;
            }

            document.getElementById('formStatus').innerHTML = '<span class="text-green-600">✓ Thank you! Your comment has been submitted.</span>';
            e.target.reset();
            setTimeout(() => {
                document.getElementById('formStatus').innerHTML = '';
            }, 3000);
        });

        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const id = this.getAttribute('href');
                if (id === '#') return;
                const target = document.querySelector(id);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    </script>
</body>
</html>
'''

ADMIN_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login · Sir Athelstan</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-cream text-ink font-sans min-h-screen flex items-center justify-center p-4">
    <div class="bg-ivory border border-stone p-8 max-w-md w-full shadow-lg">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-serif font-light tracking-widest">SIR ATHELSTAN</h1>
            <p class="text-sm text-gray-600 mt-2">Administrator Login</p>
        </div>
        <form method="POST" class="space-y-6">
            <div>
                <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Username</label>
                <input type="text" name="username" required class="w-full p-3 border border-stone focus:border-gold outline-none transition">
            </div>
            <div>
                <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Password</label>
                <input type="password" name="password" required class="w-full p-3 border border-stone focus:border-gold outline-none transition">
            </div>
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="text-red-600 text-sm bg-red-50 p-3 border border-red-200">{{ messages[0] }}</div>
                {% endif %}
            {% endwith %}
            <button type="submit" class="w-full bg-ink text-ivory py-3 text-xs uppercase tracking-widest hover:bg-gold transition">Login</button>
        </form>
    </div>
</body>
</html>
'''

ADMIN_PANEL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel · Sir Athelstan</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .slide-in { animation: slideIn 0.3s ease-out; }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .modal-overlay { background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); }
    </style>
</head>
<body class="bg-cream text-ink font-sans p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <div class="bg-ivory border border-stone p-6 mb-8 flex items-center justify-between flex-wrap gap-4">
            <div>
                <h1 class="text-2xl font-serif font-light tracking-widest">Admin Panel</h1>
                <p class="text-sm text-gray-600">Manage books · Sir Athelstan</p>
            </div>
            <div class="flex gap-4">
                <a href="/" target="_blank" class="text-xs uppercase tracking-wider hover:text-gold transition">View Site</a>
                <a href="/admin/logout" class="text-xs uppercase tracking-wider text-red-600 hover:text-red-800 transition">Logout</a>
            </div>
        </div>

        <div class="mb-8">
            <button onclick="openAddModal()" class="bg-ink text-ivory px-8 py-3 text-xs uppercase tracking-widest hover:bg-gold transition shadow-lg">+ Add New Book</button>
        </div>

        <div class="bg-ivory border border-stone p-6">
            <h2 class="text-xl font-serif mb-4">All Books</h2>
            <div class="space-y-4" id="booksList">
                {% if books and books.books %}
                    {% for book in books.books %}
                    <div class="border-b border-stone pb-4 flex items-center justify-between flex-wrap gap-4 book-item" data-id="{{ book.id }}">
                        <div class="flex-1 min-w-[200px]">
                            <h3 class="font-serif text-lg">{{ book.title }}</h3>
                            <p class="text-sm text-gray-600">{{ book.author|default('Sir Athelstan') }} · {{ book.published_year|default('') }}</p>
                            <p class="text-xs text-gray-500 truncate max-w-md">{{ book.google_play_link }}</p>
                        </div>
                        <div class="flex gap-3">
                            <button onclick="openEditModal({{ book.id }})" class="text-xs uppercase tracking-wide text-gold hover:text-ink transition">Edit</button>
                            <button onclick="deleteBook({{ book.id }})" class="text-xs uppercase tracking-wide text-red-600 hover:text-red-800 transition">Delete</button>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-center text-gray-500 py-8">No books found. Add your first book!</p>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Add/Edit Modal -->
    <div id="bookModal" class="hidden fixed inset-0 modal-overlay flex items-center justify-center p-4 z-50">
        <div class="bg-ivory border border-stone p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto slide-in">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-serif" id="modalTitle">Add Book</h2>
                <button onclick="closeModal()" class="w-8 h-8 border border-stone hover:bg-ink hover:text-ivory transition">✕</button>
            </div>
            <form id="bookForm" class="space-y-4">
                <input type="hidden" id="bookId" value="">
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Book Title *</label>
                    <input type="text" id="bookTitle" name="title" required class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Author</label>
                    <input type="text" id="bookAuthor" name="author" value="Sir Athelstan" class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Genre</label>
                    <input type="text" id="bookGenre" name="genre" class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Published Year</label>
                    <input type="number" id="bookYear" name="published_year" value="2025" class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Google Play Link *</label>
                    <input type="url" id="bookLink" name="google_play_link" required class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Cover Image URL</label>
                    <input type="url" id="bookCover" name="cover_image" class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Description</label>
                    <textarea id="bookDesc" name="description" rows="4" class="w-full p-3 border border-stone focus:border-gold outline-none transition"></textarea>
                </div>
                <div id="formStatus" class="text-sm"></div>
                <button type="submit" class="bg-ink text-ivory px-8 py-3 text-xs uppercase tracking-widest hover:bg-gold transition w-full">Save Book</button>
            </form>
        </div>
    </div>

    <script>
        function openAddModal() {
            document.getElementById('modalTitle').textContent = 'Add New Book';
            document.getElementById('bookForm').reset();
            document.getElementById('bookId').value = '';
            document.getElementById('formStatus').innerHTML = '';
            document.getElementById('bookModal').classList.remove('hidden');
        }

        function openEditModal(bookId) {
            fetch('/api/books')
                .then(res => res.json())
                .then(data => {
                    const books = data.data ? data.data.books : [];
                    const book = books.find(b => b.id === bookId);
                    if (book) {
                        document.getElementById('modalTitle').textContent = 'Edit Book';
                        document.getElementById('bookId').value = book.id;
                        document.getElementById('bookTitle').value = book.title || '';
                        document.getElementById('bookAuthor').value = book.author || 'Sir Athelstan';
                        document.getElementById('bookGenre').value = book.genre || '';
                        document.getElementById('bookYear').value = book.published_year || 2025;
                        document.getElementById('bookLink').value = book.google_play_link || '';
                        document.getElementById('bookCover').value = book.cover_image || '';
                        document.getElementById('bookDesc').value = book.description || '';
                        document.getElementById('formStatus').innerHTML = '';
                        document.getElementById('bookModal').classList.remove('hidden');
                    }
                })
                .catch(error => {
                    console.error('Error loading book:', error);
                    document.getElementById('formStatus').innerHTML = '<span class="text-red-600">⚠️ Could not load book data.</span>';
                });
        }

        function closeModal() {
            document.getElementById('bookModal').classList.add('hidden');
        }

        document.getElementById('bookForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const bookId = document.getElementById('bookId').value;
            const isEdit = bookId !== '';
            const url = isEdit ? `/admin/edit/${bookId}` : '/admin/add';
            const formData = new FormData(this);

            try {
                const response = await fetch(url, { method: 'POST', body: formData });
                const result = await response.json();

                if (result.success) {
                    document.getElementById('formStatus').innerHTML = `<span class="text-green-600">✓ ${result.message}</span>`;
                    setTimeout(() => { location.reload(); }, 1000);
                } else {
                    document.getElementById('formStatus').innerHTML = `<span class="text-red-600">⚠️ Error: ${result.message}</span>`;
                }
            } catch (error) {
                console.error('Save error:', error);
                document.getElementById('formStatus').innerHTML = '<span class="text-red-600">⚠️ An error occurred</span>';
            }
        });

        async function deleteBook(bookId) {
            if (!confirm('Are you sure you want to delete this book?')) return;
            try {
                const response = await fetch(`/admin/delete/${bookId}`, { method: 'DELETE' });
                const result = await response.json();
                if (result.success) {
                    alert('Book deleted successfully!');
                    location.reload();
                } else {
                    alert('Error deleting book');
                }
            } catch (error) {
                console.error('Delete error:', error);
                alert('An error occurred');
            }
        }

        document.getElementById('bookModal').addEventListener('click', function(e) {
            if (e.target === this) { closeModal(); }
        });
    </script>
</body>
</html>
'''

# ============================================
# 🚀 FLASK ROUTES
# ============================================

@app.route('/')
def index():
    """Home page - Show all books from Render API"""
    books = api_get_books()
    if not books:
        books = {"books": [], "total_books": 0, "author_info": {"name": "Sir Athelstan", "real_name": "Adil Raza", "location": "Siwan, Bihar, India", "genre": "Philosophy / Psychology"}}
    return render_template_string(INDEX_TEMPLATE, books=books)

@app.route('/api/books')
def api_books():
    """Proxy: Get all books from Render API"""
    books = api_get_books()
    if books:
        return jsonify({
            "success": True,
            "data": books,
            "total": books.get('total_books', 0)
        })
    return jsonify({"success": False, "error": "Failed to fetch data"}), 500

@app.route('/api/book/<int:book_id>')
def api_book(book_id):
    """Proxy: Get single book from Render API"""
    book = api_get_book(book_id)
    if book:
        return jsonify({"success": True, "data": book})
    return jsonify({"success": False, "error": "Book not found"}), 404

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid username or password')
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/admin/panel')
def admin_panel():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    books = api_get_books()
    if not books:
        books = {"books": [], "total_books": 0}
    return render_template_string(ADMIN_PANEL_TEMPLATE, books=books)

@app.route('/admin/add', methods=['POST'])
def add_book():
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    book_data = {
        "title": request.form.get('title'),
        "author": request.form.get('author', 'Sir Athelstan'),
        "cover_image": request.form.get('cover_image', ''),
        "google_play_link": request.form.get('google_play_link'),
        "description": request.form.get('description', ''),
        "published_year": int(request.form.get('published_year', 2025)),
        "genre": request.form.get('genre', '')
    }
    
    result = api_add_book(book_data)
    if result and result.get('success'):
        return jsonify({"success": True, "message": "Book added successfully!"})
    return jsonify({"success": False, "message": "Failed to add book"}), 500

@app.route('/admin/edit/<int:book_id>', methods=['POST'])
def edit_book(book_id):
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    book_data = {
        "title": request.form.get('title'),
        "author": request.form.get('author', 'Sir Athelstan'),
        "cover_image": request.form.get('cover_image', ''),
        "google_play_link": request.form.get('google_play_link'),
        "description": request.form.get('description', ''),
        "published_year": int(request.form.get('published_year', 2025)),
        "genre": request.form.get('genre', '')
    }
    
    result = api_edit_book(book_id, book_data)
    if result and result.get('success'):
        return jsonify({"success": True, "message": "Book updated successfully!"})
    return jsonify({"success": False, "message": "Failed to update book"}), 500

@app.route('/admin/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    result = api_delete_book(book_id)
    if result and result.get('success'):
        return jsonify({"success": True, "message": "Book deleted successfully!"})
    return jsonify({"success": False, "message": "Failed to delete book"}), 500

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ============================================
# 🚀 RUN APP
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
