// 平滑滾動效果
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// 表單提交處理
document.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('感謝您的訊息！我們會盡快回覆。');
    this.reset();
}); 