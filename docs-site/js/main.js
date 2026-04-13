/**
 * PDF-Master Website JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // Mobile Navigation Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            navToggle.classList.toggle('active');
        });

        // Close mobile nav when clicking a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }

    // Copy Code Buttons
    const copyButtons = document.querySelectorAll('.copy-btn');

    copyButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const code = btn.dataset.code;
            if (!code) return;

            try {
                await navigator.clipboard.writeText(code);
                const originalText = btn.textContent;
                btn.textContent = '已复制!';
                btn.style.background = 'var(--color-primary)';
                btn.style.color = 'white';
                btn.style.borderColor = 'var(--color-primary)';

                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.background = '';
                    btn.style.color = '';
                    btn.style.borderColor = '';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Intersection Observer for scroll animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.feature-card, .op-category, .provider-card, .agent-card, .step').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // Add visible class styles
    const style = document.createElement('style');
    style.textContent = `
        .visible {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);

    // Navbar background on scroll
    const nav = document.querySelector('.nav');
    let lastScrollY = window.scrollY;

    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > 50) {
            nav.style.background = 'rgba(10, 10, 10, 0.95)';
        } else {
            nav.style.background = 'rgba(10, 10, 10, 0.8)';
        }

        lastScrollY = currentScrollY;
    });

    // Stats counter animation
    const stats = document.querySelectorAll('.stat-value');
    let statsAnimated = false;

    const animateStats = () => {
        if (statsAnimated) return;

        const statsSection = document.querySelector('.hero-stats');
        if (!statsSection) return;

        const rect = statsSection.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;

        if (isVisible) {
            statsAnimated = true;
            stats.forEach(stat => {
                const finalValue = stat.textContent;
                const numericValue = parseInt(finalValue);

                if (!isNaN(numericValue)) {
                    let current = 0;
                    const increment = numericValue / 30;
                    const suffix = finalValue.replace(/[0-9]/g, '');

                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= numericValue) {
                            stat.textContent = finalValue;
                            clearInterval(timer);
                        } else {
                            stat.textContent = Math.floor(current) + suffix;
                        }
                    }, 30);
                }
            });
        }
    };

    window.addEventListener('scroll', animateStats);
    animateStats(); // Check on load

    // Table row highlight on hover
    const tableRows = document.querySelectorAll('.comparison-table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.transition = 'background 0.2s ease';
        });
    });

    // Code syntax highlighting (basic)
    document.querySelectorAll('.code-block code').forEach(code => {
        const html = code.innerHTML;
        // Highlight comments
        const highlighted = html.replace(
            /(#.*)/g,
            '<span style="color: var(--color-text-muted);">$1</span>'
        );
        code.innerHTML = highlighted;
    });

    // Lazy load images (if any are added later)
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    console.log('📄 PDF-Master website loaded successfully!');
});
