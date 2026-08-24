from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash, session
from functools import wraps
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sir_athelstan_secret_key_2025'

# Admin credentials
ADMIN_USERNAME = 'sirathelstan'
ADMIN_PASSWORD = '@UPLUS237c'

# Database setup
def init_db():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    
    # Create books table
    c.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        meta TEXT,
        link TEXT NOT NULL,
        desc TEXT,
        cover TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insert default books if table is empty
    c.execute("SELECT COUNT(*) FROM books")
    if c.fetchone()[0] == 0:
        default_books = [
            ('The Unseen Ledger', 'A Field Guide to Reclaiming Your Psychological Sovereignty · 2026', 'https://play.google.com/store/books/details?id=FI3-EQAAQBAJ', 'Explores the hidden architecture of self-deception, bias, and cognitive sovereignty.', ''),
            ('Who Is God', 'Sir Athelstan · 2026', 'https://play.google.com/store/books/details?id=A-r_EQAAQBAJ', 'A philosophical inquiry into the nature of belief, divinity, and the human mind.', ''),
            ('Everyone Is a Slave', 'Sir Athelstan · 2026', 'https://play.google.com/store/books/details?id=jRwAEgAAQBAJ', 'On psychological servitude, autonomy, and the invisible chains of modern life.', ''),
            ('Publish Your Book in 2 Days', 'Sir Athelstan · 2026', 'https://play.google.com/store/books/details?id=Fh0AEgAAQBAJ', 'A practical guide for first-time authors — from manuscript to publication.', ''),
            ('Knowledge Is a Curse', 'What Remains When the Comforting Illusions Disappear · 2026', 'https://play.google.com/store/books/details?id=ExwAEgAAQBAJ', 'Reflections on relationships, selfhood, and the other.', '')
        ]
        c.executemany("INSERT INTO books (name, meta, link, desc, cover) VALUES (?, ?, ?, ?, ?)", default_books)
    
    conn.commit()
    conn.close()


# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# HTML Templates
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sir Athelstan · Adil Raza — Author & Philosopher</title>
    <meta name="description" content="Sir Athelstan (Adil Raza) – author from Siwan, Bihar. Books on psychology, sovereignty, philosophy." />
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

        <!-- BOOKS -->
        <section id="books" class="mb-12">
            <h2 class="text-2xl font-serif uppercase border-b border-stone pb-2 mb-6 flex items-baseline justify-between">
                Books
                <span class="text-xs text-gold uppercase tracking-widest font-sans">Available on Google Play</span>
            </h2>

            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6" id="bookContainer">
                {% for book in books %}
                <div class="book-card cursor-pointer group" data-book-id="{{ book[0] }}">
                    <div class="aspect-[2/3] bg-ink overflow-hidden shadow-lg transition-transform group-hover:-translate-y-1 relative">
                        {% if book[5] %}
                            <img src="{{ book[5] }}" alt="{{ book[1] }}" class="w-full h-full object-cover">
                        {% else %}
                            <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-black text-5xl text-gold font-serif">{{ book[1][0] }}</div>
                        {% endif %}

                        <div class="absolute top-2 right-2 w-6 h-6 bg-white bg-opacity-90 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity">↗</div>
                    </div>

                    <h4 class="mt-3 font-serif text-lg font-semibold">{{ book[1] }}</h4>
                    <p class="text-xs text-gray-500 uppercase tracking-wide">Sir Athelstan</p>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- DETAILS -->
        <section id="details" class="mb-12">
            <h2 class="text-2xl font-serif uppercase border-b border-stone pb-2 mb-6">Author Details</h2>
            <div class="bg-cream border-l-4 border-gold p-6">
                <p><strong>Full name:</strong> Adil Raza</p>
                <p><strong>Pen name:</strong> Sir Athelstan</p>
                <p><strong>Location:</strong> Siwan, Bihar, India</p>
                <p><strong>Profession:</strong> Independent author, philosophy writer</p>
                <p><strong>Focus:</strong> Psychology, cognition, sovereignty</p>
                <span class="inline-block mt-3 bg-stone px-4 py-1 text-xs uppercase tracking-wide">📚 5+ books on Google Play</span>
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

                    <button type="submit" class="bg-ink text-ivory px-8 py-3 text-xs uppercase tracking-widest hover:bg-gold transition">
                        Submit Comment
                    </button>
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

    <!-- BOOK MODAL -->
    <div id="bookModal" class="hidden fixed inset-0 bg-black bg-opacity-70 z-50 flex items-center justify-center p-4">
        <div class="bg-ivory border border-stone max-w-2xl w-full max-h-[90vh] overflow-y-auto flex relative">

            <button id="modalClose" class="absolute top-4 right-4 w-8 h-8 border border-stone bg-ivory flex items-center justify-center hover:bg-ink hover:text-ivory transition z-10">✕</button>

            <div class="w-2/5 bg-ink" id="modalCover"></div>

            <div class="flex-1 p-8">
                <p class="text-xs text-gold uppercase tracking-widest mb-2">Sir Athelstan</p>
                <h3 class="text-3xl font-serif mb-2" id="modalTitle"></h3>
                <p class="text-sm italic text-gray-600 mb-4" id="modalMeta"></p>
                <p class="text-sm text-gray-800 mb-6" id="modalDesc"></p>

                <a href="#" target="_blank" id="modalPurchase" class="inline-block bg-ink text-ivory px-6 py-3 text-xs uppercase tracking-widest hover:bg-gold transition">
                    Purchase on Google Play ↗
                </a>
            </div>
        </div>
    </div>

    <script>
        // Modal functions
        const bookData = {{ books|tojson }};

        function openModal(bookId) {
            const book = bookData.find(b => b[0] === bookId);
            if (!book) return;

            document.getElementById('modalCover').innerHTML = book[5] ?
                `<img src="${book[5]}" alt="${book[1]}" class="w-full h-full object-cover">` :
                `<div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-black text-6xl text-gold font-serif">${book[1][0]}</div>`;

            document.getElementById('modalTitle').textContent = book[1];
            document.getElementById('modalMeta').textContent = book[2] || '';
            document.getElementById('modalDesc').textContent = book[4] || '';
            document.getElementById('modalPurchase').href = book[3];

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

        // Comment form
        document.getElementById('commentForm').addEventListener('submit', (e) => {
            e.preventDefault();

            const name = document.getElementById('commentName').value.trim();
            const subject = document.getElementById('commentSubject').value.trim();
            const email = document.getElementById('commentEmail').value.trim();
            const comment = document.getElementById('commentMessage').value.trim();

            if (!name || !subject || !email || !comment) {
                document.getElementById('formStatus').innerHTML =
                    '<span class="text-red-600">⚠️ All fields are required.</span>';
                return;
            }

            document.getElementById('formStatus').innerHTML =
                '<span class="text-green-600">✓ Thank you! Your comment has been submitted.</span>';

            e.target.reset();

            setTimeout(() => {
                document.getElementById('formStatus').innerHTML = '';
            }, 3000);
        });

        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const id = this.getAttribute('href');

                if (id === '#') return;

                const target = document.querySelector(id);

                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
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

                <input type="text"
                       name="username"
                       required
                       class="w-full p-3 border border-stone focus:border-gold outline-none transition">
            </div>

            <div>
                <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">Password</label>

                <input type="password"
                       name="password"
                       required
                       class="w-full p-3 border border-stone focus:border-gold outline-none transition">
            </div>

            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="text-red-600 text-sm bg-red-50 p-3 border border-red-200">
                        {{ messages[0] }}
                    </div>
                {% endif %}
            {% endwith %}

            <button type="submit"
                    class="w-full bg-ink text-ivory py-3 text-xs uppercase tracking-widest hover:bg-gold transition">
                Login
            </button>

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
        .slide-in {
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .modal-overlay {
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(4px);
        }
    </style>
</head>

<body class="bg-cream text-ink font-sans p-4 md:p-8">

    <div class="max-w-7xl mx-auto">

        <!-- Header -->
        <div class="bg-ivory border border-stone p-6 mb-8 flex items-center justify-between flex-wrap gap-4">

            <div>
                <h1 class="text-2xl font-serif font-light tracking-widest">Admin Panel</h1>
                <p class="text-sm text-gray-600">Manage books · Sir Athelstan</p>
            </div>

            <div class="flex gap-4">
                <a href="/" target="_blank" class="text-xs uppercase tracking-wider hover:text-gold transition">
                    View Site
                </a>

                <a href="/admin/logout" class="text-xs uppercase tracking-wider text-red-600 hover:text-red-800 transition">
                    Logout
                </a>
            </div>

        </div>

        <!-- Add Book Button -->
        <div class="mb-8">

            <button onclick="openAddModal()"
                    class="bg-ink text-ivory px-8 py-3 text-xs uppercase tracking-widest hover:bg-gold transition shadow-lg">
                + Add New Book
            </button>

        </div>

        <!-- Books List -->
        <div class="bg-ivory border border-stone p-6">

            <h2 class="text-xl font-serif mb-4">All Books</h2>

            <div class="space-y-4" id="booksList">

                {% for book in books %}

                <div class="border-b border-stone pb-4 flex items-center justify-between flex-wrap gap-4 book-item"
                     data-id="{{ book[0] }}">

                    <div class="flex-1 min-w-[200px]">

                        <h3 class="font-serif text-lg">{{ book[1] }}</h3>

                        <p class="text-sm text-gray-600">
                            {{ book[2] or 'No metadata' }}
                        </p>

                        <p class="text-xs text-gray-500 truncate max-w-md">
                            {{ book[3] }}
                        </p>

                    </div>

                    <div class="flex gap-3">

                        <button onclick="openEditModal({{ book[0] }})"
                                class="text-xs uppercase tracking-wide text-gold hover:text-ink transition">
                            Edit
                        </button>

                        <button onclick="deleteBook({{ book[0] }})"
                                class="text-xs uppercase tracking-wide text-red-600 hover:text-red-800 transition">
                            Delete
                        </button>

                    </div>

                </div>

                {% endfor %}

            </div>
        </div>
    </div>


    <!-- Add/Edit Modal -->
    <div id="bookModal"
         class="hidden fixed inset-0 modal-overlay flex items-center justify-center p-4 z-50">

        <div class="bg-ivory border border-stone p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto slide-in">

            <div class="flex justify-between items-center mb-6">

                <h2 class="text-2xl font-serif" id="modalTitle">
                    Add Book
                </h2>

                <button onclick="closeModal()"
                        class="w-8 h-8 border border-stone hover:bg-ink hover:text-ivory transition">
                    ✕
                </button>

            </div>


            <form id="bookForm" class="space-y-4">

                <input type="hidden" id="bookId" value="">


                <!-- FIXED: name="name" -->
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">
                        Book Name *
                    </label>

                    <input type="text"
                           id="bookName"
                           name="name"
                           required
                           class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>


                <!-- FIXED: name="meta" -->
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">
                        Metadata (Author, Year, etc.)
                    </label>

                    <input type="text"
                           id="bookMeta"
                           name="meta"
                           class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>


                <!-- FIXED: name="link" -->
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">
                        Google Play Link *
                    </label>

                    <input type="url"
                           id="bookLink"
                           name="link"
                           required
                           class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>


                <!-- FIXED: name="desc" -->
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">
                        Description
                    </label>

                    <textarea id="bookDesc"
                              name="desc"
                              rows="4"
                              class="w-full p-3 border border-stone focus:border-gold outline-none transition"></textarea>
                </div>


                <!-- FIXED: name="cover" -->
                <div>
                    <label class="block text-xs uppercase tracking-wide text-gray-600 mb-1">
                        Cover Image URL (optional)
                    </label>

                    <input type="url"
                           id="bookCover"
                           name="cover"
                           class="w-full p-3 border border-stone focus:border-gold outline-none transition">
                </div>


                <div id="formStatus" class="text-sm"></div>


                <button type="submit"
                        class="bg-ink text-ivory px-8 py-3 text-xs uppercase tracking-widest hover:bg-gold transition w-full">
                    Save Book
                </button>

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
                .then(books => {

                    const book = books.find(b => b.id === bookId);

                    if (book) {

                        document.getElementById('modalTitle').textContent = 'Edit Book';

                        document.getElementById('bookId').value = book.id;

                        document.getElementById('bookName').value = book.name;

                        document.getElementById('bookMeta').value = book.meta || '';

                        document.getElementById('bookLink').value = book.link;

                        document.getElementById('bookDesc').value = book.desc || '';

                        document.getElementById('bookCover').value = book.cover || '';

                        document.getElementById('formStatus').innerHTML = '';

                        document.getElementById('bookModal').classList.remove('hidden');
                    }
                })

                .catch(error => {

                    console.error('Error loading book:', error);

                    document.getElementById('formStatus').innerHTML =
                        '<span class="text-red-600">⚠️ Could not load book data.</span>';
                });
        }


        function closeModal() {
            document.getElementById('bookModal').classList.add('hidden');
        }


        document.getElementById('bookForm').addEventListener('submit', async function(e) {

            e.preventDefault();

            const bookId = document.getElementById('bookId').value;

            const isEdit = bookId !== '';

            const url = isEdit
                ? `/admin/edit/${bookId}`
                : '/admin/add';


            /*
             * IMPORTANT FIX:
             *
             * The inputs now have:
             * name="name"
             * name="meta"
             * name="link"
             * name="desc"
             * name="cover"
             *
             * Therefore FormData(this) correctly sends the values
             * to Flask's request.form.
             */

            const formData = new FormData(this);


            try {

                const response = await fetch(url, {
                    method: 'POST',
                    body: formData
                });


                const result = await response.json();


                if (result.success) {

                    document.getElementById('formStatus').innerHTML =
                        `<span class="text-green-600">✓ ${result.message}</span>`;


                    setTimeout(() => {
                        location.reload();
                    }, 1000);

                } else {

                    document.getElementById('formStatus').innerHTML =
                        `<span class="text-red-600">⚠️ Error: ${result.message}</span>`;
                }


            } catch (error) {

                console.error('Save error:', error);

                document.getElementById('formStatus').innerHTML =
                    '<span class="text-red-600">⚠️ An error occurred</span>';
            }

        });


        async function deleteBook(bookId) {

            if (!confirm('Are you sure you want to delete this book?')) return;


            try {

                const response = await fetch(`/admin/delete/${bookId}`, {
                    method: 'DELETE'
                });


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

            if (e.target === this) {
                closeModal();
            }

        });

    </script>

</body>
</html>
'''


# Routes
@app.route('/')
def index():

    conn = sqlite3.connect('books.db')

    c = conn.cursor()

    c.execute("SELECT * FROM books ORDER BY id")

    books = c.fetchall()

    conn.close()

    return render_template_string(INDEX_TEMPLATE, books=books)


@app.route('/api/books')
def api_books():

    conn = sqlite3.connect('books.db')

    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    c.execute("SELECT * FROM books ORDER BY id")

    books = [dict(row) for row in c.fetchall()]

    conn.close()

    return jsonify(books)


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


    conn = sqlite3.connect('books.db')

    c = conn.cursor()

    c.execute("SELECT * FROM books ORDER BY id")

    books = c.fetchall()

    conn.close()


    return render_template_string(ADMIN_PANEL_TEMPLATE, books=books)


@app.route('/admin/add', methods=['POST'])
def add_book():

    if not session.get('logged_in'):
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 401


    name = request.form.get('name')

    meta = request.form.get('meta', '')

    link = request.form.get('link')

    desc = request.form.get('desc', '')

    cover = request.form.get('cover', '')


    if not name or not link:

        return jsonify({
            'success': False,
            'message': 'Name and link are required'
        })


    conn = sqlite3.connect('books.db')

    c = conn.cursor()

    c.execute(
        "INSERT INTO books (name, meta, link, desc, cover) VALUES (?, ?, ?, ?, ?)",
        (name, meta, link, desc, cover)
    )

    conn.commit()

    conn.close()


    return jsonify({
        'success': True,
        'message': 'Book added successfully!'
    })


@app.route('/admin/edit/<int:book_id>', methods=['POST'])
def edit_book(book_id):

    if not session.get('logged_in'):
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 401


    name = request.form.get('name')

    meta = request.form.get('meta', '')

    link = request.form.get('link')

    desc = request.form.get('desc', '')

    cover = request.form.get('cover', '')


    if not name or not link:

        return jsonify({
            'success': False,
            'message': 'Name and link are required'
        })


    conn = sqlite3.connect('books.db')

    c = conn.cursor()

    c.execute(
        "UPDATE books SET name=?, meta=?, link=?, desc=?, cover=? WHERE id=?",
        (name, meta, link, desc, cover, book_id)
    )

    conn.commit()

    conn.close()


    return jsonify({
        'success': True,
        'message': 'Book updated successfully!'
    })


@app.route('/admin/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):

    if not session.get('logged_in'):
        return jsonify({
            'success': False,
            'message': 'Unauthorized'
        }), 401


    conn = sqlite3.connect('books.db')

    c = conn.cursor()

    c.execute(
        "DELETE FROM books WHERE id=?",
        (book_id,)
    )

    conn.commit()

    conn.close()


    return jsonify({
        'success': True,
        'message': 'Book deleted successfully!'
    })


@app.route('/admin/logout')
def logout():

    session.clear()

    return redirect(url_for('index'))


# Initialize database
init_db()


if __name__ == '__main__':

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
