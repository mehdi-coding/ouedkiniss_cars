const fs = require('fs').promises;

async function mergeUniqueBrands() {
    try {
        // Read both files
        const [brands1Data, brands2Data] = await Promise.all([
            fs.readFile('Brands.txt', 'utf8'),
            fs.readFile('Brands2.txt', 'utf8')
        ]);

        // Split by newline, trim, convert to uppercase, and filter out empty lines
        const brands1 = brands1Data.split('\n')
            .map(brand => brand.trim().toUpperCase())
            .filter(brand => brand !== '');
        
        const brands2 = brands2Data.split('\n')
            .map(brand => brand.trim().toUpperCase())
            .filter(brand => brand !== '');

        // Combine and get unique brands
        const allBrands = [...brands1, ...brands2];
        const uniqueBrands = [...new Set(allBrands)];

        // Sort alphabetically
        uniqueBrands.sort();

        // Write to new file
        await fs.writeFile('UniqueBrands.txt', uniqueBrands.join('\n'));

        // Log results
        console.log('=== Merge Results ===');
        console.log(`Brands in Brands.txt: ${brands1.length}`);
        console.log(`Brands in Brands2.txt: ${brands2.length}`);
        console.log(`Total unique brands: ${uniqueBrands.length}`);
        console.log(`Duplicates removed: ${allBrands.length - uniqueBrands.length}`);
        console.log('File saved as: UniqueBrands.txt');

    } catch (error) {
        console.error('Error processing files:', error.message);
    }
}

// Execute the function
mergeUniqueBrands();