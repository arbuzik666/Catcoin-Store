

document.addEventListener('DOMContentLoaded', function() {
    console.log('🐱 Catcoin готов к работе!');
    const productCards = document.querySelectorAll('.product-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });
    
    productCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s, transform 0.5s';
        observer.observe(card);
    });
    

    document.addEventListener('click', function(event) {
        createPawPrints(event.clientX, event.clientY);
    });
    
    function createPawPrints(x, y) {
        const count = 6;
        
        const paws = ['🐾', '🐱', '✨'];
        
        for (let i = 0; i < count; i++) {
            const paw = document.createElement('span');
            paw.classList.add('flying-paw');
            
            paw.textContent = paws[Math.floor(Math.random() * paws.length)];
            
            paw.style.left = x + 'px';
            paw.style.top = y + 'px';
            
            const angle = (Math.PI * 2 * i) / count + (Math.random() * 0.5 - 0.25);
            const distance = 40 + Math.random() * 70;
            const tx = Math.cos(angle) * distance;
            const ty = Math.sin(angle) * distance - 20; 
            
            paw.style.setProperty('--tx', tx + 'px');
            paw.style.setProperty('--ty', ty + 'px');
            paw.style.setProperty('--r', (Math.random() * 360 - 180) + 'deg');
            paw.style.setProperty('--s', (0.8 + Math.random() * 0.7));
            
            document.body.appendChild(paw);
            
            paw.addEventListener('animationend', function() {
                paw.remove();
            });
        }
    }
});