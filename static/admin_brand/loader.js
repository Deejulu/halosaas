// SaasN Admin Loader
(function () {
    if (window.location.pathname.startsWith('/admin/')) {
        var loader = document.createElement('div');
        loader.id = 'saasn-loader';
        loader.innerHTML = `
      <div class="logo">SaasN</div>
      <div>Restaurant Loading</div>
      <div class="spinner"></div>
    `;
        document.body.appendChild(loader);
        setTimeout(function () {
            loader.style.opacity = 0;
            setTimeout(function () {
                loader.parentNode && loader.parentNode.removeChild(loader);
            }, 500);
        }, 2000);
    }
})();
