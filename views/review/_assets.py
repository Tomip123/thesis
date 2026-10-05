KEYBOARD_SHORTCUTS_JS = """
<script>
const setupKeys = () => {
    try {
        const doc = window.parent.document;
        if (!doc) return;
        doc.addEventListener('keydown', function(e) {
            const active = doc.activeElement;
            if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) {
                return;
            }
            const clickButton = (label) => {
                const btn = Array.from(doc.querySelectorAll('button')).find(b => b.innerText.includes(label));
                if (btn) { btn.click(); e.preventDefault(); }
            };
            if (e.key === 'ArrowRight') clickButton("Save & Next");
            if (e.key === 'ArrowLeft') clickButton("Previous");
        });
    } catch (err) {
        console.error("Review shortcuts error:", err);
    }
};
setTimeout(setupKeys, 500);
setTimeout(setupKeys, 1500);
</script>
"""

STICKY_FOOTER_CSS = """
<style>
div[data-testid="stVerticalBlock"] > div:has(div.verification-footer) {
    position: fixed;
    bottom: 10px;
    left: 21rem;
    width: calc(100% - 22rem);
    max-height: 65vh;
    overflow-y: auto;
    background-color: #ffffff;
    opacity: 1 !important;
    z-index: 9999;
    border: 2px solid #4CAF50;
    border-radius: 15px;
    box-shadow: 0 -10px 40px rgba(0,0,0,0.2);
    padding: 30px;
}
@media (prefers-color-scheme: dark) {
    div[data-testid="stVerticalBlock"] > div:has(div.verification-footer) {
        background-color: #1e1e1e;
    }
}
</style>
<div class="verification-footer"></div>
"""
