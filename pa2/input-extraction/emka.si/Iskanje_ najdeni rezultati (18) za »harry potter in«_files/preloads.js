
    (function() {
      var baseURL = "https://cdn.shopify.com/shopifycloud/checkout-web/assets/";
      var scripts = ["https://cdn.shopify.com/shopifycloud/checkout-web/assets/runtime.latest.sl-SI.8c7654bc7dae0cc8e8f6.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/699.latest.sl-SI.dd87a410b730431c1e33.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/910.latest.sl-SI.48f0c0c407dcf3c0ec73.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/137.latest.sl-SI.acb2b4a872cf6cabdfa2.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/app.latest.sl-SI.de9e7781708a9459191d.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/977.latest.sl-SI.e1a0ded7d00403072415.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/582.latest.sl-SI.4ee215791a93f8eeed8e.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/78.latest.sl-SI.251751f1b1eaca6e5d24.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/927.latest.sl-SI.222f26622f6ff8ccbe95.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/2.latest.sl-SI.2e5d17f82bdd53214da5.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/387.latest.sl-SI.cebbcb752144c9c8994d.js","https://cdn.shopify.com/shopifycloud/checkout-web/assets/OnePage.latest.sl-SI.a6d9f0c7153598a1c5d5.js"];
      var styles = ["https://cdn.shopify.com/shopifycloud/checkout-web/assets/699.latest.sl-SI.984415a5e42e39e1440c.css","https://cdn.shopify.com/shopifycloud/checkout-web/assets/app.latest.sl-SI.7cb816443ebc83362061.css","https://cdn.shopify.com/shopifycloud/checkout-web/assets/268.latest.sl-SI.b5156113878175d25f8f.css"];
      var fontPreconnectUrls = [];
      var fontPrefetchUrls = [];
      var imgPrefetchUrls = ["https://cdn.shopify.com/s/files/1/0662/3549/8785/files/Logo_MK_x320.png?v=1681886463"];

      function preconnect(url, callback) {
        var link = document.createElement('link');
        link.rel = 'dns-prefetch preconnect';
        link.href = url;
        link.crossOrigin = '';
        link.onload = link.onerror = callback;
        document.head.appendChild(link);
      }

      function preconnectAssets() {
        var resources = [baseURL].concat(fontPreconnectUrls);
        var index = 0;
        (function next() {
          var res = resources[index++];
          if (res) preconnect(res[0], next);
        })();
      }

      function prefetch(url, as, callback) {
        var link = document.createElement('link');
        if (link.relList.supports('prefetch')) {
          link.rel = 'prefetch';
          link.fetchPriority = 'low';
          link.as = as;
          if (as === 'font') link.type = 'font/woff2';
          link.href = url;
          link.crossOrigin = '';
          link.onload = link.onerror = callback;
          document.head.appendChild(link);
        } else {
          var xhr = new XMLHttpRequest();
          xhr.open('GET', url, true);
          xhr.onloadend = callback;
          xhr.send();
        }
      }

      function prefetchAssets() {
        var resources = [].concat(
          scripts.map(function(url) { return [url, 'script']; }),
          styles.map(function(url) { return [url, 'style']; }),
          fontPrefetchUrls.map(function(url) { return [url, 'font']; }),
          imgPrefetchUrls.map(function(url) { return [url, 'image']; })
        );
        var index = 0;
        (function next() {
          var res = resources[index++];
          if (res) prefetch(res[0], res[1], next);
        })();
      }

      function onLoaded() {
        preconnectAssets();
        prefetchAssets();
      }

      if (document.readyState === 'complete') {
        onLoaded();
      } else {
        addEventListener('load', onLoaded);
      }
    })();
  