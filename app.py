document.getElementById('predictForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const hours = parseFloat(document.getElementById('studyHours').value);
    const resultBox = document.getElementById('resultBox');
    
    resultBox.style.display = 'block';
    resultBox.className = 'result';
    resultBox.style.backgroundColor = '#e2e3e5';
    resultBox.style.color = '#383d41';
    resultBox.innerText = 'Predicting...';
    
    try {
        const response = await fetch('/predict-web', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `StudyHours=${hours}`
        });
        const data = await response.json();
        
        if(data.status === 'success') {
            // Prediction array ya single number dono format ko handle karne ke liye
            let predVal = Array.isArray(data.prediction) ? data.prediction[0] : data.prediction;
            predVal = Number(predVal);

            // Conditional Check for Pass / Fail
            if (predVal >= 1) {
                resultBox.className = 'result pass-badge';
                resultBox.innerText = 'Result: PASS 🎉';
            } else {
                resultBox.className = 'result fail-badge';
                resultBox.innerText = 'Result: FAIL ❌';
            }
        } else {
            resultBox.className = 'result fail-badge';
            resultBox.innerText = 'Error making prediction';
        }
    } catch (err) {
        resultBox.className = 'result fail-badge';
        resultBox.innerText = 'Server Error!';
    }
});