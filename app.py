# app.py — Sir Athelstan · Author website (Flask)
#
# Project structure:
#   your-project/
#   ├── app.py
#   └── static/
#       └── images/
#           └── adil-raza.jpg

import os
import requests
from flask import (Flask, render_template_string, request, jsonify,
                   redirect, url_for, session, flash)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sir_athelstan_secret_key_2025')

# ============================================
# CONFIG
# ============================================
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://book-db-1-ng4g.onrender.com')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'sirathelstan')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '@UPLUS237c')

FALLBACK_DATA = {
    "books": [],
    "total_books": 0,
    "author_info": {
        "name": "Sir Athelstan",
        "real_name": "Adil Raza",
        "location": "Siwan, Bihar, India",
        "genre": "Philosophy / Psychology",
    },
}

# ============================================
# API HELPERS (Render-hosted books API)
# ============================================
def _api(method, path, **kwargs):
    try:
        response = requests.request(method, f"{API_BASE_URL}{path}", timeout=10, **kwargs)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"API {method} {path} error: {e}")
    return None


def api_get_books():
    data = _api('GET', '/api/books')
    if data and data.get('success'):
        return data.get('data', {})
    return None


def api_get_book(book_id):
    data = _api('GET', f'/api/book/{book_id}')
    if data and data.get('success'):
        return data.get('data')
    return None


def api_add_book(book_data):
    return _api('POST', '/api/add', json=book_data)


def api_edit_book(book_id, book_data):
    return _api('PUT', f'/api/edit/{book_id}', json=book_data)


def api_delete_book(book_id):
    return _api('DELETE', f'/api/delete/{book_id}')


# ============================================
# HELPERS
# ============================================
def to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def book_from_form():
    return {
        "title": request.form.get('title', '').strip(),
        "author": request.form.get('author', '').strip() or 'Sir Athelstan',
        "cover_image": request.form.get('cover_image', '').strip(),
        "google_play_link": request.form.get('google_play_link', '').strip(),
        "description": request.form.get('description', '').strip(),
        "published_year": to_int(request.form.get('published_year'), 2025),
        "genre": request.form.get('genre', '').strip(),
    }


# ============================================
# HTML TEMPLATES
# ============================================

INDEX_TEMPLATE = '''
{% set book_list = books.books if books and books.books else [] %}
{% set info = books.author_info if books and books.author_info else {} %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sir Athelstan · Adil Raza — Author & Philosopher</title>
  <meta name="description" content="Sir Athelstan is the pen name of Adil Raza, an independent author and thinker from Siwan, Bihar, India. Writing on human psychology, cognition and psychological sovereignty." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
  <script>document.documentElement.classList.add('js');</script>
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
            stone: '#e3ded5',
            muted: '#6f6a62'
          },
          fontFamily: {
            serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
            sans: ['Inter', 'system-ui', 'sans-serif']
          }
        }
      }
    };
  </script>
  <style>
    html { scroll-behavior: smooth; }
    section[id] { scroll-margin-top: 90px; }
    body { -webkit-font-smoothing: antialiased; }

    .link-underline {
      background-image: linear-gradient(currentColor, currentColor);
      background-size: 0 1px;
      background-position: 0 100%;
      background-repeat: no-repeat;
      transition: background-size .45s ease, color .3s ease;
    }
    .link-underline:hover { background-size: 100% 1px; }

    .btn-solid {
      display: inline-flex; align-items: center; gap: .75rem;
      background: #1c1c1c; color: #fcfbf9;
      padding: 1rem 2rem; font-size: 11px; letter-spacing: .25em; text-transform: uppercase;
      transition: background-color .5s ease;
    }
    .btn-solid:hover { background: #a0743c; }

    .btn-line {
      display: inline-flex; align-items: center; gap: .75rem;
      border: 1px solid #1c1c1c; color: #1c1c1c;
      padding: 1rem 2rem; font-size: 11px; letter-spacing: .25em; text-transform: uppercase;
      transition: background-color .5s ease, color .5s ease;
    }
    .btn-line:hover { background: #1c1c1c; color: #fcfbf9; }

    .field {
      width: 100%; background: transparent;
      border: 0; border-bottom: 1px solid #e3ded5;
      padding: .75rem 0; font-size: 1rem; color: #1c1c1c; outline: none;
      transition: border-color .3s ease;
    }
    .field:focus { border-bottom-color: #a0743c; }
    textarea.field { resize: vertical; }

    .cover-shadow {
      box-shadow: 0 1px 2px rgba(28,28,28,.12), 0 22px 40px -22px rgba(28,28,28,.55);
    }

    /* Profile photo fallback (monogram if the image file is missing) */
    .monogram { display: none; }
    .no-photo img { display: none; }
    .no-photo .monogram { display: flex; align-items: center; justify-content: center; }

    /* Gentle reveal on scroll (only when JS is running) */
    .js .reveal { opacity: 0; transform: translateY(16px); transition: opacity .9s ease, transform .9s ease; }
    .js .reveal.is-in { opacity: 1; transform: none; }
  </style>
</head>

<body class="bg-cream text-ink font-sans antialiased selection:bg-gold selection:text-ivory">

  <!-- ============ HEADER ============ -->
  <header class="sticky top-0 z-40 bg-cream/90 backdrop-blur border-b border-stone">
    <div class="max-w-7xl mx-auto px-6 md:px-10 py-4 flex flex-wrap items-center justify-between gap-x-8 gap-y-3">
      <a href="#top" class="font-serif text-xl tracking-[0.3em] uppercase">Sir Athelstan</a>
      <nav class="w-full md:w-auto flex gap-6 md:gap-8 overflow-x-auto whitespace-nowrap text-[11px] uppercase tracking-[0.22em] text-muted">
        <a href="#about" class="link-underline hover:text-ink">About</a>
        <a href="#books" class="link-underline hover:text-ink">Books</a>
        <a href="#author" class="link-underline hover:text-ink">Author</a>
        <a href="#contact" class="link-underline hover:text-ink">Contact</a>
        <a href="#comments" class="link-underline hover:text-ink">Comments</a>
      </nav>
    </div>
  </header>

  <!-- ============ HERO (profile) ============ -->
  <section id="top" class="relative overflow-hidden">
    <div class="max-w-7xl mx-auto px-6 md:px-10 pt-14 md:pt-24 pb-16 md:pb-24 grid md:grid-cols-12 gap-14 md:gap-16 items-center">

      <figure class="reveal order-1 md:order-2 md:col-span-5 w-full max-w-md md:max-w-none mx-auto">
        <div class="relative overflow-hidden shadow-[0_30px_60px_-20px_rgba(28,28,28,0.45)]">
          <img src="{{ url_for('static', filename='images/adil-raza.jpg') }}"
               alt="Adil Raza, known as Sir Athelstan"
               class="w-full aspect-[4/5] object-cover"
               style="object-position: 50% 25%"
               onerror="this.parentNode.parentNode.classList.add('no-photo')" />
          <div class="monogram absolute inset-0 bg-ink font-serif text-8xl text-gold">AR</div>
        </div>
        <figcaption class="mt-4 text-[11px] uppercase tracking-[0.25em] text-muted text-right">Adil Raza · Sir Athelstan</figcaption>
      </figure>

      <div class="reveal order-2 md:order-1 md:col-span-7">
        <p class="text-[11px] uppercase tracking-[0.3em] text-gold">Author &amp; Philosopher · Siwan, Bihar</p>
        <h1 class="mt-6 font-serif font-light text-6xl md:text-8xl leading-[0.95] tracking-tight">Sir Athelstan</h1>
        <p class="mt-5 font-serif italic text-2xl md:text-3xl text-muted">The pen name of Adil Raza</p>
        <p class="mt-8 text-lg leading-relaxed text-ink/80 max-w-xl">
          An independent author and thinker from Siwan, Bihar, India, writing on human psychology, cognition, and psychological sovereignty.
        </p>
        <div class="mt-10 flex flex-wrap gap-4">
          <a href="#books" class="btn-solid">Explore the Books <span aria-hidden="true">→</span></a>
          <a href="#contact" class="btn-line">Get in Touch</a>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ STATS STRIP ============ -->
  <section class="border-y border-stone bg-ivory">
    <div class="max-w-7xl mx-auto px-6 md:px-10 py-8 grid grid-cols-1 sm:grid-cols-3 gap-6 text-center sm:text-left">
      <div>
        <p class="font-serif text-4xl">{{ book_list|length }}</p>
        <p class="mt-1 text-[11px] uppercase tracking-[0.2em] text-muted">Books on Google Play</p>
      </div>
      <div>
        <p class="font-serif text-4xl">Google Play</p>
        <p class="mt-1 text-[11px] uppercase tracking-[0.2em] text-muted">Where the books are available</p>
      </div>
      <div>
        <p class="font-serif text-4xl">Siwan, Bihar</p>
        <p class="mt-1 text-[11px] uppercase tracking-[0.2em] text-muted">India</p>
      </div>
    </div>
  </section>

  <!-- ============ ABOUT ============ -->
  <section id="about" class="py-24 md:py-32">
    <div class="max-w-7xl mx-auto px-6 md:px-10 grid md:grid-cols-12 gap-10 md:gap-16 reveal">
      <div class="md:col-span-4">
        <p class="text-[11px] uppercase tracking-[0.3em] text-gold">01 — About</p>
        <h2 class="mt-4 font-serif font-light text-4xl md:text-5xl leading-tight">About the Author</h2>
      </div>
      <div class="md:col-span-7 md:col-start-6 space-y-6 text-lg leading-relaxed text-ink/80">
        <p>
          <span class="font-serif text-2xl text-ink">Sir Athelstan</span> is the pen name of <span class="text-ink">Adil Raza</span>, an independent author and thinker from Siwan, Bihar, India.
        </p>
        <p>
          He writes on human psychology, cognition, and psychological sovereignty. His work blends philosophy, behavioural insight, and practical wisdom.
        </p>
      </div>
    </div>
  </section>

  <!-- ============ BOOKS ============ -->
  <section id="books" class="py-24 md:py-32 bg-ivory border-y border-stone">
    <div class="max-w-7xl mx-auto px-6 md:px-10">
      <div class="reveal flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-16">
        <div>
          <p class="text-[11px] uppercase tracking-[0.3em] text-gold">02 — Books</p>
          <h2 class="mt-4 font-serif font-light text-4xl md:text-5xl leading-tight">The Library</h2>
        </div>
        <p class="text-[11px] uppercase tracking-[0.25em] text-muted">Available on Google Play</p>
      </div>

      {% if book_list %}
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 md:gap-x-10 gap-y-16">
        {% for book in book_list %}
        <button type="button" class="book-card group text-left reveal" data-book-id="{{ book.id }}">
          <div class="relative aspect-[2/3] bg-ink overflow-hidden cover-shadow transition duration-500 group-hover:-translate-y-2">
            {% if book.cover_image %}
              <img src="{{ book.cover_image }}" alt="{{ book.title }}" loading="lazy" class="w-full h-full object-cover" />
            {% else %}
              <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#2a2826] to-[#0e0d0c] font-serif text-6xl text-gold">{{ (book.title or '?')[0] }}</div>
            {% endif %}
          </div>
          <h3 class="mt-6 font-serif text-2xl leading-tight group-hover:text-gold transition">{{ book.title }}</h3>
          <p class="mt-2 text-[11px] uppercase tracking-[0.2em] text-muted">
            {{ book.author or 'Sir Athelstan' }}{% if book.published_year %} · {{ book.published_year }}{% endif %}
          </p>
        </button>
        {% endfor %}
      </div>
      {% else %}
        <p class="text-center text-muted py-16">No books listed yet.</p>
      {% endif %}
    </div>
  </section>

  <!-- ============ AUTHOR DETAILS ============ -->
  <section id="author" class="py-24 md:py-32">
    <div class="max-w-7xl mx-auto px-6 md:px-10 grid md:grid-cols-12 gap-10 md:gap-16 reveal">
      <div class="md:col-span-4">
        <p class="text-[11px] uppercase tracking-[0.3em] text-gold">03 — Author</p>
        <h2 class="mt-4 font-serif font-light text-4xl md:text-5xl leading-tight">Author Details</h2>
      </div>
      <dl class="md:col-span-7 md:col-start-6 divide-y divide-stone border-y border-stone">
        <div class="py-5 grid grid-cols-3 gap-4">
          <dt class="text-[11px] uppercase tracking-[0.2em] text-muted">Full name</dt>
          <dd class="col-span-2 font-serif text-2xl">{{ info.real_name or 'Adil Raza' }}</dd>
        </div>
        <div class="py-5 grid grid-cols-3 gap-4">
          <dt class="text-[11px] uppercase tracking-[0.2em] text-muted">Pen name</dt>
          <dd class="col-span-2 font-serif text-2xl">{{ info.name or 'Sir Athelstan' }}</dd>
        </div>
        <div class="py-5 grid grid-cols-3 gap-4">
          <dt class="text-[11px] uppercase tracking-[0.2em] text-muted">Location</dt>
          <dd class="col-span-2 text-lg">{{ info.location or 'Siwan, Bihar, India' }}</dd>
        </div>
        <div class="py-5 grid grid-cols-3 gap-4">
          <dt class="text-[11px] uppercase tracking-[0.2em] text-muted">Profession</dt>
          <dd class="col-span-2 text-lg">Independent author, philosophy writer</dd>
        </div>
        <div class="py-5 grid grid-cols-3 gap-4">
          <dt class="text-[11px] uppercase tracking-[0.2em] text-muted">Focus</dt>
          <dd class="col-span-2 text-lg">Psychology, cognition, sovereignty</dd>
        </div>
      </dl>
    </div>
  </section>

  <!-- ============ CONTACT ============ -->
  <section id="contact" class="py-24 md:py-32 bg-ivory border-y border-stone">
    <div class="max-w-7xl mx-auto px-6 md:px-10 grid md:grid-cols-12 gap-10 md:gap-16 reveal">
      <div class="md:col-span-4">
        <p class="text-[11px] uppercase tracking-[0.3em] text-gold">04 — Contact</p>
        <h2 class="mt-4 font-serif font-light text-4xl md:text-5xl leading-tight">Get in Touch</h2>
      </div>
      <ul class="md:col-span-7 md:col-start-6 divide-y divide-stone border-y border-stone">
        <li>
          <a href="mailto:sirathelstan0@gmail.com" class="group flex items-center justify-between gap-4 py-6 hover:text-gold transition">
            <span class="text-[11px] uppercase tracking-[0.2em] text-muted">Email</span>
            <span class="font-serif text-lg md:text-2xl break-all">sirathelstan0@gmail.com</span>
          </a>
        </li>
        <li>
          <a href="https://youtube.com/@authorathelstan" target="_blank" rel="noopener" class="group flex items-center justify-between gap-4 py-6 hover:text-gold transition">
            <span class="text-[11px] uppercase tracking-[0.2em] text-muted">YouTube</span>
            <span class="font-serif text-lg md:text-2xl">@authorathelstan</span>
          </a>
        </li>
        <li>
          <a href="https://instagram.com/authorathelstan" target="_blank" rel="noopener" class="group flex items-center justify-between gap-4 py-6 hover:text-gold transition">
            <span class="text-[11px] uppercase tracking-[0.2em] text-muted">Instagram</span>
            <span class="font-serif text-lg md:text-2xl">@authorathelstan</span>
          </a>
        </li>
        <li>
          <a href="https://twitter.com/authorathelstan" target="_blank" rel="noopener" class="group flex items-center justify-between gap-4 py-6 hover:text-gold transition">
            <span class="text-[11px] uppercase tracking-[0.2em] text-muted">Twitter / X</span>
            <span class="font-serif text-lg md:text-2xl">@authorathelstan</span>
          </a>
        </li>
      </ul>
    </div>
  </section>

  <!-- ============ COMMENTS ============ -->
  <section id="comments" class="py-24 md:py-32">
    <div class="max-w-7xl mx-auto px-6 md:px-10 grid md:grid-cols-12 gap-10 md:gap-16 reveal">
      <div class="md:col-span-4">
        <p class="text-[11px] uppercase tracking-[0.3em] text-gold">05 — Comments</p>
        <h2 class="mt-4 font-serif font-light text-4xl md:text-5xl leading-tight">Leave a Comment</h2>
      </div>
      <form id="commentForm" class="md:col-span-7 md:col-start-6 grid md:grid-cols-2 gap-x-10 gap-y-8">
        <div>
          <label for="commentName" class="block text-[11px] uppercase tracking-[0.25em] text-muted mb-2">Full name</label>
          <input id="commentName" type="text" required class="field" />
        </div>
        <div>
          <label for="commentEmail" class="block text-[11px] uppercase tracking-[0.25em] text-muted mb-2">Email address</label>
          <input id="commentEmail" type="email" required class="field" />
        </div>
        <div class="md:col-span-2">
          <label for="commentSubject" class="block text-[11px] uppercase tracking-[0.25em] text-muted mb-2">Subject</label>
          <input id="commentSubject" type="text" required class="field" />
        </div>
        <div class="md:col-span-2">
          <label for="commentMessage" class="block text-[11px] uppercase tracking-[0.25em] text-muted mb-2">Your comment</label>
          <textarea id="commentMessage" rows="5" required class="field"></textarea>
        </div>
        <div class="md:col-span-2 flex flex-col sm:flex-row sm:items-center gap-5">
          <button type="submit" class="btn-solid self-start">Send Message</button>
          <p id="formStatus" class="text-sm text-muted"></p>
        </div>
      </form>
    </div>
  </section>

  <!-- ============ FOOTER ============ -->
  <footer class="border-t border-stone">
    <div class="max-w-7xl mx-auto px-6 md:px-10 py-12 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
      <p class="font-serif text-2xl tracking-[0.3em] uppercase">Sir Athelstan</p>
      <nav class="flex flex-wrap gap-6 text-[11px] uppercase tracking-[0.22em] text-muted">
        <a href="#about" class="link-underline hover:text-ink">About</a>
        <a href="#books" class="link-underline hover:text-ink">Books</a>
        <a href="#contact" class="link-underline hover:text-ink">Contact</a>
        <a href="/admin" class="link-underline hover:text-ink">Admin</a>
      </nav>
    </div>
    <p class="max-w-7xl mx-auto px-6 md:px-10 pb-10 text-xs text-muted">© 2026 Sir Athelstan (Adil Raza) · Siwan, Bihar · India</p>
  </footer>

  <!-- ============ BOOK MODAL ============ -->
  <div id="bookModal" class="fixed inset-0 z-50 items-center justify-center p-4 md:p-10 bg-ink/70 backdrop-blur-sm"
       style="display:none" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
    <div class="relative bg-ivory w-full max-w-4xl max-h-[90vh] overflow-y-auto grid md:grid-cols-5 shadow-2xl">
      <button id="modalClose" type="button" aria-label="Close"
              class="absolute top-4 right-4 z-10 w-9 h-9 flex items-center justify-center bg-ivory text-ink rounded-full shadow hover:text-gold transition">✕</button>
      <div id="modalCover" class="md:col-span-2 bg-ink flex items-center justify-center p-8 min-h-[280px]"></div>
      <div class="md:col-span-3 p-8 md:p-12">
        <p id="modalAuthor" class="text-[11px] uppercase tracking-[0.3em] text-gold"></p>
        <h3 id="modalTitle" class="mt-3 font-serif text-4xl leading-tight"></h3>
        <p id="modalMeta" class="mt-2 text-sm text-muted"></p>
        <p id="modalDesc" class="mt-6 text-base leading-relaxed text-ink/80"></p>
        <a id="modalPurchase" href="#" target="_blank" rel="noopener" class="btn-solid mt-10">Purchase on Google Play ↗</a>
      </div>
    </div>
  </div>

  <script>
    // ----- Books data (from the API) -----
    const bookData = {{ book_list|tojson }};

    // ----- Book modal -----
    const modal = document.getElementById('bookModal');
    const modalCover = document.getElementById('modalCover');

    function openBook(id) {
      const book = bookData.find(b => String(b.id) === String(id));
      if (!book) return;

      modalCover.innerHTML = '';
      if (book.cover_image) {
        const img = document.createElement('img');
        img.src = book.cover_image;
        img.alt = book.title || '';
        img.className = 'max-h-[60vh] max-w-full w-auto shadow-2xl';
        modalCover.appendChild(img);
      } else {
        const ph = document.createElement('div');
        ph.className = 'font-serif text-8xl text-gold';
        ph.textContent = (book.title || '?').charAt(0);
        modalCover.appendChild(ph);
      }

      document.getElementById('modalAuthor').textContent = book.author || 'Sir Athelstan';
      document.getElementById('modalTitle').textContent = book.title || 'Untitled';
      document.getElementById('modalMeta').textContent = book.published_year ? `Published ${book.published_year}` : '';
      document.getElementById('modalDesc').textContent = book.description || '';

      const buy = document.getElementById('modalPurchase');
      buy.href = book.google_play_link || '#';
      buy.style.display = book.google_play_link ? 'inline-flex' : 'none';

      modal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }

    function closeBook() {
      modal.style.display = 'none';
      document.body.style.overflow = '';
    }

    document.querySelectorAll('.book-card').forEach(card => {
      card.addEventListener('click', () => openBook(card.dataset.bookId));
    });
    document.getElementById('modalClose').addEventListener('click', closeBook);
    modal.addEventListener('click', e => { if (e.target === modal) closeBook(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeBook(); });

    // ----- Comment form (opens your email app with the message) -----
    const form = document.getElementById('commentForm');
    const formStatus = document.getElementById('formStatus');

    form.addEventListener('submit', e => {
      e.preventDefault();
      const name = document.getElementById('commentName').value.trim();
      const email = document.getElementById('commentEmail').value.trim();
      const subject = document.getElementById('commentSubject').value.trim();
      const message = document.getElementById('commentMessage').value.trim();

      if (!name || !email || !subject || !message) {
        formStatus.textContent = 'Please fill in all fields.';
        formStatus.className = 'text-sm text-red-700';
        return;
      }

      const body = `${message}\n\n— ${name}\n${email}`;
      window.location.href = `mailto:sirathelstan0@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

      formStatus.textContent = 'Your email app is opening with this message. Thank you.';
      formStatus.className = 'text-sm text-gold';
      form.reset();
    });

    // ----- Reveal on scroll -----
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
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
# ROUTES
# ============================================

@app.route('/')
def index():
    """Public author website"""
    books = api_get_books() or FALLBACK_DATA
    return render_template_string(INDEX_TEMPLATE, books=books)


@app.route('/api/books')
def api_books():
    """Proxy: all books from the Render API"""
    books = api_get_books()
    if books:
        return jsonify({"success": True, "data": books, "total": books.get('total_books', 0)})
    return jsonify({"success": False, "error": "Failed to fetch data"}), 500


@app.route('/api/book/<int:book_id>')
def api_book(book_id):
    """Proxy: single book from the Render API"""
    book = api_get_book(book_id)
    if book:
        return jsonify({"success": True, "data": book})
    return jsonify({"success": False, "error": "Book not found"}), 404


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        flash('Invalid username or password')
    return render_template_string(ADMIN_LOGIN_TEMPLATE)


@app.route('/admin/panel')
def admin_panel():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    books = api_get_books() or {"books": [], "total_books": 0}
    return render_template_string(ADMIN_PANEL_TEMPLATE, books=books)


@app.route('/admin/add', methods=['POST'])
def add_book():
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    result = api_add_book(book_from_form())
    if result and result.get('success'):
        return jsonify({"success": True, "message": "Book added successfully!"})
    return jsonify({"success": False, "message": "Failed to add book"}), 500


@app.route('/admin/edit/<int:book_id>', methods=['POST'])
def edit_book(book_id):
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    result = api_edit_book(book_id, book_from_form())
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
# RUN
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
