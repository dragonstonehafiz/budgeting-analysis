export const storeIcons = {
  // Public CDN source for Simple Icons.
  // Add more entries as needed using normalized (lowercase/trimmed) store names.
  '7 eleven': 'https://upload.wikimedia.org/wikipedia/commons/4/40/7-eleven_logo.svg',
  aliexpress: 'https://cdn.simpleicons.org/aliexpress',
  amazon: 'https://upload.wikimedia.org/wikipedia/commons/d/de/Amazon_icon.png',
  'battle net': 'https://warcraft.wiki.gg/images/Battlenet_2021_icon.svg?70eff1=&format=original',
  'bungie store': 'https://cdn.simpleicons.org/bungie',
  ebay: 'https://cdn.simpleicons.org/ebay',
  'google play store': 'https://cdn.simpleicons.org/googleplay',
  kindle: 'https://static.wikia.nocookie.net/logopedia/images/2/2c/Kindle_logo_2024.svg/revision/latest?cb=20241109212732',
  lenovo: 'https://cdn.simpleicons.org/lenovo',
  'meta quest store': 'https://cdn.simpleicons.org/meta',
  'microsoft store': "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Microsoft_icon.svg/250px-Microsoft_icon.svg.png",
  'nintendo eshop': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Nintendo_Switch_logo.svg/250px-Nintendo_Switch_logo.svg.png',
  shopee: 'https://cdn.simpleicons.org/shopee',
  steam: 'https://cdn.simpleicons.org/steam',
  itunes: 'https://cdn.simpleicons.org/itunes',
  'myfonts.com': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/MyFontsLogo.svg/330px-MyFontsLogo.svg.png',
  'xbox gear shop': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/250px-Xbox_one_logo.svg.png',
  'xbox store': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/250px-Xbox_one_logo.svg.png',
  bookwalker: "https://upload.wikimedia.org/wikipedia/commons/b/bf/Bookwalkerlogo.jpg",
  buyee: "https://cdn.brandfetch.io/idXm28V7xB/w/400/h/400/theme/dark/icon.png?c=1dxbfHSJFAPEGdCLU4o5B",
  kinokuniya: "https://seibu.com.my/cdn/shop/collections/kinokuniya_logo.jpg?v=1698235167",
  kobo: "https://kobowritinglife.zendesk.com/hc/en-us/article_attachments/360091438051",
}

export function normalizeStoreName(store) {
  return String(store || '').trim().toLowerCase()
}

export function getStoreIcon(store) {
  const normalizedStore = normalizeStoreName(store)
  if (!normalizedStore) return null
  return storeIcons[normalizedStore] || null
}
