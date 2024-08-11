document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('file');
    const processType = document.getElementById('process_type').value;
    
    if (!fileInput.files.length) {
        alert("Please choose a file!");
        return;
    }

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const text = e.target.result;
        const pathsXYs = parseCSV(text);

        let processedPaths;
        switch (processType) {
            case 'symmetry':
                processedPaths = exploreSymmetry(pathsXYs);
                break;
            case 'regularize':
                processedPaths = regularizeCurves(pathsXYs);
                break;
            case 'complete':
                processedPaths = completeCurves(pathsXYs);
                break;
            default:
                processedPaths = pathsXYs;
        }

        const csvContent = generateCSV(processedPaths);
        const csvBlob = new Blob([csvContent], { type: 'text/csv' });
        const downloadLink = document.getElementById('download-link');
        downloadLink.href = URL.createObjectURL(csvBlob);
        downloadLink.download = 'processed_curves.csv';

        document.getElementById('results').style.display = 'block';

        plotCurves(processedPaths);
    };

    reader.readAsText(file);
});

function parseCSV(text) {
    const lines = text.trim().split('\n');
    const pathsXYs = [];

    let currentPath = [];
    let currentSubPath = [];
    let currentPathId = -1;
    let currentSubPathId = -1;

    for (const line of lines) {
        const [pathId, subPathId, pointId, x, y] = line.split(',').map(Number);
        
        if (pathId !== currentPathId) {
            if (currentSubPath.length > 0) {
                currentPath.push(currentSubPath);
            }
            if (currentPath.length > 0) {
                pathsXYs.push(currentPath);
            }
            currentPath = [];
            currentSubPath = [];
            currentPathId = pathId;
            currentSubPathId = -1;
        }

        if (subPathId !== currentSubPathId) {
            if (currentSubPath.length > 0) {
                currentPath.push(currentSubPath);
            }
            currentSubPath = [];
            currentSubPathId = subPathId;
        }

        currentSubPath.push([x, y]);
    }

    if (currentSubPath.length > 0) {
        currentPath.push(currentSubPath);
    }
    if (currentPath.length > 0) {
        pathsXYs.push(currentPath);
    }

    return pathsXYs;
}

function generateCSV(pathsXYs) {
    let csv = '';
    pathsXYs.forEach((path, pathIdx) => {
        path.forEach((subPath, subPathIdx) => {
            subPath.forEach((point, pointIdx) => {
                csv += `${pathIdx},${subPathIdx},${pointIdx},${point[0]},${point[1]}\n`;
            });
        });
    });
    return csv;
}

function exploreSymmetry(pathsXYs) {
    return pathsXYs.map(path => 
        path.map(subPath => 
            subPath.map(([x, y]) => [-x, y])
        )
    );
}

function regularizeCurves(pathsXYs) {
    // Placeholder for regularization logic
    return pathsXYs;
}

function completeCurves(pathsXYs) {
    // Placeholder for curve completion logic
    return pathsXYs;
}

function plotCurves(pathsXYs) {
    const canvas = document.getElementById('plot-canvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    pathsXYs.forEach(path => {
        path.forEach(subPath => {
            ctx.beginPath();
            subPath.forEach(([x, y], idx) => {
                const scaledX = (x + 100) * 2;
                const scaledY = (100 - y) * 2;
                if (idx === 0) {
                    ctx.moveTo(scaledX, scaledY);
                } else {
                    ctx.lineTo(scaledX, scaledY);
                }
            });
            ctx.stroke();
        });
    });
}
