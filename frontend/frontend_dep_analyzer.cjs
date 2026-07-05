const fs = require('fs');
const path = require('path');

function analyzeFrontend(dir, base, deps = {}) {
    if (!fs.existsSync(dir)) return deps;
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            analyzeFrontend(fullPath, base, deps);
        } else if (file.endsWith('.ts') || file.endsWith('.tsx')) {
            const content = fs.readFileSync(fullPath, 'utf8');
            const imports = [];
            const importRegex = /import\s+.*?from\s+['"](.*?)['"]/g;
            let match;
            while ((match = importRegex.exec(content)) !== null) {
                if (match[1].startsWith('.') || match[1].startsWith('@/')) {
                    imports.push(match[1]);
                }
            }
            const relPath = path.relative(base, fullPath);
            deps[relPath] = imports;
        }
    }
    return deps;
}

const deps = analyzeFrontend(path.join(__dirname, 'src'), path.join(__dirname, 'src'));
for (const [mod, imports] of Object.entries(deps)) {
    console.log(`${mod} -> ${JSON.stringify(imports)}`);
}
