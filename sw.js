const CACHE_NAME = 'dhy-lego-v1';
const urlsToCache = [
  './lego_mario_builder.html',
  './styles.css',
  './script.js'
];

// 安装事件
self.addEventListener('install', event => {
  console.log('DHY乐高拼搭图生成器 Service Worker 安装中...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('DHY乐高拼搭图生成器缓存已打开');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        // 立即激活新的Service Worker
        return self.skipWaiting();
      })
  );
});

// 获取事件
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 如果找到缓存的响应，返回它
        if (response) {
          return response;
        }
        
        // 否则，从网络获取
        return fetch(event.request).then(
          response => {
            // 检查是否收到有效响应
            if(!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // 克隆响应
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          }
        );
      })
  );
});

// 激活事件
self.addEventListener('activate', event => {
  console.log('DHY乐高拼搭图生成器 Service Worker 激活');
  event.waitUntil(
    (async () => {
      // 清理旧缓存
      const names = await caches.keys();
      await Promise.all(
        names.map(n => (n !== CACHE_NAME ? (console.log('删除旧缓存:', n), caches.delete(n)) : null))
      );
      // 立即控制所有客户端
      await self.clients.claim();
    })()
  );
});