/**
 * mockTransactions.js
 *
 * Shared mock transaction data used across pages until the FastAPI backend is wired up.
 * Replace the MOCK_TRANSACTIONS import with an API call when the backend is ready.
 *
 * Transaction shape:
 *   { Date: string, Cost: number, Category: string, Item: string,
 *     Month: string, MonthNum: number, Year: number, Notes?: string }
 */

const MONTHS = [
  { name: 'January',   num: 1  }, { name: 'February',  num: 2  }, { name: 'March',     num: 3  },
  { name: 'April',     num: 4  }, { name: 'May',        num: 5  }, { name: 'June',      num: 6  },
  { name: 'July',      num: 7  }, { name: 'August',     num: 8  }, { name: 'September', num: 9  },
  { name: 'October',   num: 10 }, { name: 'November',   num: 11 }, { name: 'December',  num: 12 },
]

// 100 procedurally-generated grocery purchases spread across 2025
const GROCERY_ENTRIES = Array.from({ length: 100 }, (_, i) => {
  const month = MONTHS[i % 12]
  const day   = ((i * 3) % 27) + 1
  const cost  = parseFloat((20 + (i * 7.3) % 60).toFixed(2))
  return {
    Date:     `2025-${String(month.num).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
    Cost:     cost,
    Category: 'Food & Beverages',
    Item:     'Groceries',
    Month:    month.name,
    MonthNum: month.num,
    Year:     2025,
  }
})

const HAND_CRAFTED = [
  { Date: '2025-01-03', Cost: 12.50,  Category: 'Food & Beverages',          Item: 'Lunch',           Month: 'January',   MonthNum: 1,  Year: 2025 },
  { Date: '2025-01-10', Cost: 85.00,  Category: 'Gaming',                    Item: 'Steam',           Month: 'January',   MonthNum: 1,  Year: 2025 },
  { Date: '2025-01-18', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'January',   MonthNum: 1,  Year: 2025 },
  { Date: '2025-02-02', Cost: 45.00,  Category: 'Food & Beverages',          Item: 'Groceries',       Month: 'February',  MonthNum: 2,  Year: 2025 },
  { Date: '2025-02-14', Cost: 120.00, Category: 'Electronics & Accessories', Item: 'USB Hub',         Month: 'February',  MonthNum: 2,  Year: 2025 },
  { Date: '2025-02-20', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'February',  MonthNum: 2,  Year: 2025 },
  { Date: '2025-03-05', Cost: 60.00,  Category: 'Movies & Media',            Item: 'Blu-ray Box Set', Month: 'March',     MonthNum: 3,  Year: 2025 },
  { Date: '2025-03-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'March',     MonthNum: 3,  Year: 2025 },
  { Date: '2025-03-28', Cost: 250.00, Category: 'Gaming',                    Item: 'Steam',           Month: 'March',     MonthNum: 3,  Year: 2025 },
  { Date: '2025-04-01', Cost: 35.00,  Category: 'Food & Beverages',          Item: 'Groceries',       Month: 'April',     MonthNum: 4,  Year: 2025 },
  { Date: '2025-04-10', Cost: 70.00,  Category: 'Clothing & Apparel',        Item: 'Jacket',          Month: 'April',     MonthNum: 4,  Year: 2025 },
  { Date: '2025-04-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'April',     MonthNum: 4,  Year: 2025 },
  { Date: '2025-04-22', Cost: 22.00,  Category: 'Food & Beverages',          Item: 'Lunch',           Month: 'April',     MonthNum: 4,  Year: 2025 },
  { Date: '2025-05-03', Cost: 90.00,  Category: 'Health & Personal Care',    Item: 'Gym Membership',  Month: 'May',       MonthNum: 5,  Year: 2025 },
  { Date: '2025-05-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'May',       MonthNum: 5,  Year: 2025 },
  { Date: '2025-05-19', Cost: 45.00,  Category: 'Books & Literature',        Item: 'Novel',           Month: 'May',       MonthNum: 5,  Year: 2025 },
  { Date: '2025-06-07', Cost: 200.00, Category: 'Electronics & Accessories', Item: 'Keyboard',        Month: 'June',      MonthNum: 6,  Year: 2025 },
  { Date: '2025-06-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'June',      MonthNum: 6,  Year: 2025 },
  { Date: '2025-06-25', Cost: 55.00,  Category: 'Food & Beverages',          Item: 'Groceries',       Month: 'June',      MonthNum: 6,  Year: 2025 },
  { Date: '2025-07-04', Cost: 30.00,  Category: 'Movies & Media',            Item: 'Blu-ray Box Set', Month: 'July',      MonthNum: 7,  Year: 2025 },
  { Date: '2025-07-14', Cost: 110.00, Category: 'Gaming',                    Item: 'Steam',           Month: 'July',      MonthNum: 7,  Year: 2025 },
  { Date: '2025-07-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'July',      MonthNum: 7,  Year: 2025 },
  { Date: '2025-08-01', Cost: 75.00,  Category: 'Collectibles',              Item: 'Figurine',        Month: 'August',    MonthNum: 8,  Year: 2025 },
  { Date: '2025-08-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'August',    MonthNum: 8,  Year: 2025 },
  { Date: '2025-08-20', Cost: 40.00,  Category: 'Food & Beverages',          Item: 'Groceries',       Month: 'August',    MonthNum: 8,  Year: 2025 },
  { Date: '2025-09-10', Cost: 95.00,  Category: 'Music & Audio',             Item: 'Headphones',      Month: 'September', MonthNum: 9,  Year: 2025 },
  { Date: '2025-09-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'September', MonthNum: 9,  Year: 2025 },
  { Date: '2025-10-05', Cost: 25.00,  Category: 'Food & Beverages',          Item: 'Lunch',           Month: 'October',   MonthNum: 10, Year: 2025 },
  { Date: '2025-10-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'October',   MonthNum: 10, Year: 2025 },
  { Date: '2025-10-18', Cost: 180.00, Category: 'Gaming',                    Item: 'Steam',           Month: 'October',   MonthNum: 10, Year: 2025 },
  { Date: '2025-11-02', Cost: 60.00,  Category: 'Miscellaneous',             Item: 'Misc Item',       Month: 'November',  MonthNum: 11, Year: 2025 },
  { Date: '2025-11-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'November',  MonthNum: 11, Year: 2025 },
  { Date: '2025-11-28', Cost: 320.00, Category: 'Electronics & Accessories', Item: 'Monitor',         Month: 'November',  MonthNum: 11, Year: 2025 },
  { Date: '2025-12-10', Cost: 145.00, Category: 'Gaming',                    Item: 'Steam',           Month: 'December',  MonthNum: 12, Year: 2025 },
  { Date: '2025-12-15', Cost: 15.00,  Category: 'Digital Subscriptions',     Item: 'Netflix',         Month: 'December',  MonthNum: 12, Year: 2025 },
  { Date: '2025-12-24', Cost: 85.00,  Category: 'Food & Beverages',          Item: 'Groceries',       Month: 'December',  MonthNum: 12, Year: 2025 },
]

export const MOCK_TRANSACTIONS = [...GROCERY_ENTRIES, ...HAND_CRAFTED]
