const { chromium } = require('playwright');

const brands = require('./Brands.js');

const fuels = ['GPL', 'Diesel', 'Essence', 'Hybride', 'Electrique']

const gearBoxes = ['Automatique', 'Manuelle', 'Semi Automatique']

const papers = ['Carte grise / safia', 'Carte jaune', 'Licence / Délai']

const colors = ["Aubergine", "Autre", "Beige", "Blanc", "Bleu", "Bleu Ciel", "Bleu Gauloise", "Bleu Nuit", "Bleu Turquoise", "Grenat", "Gris", "Gris Alluminium", "Gris Argent", "Gris Champagne", "Gris Manitoba", "Gris Souris", "Jaune", "Maron Chocolat", "Mauve", "Miel", "Noir", "Orange", "Rose", "Rouge", "Rouge Bordeaux", "Vert", "Vert Bouteille", "Vert Militaire", "Vert Pistache", "Violet"]

async function slowScroll(page, step = 100, delay = 200, maxNumber = 100) {
    while (maxNumber > 0) {
        await page.evaluate((s) => window.scrollBy(0, s), step);
        await page.waitForTimeout(delay);
        maxNumber--
    }
}

const { Sequelize, DataTypes } = require('sequelize');

// connect to sqlite db
const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: 'cars_db.sqlite',
    logging: false,   // 🚀 disables all SQL logs
});

// define Car model
const Car = sequelize.define('Car', {
    id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
    link: { type: DataTypes.STRING, allowNull: false, unique: true },
    title: { type: DataTypes.STRING },
    price: { type: DataTypes.INTEGER, allowNull: false },
    engine: { type: DataTypes.STRING },
    fuel: { type: DataTypes.STRING },
    mileage: { type: DataTypes.INTEGER },
    color: { type: DataTypes.STRING },
    gearbox: { type: DataTypes.STRING },
    paper: { type: DataTypes.STRING },
    brand: { type: DataTypes.STRING },
    year: { type: DataTypes.INTEGER },
    model: { type: DataTypes.STRING },
    finition: { type: DataTypes.STRING },
    location: { type: DataTypes.STRING },
    wilaya: { type: DataTypes.INTEGER },
    date: { type: DataTypes.DATE },
}, {
    timestamps: true // auto-manages createdAt and updatedAt
});

async function scrapeOuedkniss(page, pageNum = 1, minPice = 50, maxPrice = 120) {
    /**
     * Scrapes car titles from Ouedkniss.com using Playwright.
     * It handles lazy-loaded content by scraping while scrolling to the bottom of the page.
     */
    const url = `https://www.ouedkniss.com/automobiles_vehicules/${pageNum}?priceUnit=MILLION&priceRangeMin=${minPice}&priceRangeMax=${maxPrice}`;


    console.log(`Navigating to ${url}...`);
    await page.goto(url);

    console.log("Scrolling and scraping to load all content...");

    // Scroll to the bottom of the page
    await slowScroll(page, 1200, 200, 10)

    // Wait for a brief moment for new content to load
    await page.waitForTimeout(2000); // Wait for 2 seconds

    // Get all the listing divs and scrape the new ones
    const allListingItems = await page.locator('.search-view-item').all();
    // const allListingItems = await autoScrollAndCollect(page);

    for (let i = 0; i < allListingItems.length; i++) {
        const item = allListingItems[i];

        // Scroll into view before scraping
        await item.scrollIntoViewIfNeeded();
        await page.waitForTimeout(200); // small delay to let content load

        let href, titleText, brand, year, model, finition, price, mileage, fuel, gearBox, paper, engine, color, location, wilaya, postDate

        try {
            // Extract Link

            const link = item.locator('a.v-card--link');
            if (await link.count() > 0) {
                href = await link.getAttribute('href');
                href = 'https://www.ouedkniss.com' + href
            }

            // Extract Title    
            const titleH3 = item.locator('h3.o-announ-card-title');
            if (await titleH3.count() > 0) {
                titleText = await titleH3.textContent();
                titleText = titleText.trim()
            }


            // Extract brand
            brand = brands.find(brand =>
                titleText.toUpperCase().includes(brand)
            );

            // find all 4-digit numbers that look like years
            let matches = titleText.match(/\b(19\d{2}|20\d{2})\b/g);

            // convert to numbers and filter range
            if (matches) {
                matches = matches
                    .map(y => Number(y))

                if (matches.length > 1) {
                    year = matches[1]

                } else year = matches[0];
            }


            // Create regex to remove brand (case-insensitive)
            const brandRegex = new RegExp(`\\b${brand}\\b`, "i");
            let cleanText = titleText.replace(brandRegex, "");

            // Split by spaces
            const parts = cleanText.split(year);

            // Model = first word
            model = parts[0].trim() || null;

            // Finition = rest of string
            finition = parts.length > 1 ? parts[1].trim() : null;

            // Extract Price
            let priceText = await item.locator('span.price div.mr-1')
            if (await priceText.count() > 0) {
                priceText = await priceText.innerText();
                price = parseInt(priceText, 10); // convert to number
            }

            // Extract more info
            let chips = await item.locator('span.v-chip')
            if (await chips.count() > 0) {
                chips = await chips.allInnerTexts();

                for (let entry of chips) {
                    entry = entry.trim()
                    // Find Milage
                    if (entry.includes("km")) {
                        const parts = entry.split("km");
                        const firstPart = parts[0].trim().replace(/\s/g, ""); // remove spaces

                        if (!isNaN(firstPart) && firstPart !== "") {
                            mileage = Number(firstPart);
                            continue
                        }

                    }

                    // Find Fuel
                    if (fuels.includes(entry)) {
                        fuel = entry; // exact match
                        continue
                    }

                    // Find Gearbox
                    if (gearBoxes.includes(entry)) {
                        gearBox = entry; // exact match
                        continue
                    }
                    // Find Papers
                    if (papers.includes(entry)) {
                        paper = entry; // exact match
                        continue
                    }

                    // Find Color
                    if (colors.includes(entry)) {
                        color = entry; // exact match
                        continue
                    }

                    engine = entry
                }
            }

            // Extract Location and Wilaya
            const cityLocator = item.locator('span.o-announ-card-city');
            if (await cityLocator.count() > 0) {
                const rawText = await cityLocator.innerText();
                // Split and trim
                const [locationt, wilayat] = rawText.split(',').map(s => s.trim());
                wilaya = parseInt(wilayat, 10);
                location = locationt
            }

            // Extract post date
            const dateLocator = item.locator('span.o-announ-card-date');
            if (await dateLocator.count() > 0) {
                let dateText = await dateLocator.innerText();
                dateText = dateText.trim().split(" ")
                if (dateText[dateText.length - 1].trim().toLowerCase() === "ans") {
                    postDate = new Date();
                    postDate.setFullYear(postDate.getFullYear() - Number(dateText[dateText.length - 2].trim()));
                } else if (dateText[dateText.length - 1].trim().toLowerCase() === "mois") {
                    postDate = new Date();
                    postDate.setMonth(postDate.getMonth() - Number(dateText[dateText.length - 2].trim()));
                } else if (dateText[dateText.length - 1].trim().toLowerCase() === "jours") {
                    postDate = new Date();
                    postDate.setDate(postDate.getDate() - Number(dateText[dateText.length - 2].trim()));
                } else if (dateText[dateText.length - 1].trim().toLowerCase() === "jour") {
                    postDate = new Date();
                    postDate.setDate(postDate.getDate() - Number(dateText[dateText.length - 2].trim()));
                } else if (dateText[dateText.length - 1].trim().toLowerCase() === "heures") {
                    postDate = new Date();
                    postDate.setHours(postDate.getHours() - Number(dateText[dateText.length - 2].trim()));
                } else if (dateText[dateText.length - 1].trim().toLowerCase() === "heure") {
                    postDate = new Date();
                    postDate.setHours(postDate.getHours() - Number(dateText[dateText.length - 2].trim()));
                } else if (dateText[dateText.length - 1].trim().toLowerCase() === "minutes") {
                    postDate = new Date();
                    postDate.setMinutes(postDate.getMinutes() - Number(dateText[dateText.length - 2].trim()));
                } else if (dateText[dateText.length - 1].trim().toLowerCase() === "minute") {
                    postDate = new Date();
                    postDate.setMinutes(postDate.getMinutes() - Number(dateText[dateText.length - 2].trim()));
                }

                if (postDate) postDate = postDate.toISOString().split("T")[0]
            }



            // Logging results
            console.log(href);
            console.log(`Listing ${i + 1}: ${titleText}`);
            console.log("Brand:", brand);
            console.log("Model:", model);
            console.log("Finition:", finition);
            console.log("Color:", color);
            console.log("Engine:", engine);
            console.log("Year:", year);
            console.log("Price:", price);
            console.log("Mileage:", mileage);
            console.log("Fuel:", fuel);
            console.log("GearBox:", gearBox);
            console.log("Paper:", paper);
            console.log("Location:", location);
            console.log("Wilaya:", wilaya);
            console.log("Date:", postDate);

            const existing = await Car.findOne({ where: { link: href } });

            if (existing) {
                // Only update if values actually changed
                const updated = await existing.update({
                    link: href,
                    title: titleText,
                    brand,
                    year,
                    model,
                    finition,
                    price,
                    mileage,
                    fuel,
                    gearbox: gearBox,
                    paper,
                    engine,
                    color,
                    location,
                    wilaya,
                    date: postDate
                });

                if (updated.changed().length > 0) {
                    console.log("♻️ Updated fields:", updated.changed());
                } else {
                    console.log("✅ No changes, skipped update.");
                }
            } else {
                await Car.create({
                    link: href,
                    title: titleText,
                    brand,
                    year,
                    model,
                    finition,
                    price,
                    mileage,
                    fuel,
                    gearbox: gearBox,
                    paper,
                    engine,
                    color,
                    location,
                    wilaya,
                    date: postDate
                });
                console.log("🚀 Inserted new car:", href);
            }

            console.log('------------')

        } catch (e) {
            console.log(`Error scraping listing ${i + 1}: ${e.message}`);
        }
    }


}

async function main(numberPages = 1, minPice = 50, maxPrice = 3000) {
    await sequelize.sync(); // ensure table is ready
    // Run the main function
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();
    for (let index = numberPages; index > 0; index--) {
        await scrapeOuedkniss(page, index, minPice, maxPrice);
    }

    // Close the browser
    // await browser.close();
    console.log("Scraping finished.");
}

main(2)
