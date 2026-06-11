(function () {
    'use strict';

    /* ========================================
       DOM Ready
    ======================================== */
    document.addEventListener('DOMContentLoaded', function () {

        /* ========================================
           Theme Toggle
        ======================================== */
        const themeToggle = document.getElementById('themeToggle');
        const html = document.documentElement;

        function getPreferredTheme() {
            const stored = localStorage.getItem('theme');
            if (stored) return stored;
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }

        function setTheme(theme) {
            html.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        }

        setTheme(getPreferredTheme());

        if (themeToggle) {
            themeToggle.addEventListener('click', function () {
                const current = html.getAttribute('data-theme');
                setTheme(current === 'dark' ? 'light' : 'dark');
            });
        }

        /* ========================================
           Search Dropdown with Suggestions
        ======================================== */
        const searchToggle = document.getElementById('searchToggle');
        const searchDropdown = document.getElementById('searchDropdown');
        const searchClose = document.getElementById('searchClose');
        const searchInput = document.getElementById('searchInput');
        const suggestionsEl = document.getElementById('searchSuggestions');
        const suggestionsResults = document.getElementById('suggestionsResults');
        const headerSearchInput = document.getElementById('headerSearchInput');

        let searchTimer = null;
        let searchOpen = false;

        function openSearch() {
            if (!searchDropdown) return;
            searchDropdown.classList.add('active');
            searchOpen = true;
            if (searchInput) setTimeout(function () { searchInput.focus(); }, 100);
            if (suggestionsResults) suggestionsResults.style.display = 'none';
            var def = suggestionsEl ? suggestionsEl.querySelector('.suggestions-default') : null;
            if (def) def.style.display = 'block';
        }

        function closeSearch() {
            if (!searchDropdown) return;
            searchDropdown.classList.remove('active');
            searchOpen = false;
            if (searchInput) searchInput.value = '';
            if (suggestionsResults) suggestionsResults.style.display = 'none';
            var def = suggestionsEl ? suggestionsEl.querySelector('.suggestions-default') : null;
            if (def) def.style.display = 'block';
        }

        if (searchToggle) searchToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            if (searchOpen) { closeSearch(); } else { openSearch(); }
        });

        if (searchClose) searchClose.addEventListener('click', closeSearch);

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeSearch();
            if ((e.key === '/' || (e.ctrlKey && e.key === 'k')) && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
                e.preventDefault();
                openSearch();
            }
        });

        /* Close on click outside */
        document.addEventListener('click', function (e) {
            var headerSearch = document.querySelector('.header-search-form');
            if (searchOpen && searchDropdown && !searchDropdown.contains(e.target)
                && e.target !== searchToggle && !searchToggle.contains(e.target)
                && (!headerSearch || !headerSearch.contains(e.target))) {
                closeSearch();
            }
        });

        /* Live search suggestions */
        if (searchInput) {
            searchInput.addEventListener('input', function () {
                var q = this.value.trim();
                clearTimeout(searchTimer);

                var def = suggestionsEl ? suggestionsEl.querySelector('.suggestions-default') : null;
                if (!suggestionsResults) return;

                if (q.length < 2) {
                    suggestionsResults.style.display = 'none';
                    suggestionsResults.innerHTML = '';
                    if (def) def.style.display = 'block';
                    return;
                }

                if (def) def.style.display = 'none';

                searchTimer = setTimeout(function () {
                    fetch('/search/suggest/?q=' + encodeURIComponent(q))
                        .then(function (r) { return r.json(); })
                        .then(function (data) {
                            suggestionsResults.innerHTML = data.html;
                            suggestionsResults.style.display = 'block';
                        })
                        .catch(function () {
                            suggestionsResults.style.display = 'none';
                        });
                }, 150);
            });
        }

        /* Sync header search input with dropdown */
        if (headerSearchInput) {
            headerSearchInput.addEventListener('focus', function (e) {
                openSearch();
                if (searchInput) {
                    searchInput.value = headerSearchInput.value;
                    searchInput.dispatchEvent(new Event('input'));
                }
            });

            headerSearchInput.addEventListener('input', function () {
                if (searchInput) {
                    searchInput.value = this.value;
                    searchInput.dispatchEvent(new Event('input'));
                }
            });
        }

        /* Sync dropdown input back to header */
        if (searchInput) {
            searchInput.addEventListener('input', function () {
                if (headerSearchInput) {
                    headerSearchInput.value = this.value;
                }
            });
        }

        /* ========================================
           Mobile Drawer Menu
        ======================================== */
        const hamburger = document.getElementById('hamburger');
        const mainNav = document.getElementById('mainNav');
        const drawerOverlay = document.getElementById('drawerOverlay');
        const drawerClose = document.getElementById('drawerClose');
        const drawerThemeToggle = document.getElementById('drawerThemeToggle');
        var drawerOpen = false;

        /* Focus trap elements */
        function getFocusableElements() {
            if (!mainNav || !mainNav.classList.contains('active')) return [];
            return Array.from(mainNav.querySelectorAll(
                'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
            ));
        }

        function trapFocus(e) {
            if (e.key !== 'Tab') return;
            var focusable = getFocusableElements();
            if (focusable.length === 0) return;
            var first = focusable[0];
            var last = focusable[focusable.length - 1];
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        }

        function openDrawer() {
            if (!mainNav) return;
            hamburger.classList.add('active');
            mainNav.classList.add('active');
            document.body.classList.add('nav-open');
            drawerOpen = true;
            document.addEventListener('keydown', trapFocus);
            /* Focus close button */
            setTimeout(function () {
                if (drawerClose) drawerClose.focus();
            }, 350);
            /* Re-trigger stagger animation by removing and re-adding items */
            var items = mainNav.querySelectorAll('.drawer-nav-item');
            items.forEach(function (item) {
                item.style.animation = 'none';
                item.offsetHeight; /* force reflow */
                item.style.animation = '';
            });
        }

        function closeDrawer() {
            if (!mainNav) return;
            hamburger.classList.remove('active');
            mainNav.classList.remove('active');
            document.body.classList.remove('nav-open');
            drawerOpen = false;
            document.removeEventListener('keydown', trapFocus);
            /* Return focus to hamburger */
            if (hamburger) hamburger.focus();
        }

        if (hamburger && mainNav) {
            hamburger.addEventListener('click', function () {
                if (drawerOpen) {
                    closeDrawer();
                } else {
                    openDrawer();
                }
            });

            /* Close on overlay click */
            if (drawerOverlay) {
                drawerOverlay.addEventListener('click', closeDrawer);
            }

            /* Close button */
            if (drawerClose) {
                drawerClose.addEventListener('click', closeDrawer);
            }

            /* Close on nav link click */
            mainNav.querySelectorAll('a.drawer-nav-item').forEach(function (link) {
                link.addEventListener('click', closeDrawer);
            });

            /* ESC key */
            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && drawerOpen) {
                    closeDrawer();
                }
            });

            /* Sync drawer theme toggle with header theme toggle */
            if (drawerThemeToggle) {
                drawerThemeToggle.addEventListener('click', function () {
                    if (themeToggle) themeToggle.click();
                });
            }

            /* Drawer category toggle */
            var catToggle = document.getElementById('drawerCategoryToggle');
            var catList = document.getElementById('drawerCategoryList');
            if (catToggle && catList) {
                catToggle.addEventListener('click', function (e) {
                    e.stopPropagation();
                    catToggle.classList.toggle('open');
                    catList.classList.toggle('open');
                });
            }
        }

        /* ========================================
           Sticky Header on Scroll
        ======================================== */
        const siteHeader = document.getElementById('siteHeader');
        let headerScrolled = false;

        function checkScroll() {
            if (!siteHeader) return;
            if (window.scrollY > 10) {
                if (!headerScrolled) {
                    siteHeader.classList.add('scrolled');
                    headerScrolled = true;
                }
            } else {
                if (headerScrolled) {
                    siteHeader.classList.remove('scrolled');
                    headerScrolled = false;
                }
            }
        }

        window.addEventListener('scroll', checkScroll, { passive: true });
        checkScroll();

        /* ========================================
           Lazy Loading Images (fallback)
        ======================================== */
        if ('loading' in HTMLImageElement.prototype) {
            document.querySelectorAll('img[loading="lazy"]').forEach(function (img) {
                img.src = img.src;
            });
        }

        /* ========================================
           Smooth Anchor Scrolling
        ======================================== */
        document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
            anchor.addEventListener('click', function (e) {
                var target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });

        /* ========================================
           Hero Carousel (Fade)
        ======================================== */
        var carousel = document.getElementById('heroCarousel');
        if (carousel) {
            var slides = carousel.querySelectorAll('.slide');
            var dots = carousel.querySelectorAll('.dot');
            var prevBtn = document.getElementById('carouselPrev');
            var nextBtn = document.getElementById('carouselNext');
            var current = 0;
            var total = slides.length;
            var timer = null;

            if (total < 2) return;

            function goTo(index) {
                if (index < 0) index = total - 1;
                if (index >= total) index = 0;
                current = index;

                slides.forEach(function (s, i) {
                    s.classList.toggle('active', i === current);
                });
                dots.forEach(function (d, i) {
                    d.classList.toggle('active', i === current);
                });
            }

            function nextSlide() { goTo(current + 1); }
            function prevSlide() { goTo(current - 1); }

            function resetTimer() {
                clearInterval(timer);
                timer = setInterval(nextSlide, 5000);
            }

            if (nextBtn) nextBtn.addEventListener('click', function () { nextSlide(); resetTimer(); });
            if (prevBtn) prevBtn.addEventListener('click', function () { prevSlide(); resetTimer(); });

            dots.forEach(function (d) {
                d.addEventListener('click', function () {
                    goTo(parseInt(this.getAttribute('data-index')));
                    resetTimer();
                });
            });

            timer = setInterval(nextSlide, 5000);

            carousel.addEventListener('mouseenter', function () { clearInterval(timer); });
            carousel.addEventListener('mouseleave', function () { timer = setInterval(nextSlide, 5000); });
        }

        /* ========================================
           Load More Button
        ======================================== */
        var loadMoreBtn = document.getElementById('loadMoreBtn');
        var newsFeed = document.getElementById('newsFeed');
        if (loadMoreBtn && newsFeed) {
            var rows = newsFeed.querySelectorAll('.news-row');
            var visible = 5;
            var total = rows.length;

            function showRows(count) {
                rows.forEach(function (r, i) {
                    r.style.display = i < count ? '' : 'none';
                });
                if (count >= total) {
                    loadMoreBtn.style.display = 'none';
                }
            }

            showRows(visible);

            loadMoreBtn.addEventListener('click', function () {
                visible += 5;
                showRows(visible);
            });
        }

        /* ========================================
           Article Page Interactive Features
        ======================================== */

        /* Reading Progress Bar */
        var progressBar = document.getElementById('readingProgress');
        if (progressBar) {
            window.addEventListener('scroll', function () {
                var scrollTop = window.scrollY;
                var docHeight = document.documentElement.scrollHeight - window.innerHeight;
                var progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
                progressBar.style.width = progress + '%';
            }, { passive: true });
        }

        /* Table of Contents */
        var tocList = document.getElementById('tocList');
        var tocCard = document.getElementById('tableOfContents');
        var articleBody = document.getElementById('articleBody');
        if (tocList && articleBody) {
            var headings = articleBody.querySelectorAll('h2, h3');
            var tocItems = [];
            if (headings.length && tocCard) {
                tocCard.style.display = 'block';
            }
            headings.forEach(function (h, i) {
                if (!h.id) {
                    h.id = 'heading-' + i;
                }
                var li = document.createElement('li');
                var a = document.createElement('a');
                a.href = '#' + h.id;
                a.className = 'toc-link' + (h.tagName === 'H3' ? ' toc-h3' : '');
                a.textContent = h.textContent;
                a.addEventListener('click', function (e) {
                    e.preventDefault();
                    var target = document.getElementById(this.getAttribute('href').slice(1));
                    if (target) {
                        var top = target.getBoundingClientRect().top + window.scrollY - 80;
                        window.scrollTo({ top: top, behavior: 'smooth' });
                    }
                });
                li.appendChild(a);
                tocList.appendChild(li);
                tocItems.push(a);
            });

            /* Highlight active TOC item on scroll */
            if (tocItems.length) {
                window.addEventListener('scroll', function () {
                    var current = '';
                    headings.forEach(function (h) {
                        var rect = h.getBoundingClientRect();
                        if (rect.top <= 120) {
                            current = h.id;
                        }
                    });
                    tocItems.forEach(function (a) {
                        a.classList.toggle('active', a.getAttribute('href') === '#' + current);
                    });
                }, { passive: true });
            }
        }

        /* Font Size Toggle */
        var fontSizeBtns = document.querySelectorAll('.font-size-btn');
        if (fontSizeBtns.length && articleBody) {
            fontSizeBtns.forEach(function (btn) {
                btn.addEventListener('click', function () {
                    fontSizeBtns.forEach(function (b) { b.classList.remove('active'); });
                    this.classList.add('active');
                    var size = this.getAttribute('data-size');
                    articleBody.classList.remove('font-large', 'font-xlarge');
                    if (size === 'large') articleBody.classList.add('font-large');
                    if (size === 'xlarge') articleBody.classList.add('font-xlarge');
                });
            });
        }

        /* Copy Link */
        function setupCopyLink(btnId) {
            var btn = document.getElementById(btnId);
            if (!btn) return;
            btn.addEventListener('click', function () {
                var url = window.location.href;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(url).then(function () {
                        btn.classList.add('copied');
                        var originalHTML = btn.innerHTML;
                        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg><span>Copied!</span>';
                        setTimeout(function () {
                            btn.classList.remove('copied');
                            btn.innerHTML = originalHTML;
                        }, 2500);
                    });
                } else {
                    var input = document.createElement('input');
                    input.value = url;
                    document.body.appendChild(input);
                    input.select();
                    document.execCommand('copy');
                    document.body.removeChild(input);
                    btn.classList.add('copied');
                    setTimeout(function () { btn.classList.remove('copied'); }, 2500);
                }
            });
        }
        setupCopyLink('copyLinkBtn');

        /* Image Lightbox */
        var lightbox = document.getElementById('lightbox');
        var lightboxImage = document.getElementById('lightboxImage');
        var lightboxCaption = document.getElementById('lightboxCaption');
        var lightboxClose = document.getElementById('lightboxClose');

        if (lightbox && lightboxImage && articleBody) {
            articleBody.querySelectorAll('img').forEach(function (img) {
                img.addEventListener('click', function () {
                    lightbox.classList.add('active');
                    lightboxImage.src = this.src;
                    lightboxImage.alt = this.alt;
                    lightboxCaption.textContent = this.alt || '';
                });
            });

            function closeLightbox() {
                lightbox.classList.remove('active');
            }

            if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
            lightbox.addEventListener('click', closeLightbox);
            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && lightbox.classList.contains('active')) {
                    closeLightbox();
                }
            });
        }

        /* Back to Top */
        var backToTop = document.getElementById('backToTop');
        if (backToTop) {
            window.addEventListener('scroll', function () {
                backToTop.classList.toggle('visible', window.scrollY > 500);
            }, { passive: true });

            backToTop.addEventListener('click', function () {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }

        /* ========================================
           Cookie Consent Banner
        ======================================== */
        var cookieConsent = document.getElementById('cookieConsent');
        var cookieBtn = document.getElementById('cookieConsentBtn');
        if (cookieConsent && cookieBtn) {
            if (!localStorage.getItem('cookie_consent')) {
                setTimeout(function () {
                    cookieConsent.classList.add('show');
                }, 500);
            }
            cookieBtn.addEventListener('click', function () {
                localStorage.setItem('cookie_consent', 'accepted');
                cookieConsent.classList.remove('show');
            });
        }

    });

})();
