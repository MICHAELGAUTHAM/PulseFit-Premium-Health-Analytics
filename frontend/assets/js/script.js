/* ==========================================================================
   PulseFit Dashboard Interactive Logic (Full-Stack Integrated)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Core State Definition
    let healthData = {
        water: 0, // ml
        waterGoal: 2500, // ml
        steps: 0,
        stepsGoal: 10000,
        calories: 0,
        caloriesGoal: 2400,
        sleepHours: 0.0,
        sleepScore: 0,
        heartRate: 72,
        height: 175, // cm
        weight: 70, // kg
    };

    let weeklyChartInstance = null;
    let heartChartInstance = null;

    // 2. DOM Cache References
    const navLinks = document.querySelectorAll('.nav-link');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const settingsDarkMode = document.getElementById('settings-dark-mode');
    
    const heightSlider = document.getElementById('bmi-height');
    const weightSlider = document.getElementById('bmi-weight');
    const heightLbl = document.getElementById('height-lbl');
    const weightLbl = document.getElementById('weight-lbl');
    const bmiVal = document.getElementById('val-bmi');
    const bmiStatus = document.getElementById('val-bmi-status');
    const bmiFeedback = document.getElementById('bmi-feedback');
    const bmiNeedle = document.getElementById('bmi-needle');

    const quickAddButtons = document.querySelectorAll('.btn-quick-add');
    const waterIntakeVal = document.getElementById('water-intake-val');
    const vesselPercentage = document.getElementById('vessel-percentage');
    const waterLevelWaves = document.getElementById('water-level-waves');
    const valWaterQuick = document.getElementById('val-water-quick');
    const valWaterPct = document.getElementById('val-water-pct');
    const progressWaterBar = document.getElementById('progress-water-bar');

    const ringSteps = document.getElementById('ring-steps');
    const ringCalories = document.getElementById('ring-calories');
    const ringWater = document.getElementById('ring-water');
    const legendStepsVal = document.getElementById('legend-steps-val');
    const legendCaloriesVal = document.getElementById('legend-calories-val');
    const legendWaterVal = document.getElementById('legend-water-val');
    const ringsPercentageLabel = document.getElementById('rings-percentage');

    const valHeart = document.getElementById('val-heart');
    const btnResetData = document.getElementById('btn-reset-data');

    // 3. API Integration Helpers

    // Load metrics from backend
    async function loadDashboardData() {
        try {
            const token = localStorage.getItem('pulsefit_token') || sessionStorage.getItem('pulsefit_token');
            if (!token) return; // Wait for login

            const res = await apiFetch('/dashboard');
            if (res.ok) {
                const data = await res.json();
                
                healthData.heartRate = data.heart_rate;
                healthData.water = data.water_intake;
                healthData.steps = data.steps;
                healthData.calories = data.calories;
                healthData.sleepHours = data.sleep_hours;
                healthData.sleepScore = data.sleep_score;

                // Configure goal targets from backend
                data.goals.forEach(g => {
                    if (g.type === 'water') healthData.waterGoal = g.target_value;
                    if (g.type === 'steps') healthData.stepsGoal = g.target_value;
                    if (g.type === 'calories') healthData.caloriesGoal = g.target_value;
                    if (g.type === 'sleep') healthData.sleepGoal = g.target_value;
                });

                // Update physical heights/weights from profile
                const profileRes = await apiFetch('/auth/profile');
                if (profileRes.ok) {
                    const user = await profileRes.json();
                    healthData.height = user.height || 175;
                    healthData.weight = user.weight || 70;
                    
                    if (heightSlider && weightSlider) {
                        heightSlider.value = healthData.height;
                        weightSlider.value = healthData.weight;
                    }
                }

                // Render metrics to UI
                updateUIElements();
            }
        } catch (e) {
            console.error('Failed to load dashboard metrics:', e);
        }
    }

    // Refresh UI elements
    function updateUIElements() {
        if (valHeart) valHeart.textContent = healthData.heartRate;
        
        // Steps updates
        const stepsEl = document.getElementById('val-steps');
        if (stepsEl) {
            stepsEl.textContent = healthData.steps.toLocaleString();
            stepsEl.setAttribute('data-target', healthData.steps);
        }
        const stepsBar = document.getElementById('progress-steps-bar');
        if (stepsBar) {
            const stepsPct = Math.min(100, (healthData.steps / healthData.stepsGoal) * 100);
            stepsBar.style.width = `${stepsPct}%`;
            stepsBar.parentElement.nextElementSibling.children[1].textContent = `${stepsPct.toFixed(1)}%`;
            stepsBar.parentElement.nextElementSibling.children[0].textContent = `Goal: ${healthData.stepsGoal.toLocaleString()}`;
        }

        // Calories updates
        const calEl = document.getElementById('val-calories');
        if (calEl) {
            calEl.textContent = healthData.calories.toLocaleString();
            calEl.setAttribute('data-target', healthData.calories);
        }
        const calBar = document.getElementById('progress-calories-bar');
        if (calBar) {
            const calPct = Math.min(100, (healthData.calories / healthData.caloriesGoal) * 100);
            calBar.style.width = `${calPct}%`;
            calBar.parentElement.nextElementSibling.children[1].textContent = `${calPct.toFixed(1)}%`;
            calBar.parentElement.nextElementSibling.children[0].textContent = `Goal: ${healthData.caloriesGoal.toLocaleString()} kcal`;
        }

        // Sleep updates
        const sleepHrs = document.getElementById('val-sleep-hours');
        if (sleepHrs) sleepHrs.textContent = healthData.sleepHours;
        const sleepScore = document.getElementById('val-sleep-score');
        if (sleepScore) sleepScore.textContent = `${healthData.sleepScore}%`;

        // Update gauges and sliders
        calculateBMI(false);
        updateWaterVisuals(0);
        updateRadialRings();
    }

    // 4. Dynamic Helper Functions
    
    // Number Counting Animation
    const animateNumbers = () => {
        const counters = document.querySelectorAll('.animate-number');
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            if (!target) return;
            const duration = 1200; // ms
            const stepTime = 15;
            const stepValue = target / (duration / stepTime);
            
            let current = 0;
            const timer = setInterval(() => {
                current += stepValue;
                if (current >= target) {
                    counter.textContent = Math.round(target).toLocaleString();
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.round(current).toLocaleString();
                }
            }, stepTime);
        });
    };

    // Theme Management
    const setTheme = (isDark) => {
        if (isDark) {
            document.body.classList.remove('light-theme');
            document.body.classList.add('dark-theme');
            if (settingsDarkMode) settingsDarkMode.checked = true;
            localStorage.setItem('pulsefit-theme', 'dark');
        } else {
            document.body.classList.remove('dark-theme');
            document.body.classList.add('light-theme');
            if (settingsDarkMode) settingsDarkMode.checked = false;
            localStorage.setItem('pulsefit-theme', 'light');
        }
        
        updateChartsTheme(isDark);
    };

    // BMI Calculator
    const calculateBMI = async (isChange = false) => {
        if (!heightSlider || !weightSlider) return;
        
        const h = parseInt(heightSlider.value);
        const w = parseInt(weightSlider.value);

        if (heightLbl) heightLbl.textContent = `${h} cm`;
        if (weightLbl) weightLbl.textContent = `${w} kg`;

        const bmi = (w / ((h / 100) ** 2)).toFixed(1);
        if (bmiVal) bmiVal.textContent = bmi;

        // Needle rotation angle
        let angle = ((bmi - 15) / 20) * 120 - 60;
        angle = Math.max(-75, Math.min(75, angle));
        if (bmiNeedle) bmiNeedle.style.transform = `rotate(${angle}deg)`;

        let text = "";
        let status = "";

        if (bmi < 18.5) {
            status = "Underweight";
            text = "Your weight is lower than optimal. Consider increasing nutrient-rich foods.";
            if (bmiStatus) bmiStatus.style.color = "var(--accent-color)";
        } else if (bmi >= 18.5 && bmi < 25) {
            status = "Normal Weight";
            text = "You have a healthy body weight. Maintain physical activity & hydration.";
            if (bmiStatus) bmiStatus.style.color = "var(--success-color)";
        } else if (bmi >= 25 && bmi < 30) {
            status = "Overweight";
            text = "Your weight is slightly above average. Regular cardiovascular exercise is recommended.";
            if (bmiStatus) bmiStatus.style.color = "var(--warning-color)";
        } else {
            status = "Obese";
            text = "Consider seeking professional nutritional and fitness advice for heart health.";
            if (bmiStatus) bmiStatus.style.color = "var(--danger-color)";
        }

        if (bmiStatus) bmiStatus.textContent = status;
        if (bmiFeedback) bmiFeedback.querySelector('span').textContent = text;

        if (isChange) {
            try {
                const res = await apiFetch('/bmi/calculate', {
                    method: 'POST',
                    body: JSON.stringify({ height: h, weight: w })
                });
                if (res.ok) {
                    showToast('Height & Weight biometrics saved to database.', 'success');
                    healthData.height = h;
                    healthData.weight = w;
                }
            } catch (err) {
                console.error("Failed to post BMI:", err);
            }
        }
    };

    // Confetti Celebration
    const triggerConfetti = () => {
        if (typeof confetti === 'function') {
            confetti({
                particleCount: 150,
                spread: 80,
                origin: { y: 0.6 },
                colors: ['#00E5FF', '#2563EB', '#7C3AED', '#10B981']
            });
        }
    };

    // Update Radial Goal Rings
    const updateRadialRings = () => {
        const stepsPct = Math.min(100, Math.round((healthData.steps / healthData.stepsGoal) * 100)) || 0;
        const caloriesPct = Math.min(100, Math.round((healthData.calories / healthData.caloriesGoal) * 100)) || 0;
        const waterPct = Math.min(100, Math.round((healthData.water / healthData.waterGoal) * 100)) || 0;

        if (ringSteps) {
            const offsetSteps = 502 - (502 * stepsPct) / 100;
            ringSteps.style.strokeDashoffset = offsetSteps;
        }
        if (ringCalories) {
            const offsetCalories = 377 - (377 * caloriesPct) / 100;
            ringCalories.style.strokeDashoffset = offsetCalories;
        }
        if (ringWater) {
            const offsetWater = 251 - (251 * waterPct) / 100;
            ringWater.style.strokeDashoffset = offsetWater;
        }

        if (legendStepsVal) legendStepsVal.textContent = `${stepsPct}%`;
        if (legendCaloriesVal) legendCaloriesVal.textContent = `${caloriesPct}%`;
        if (legendWaterVal) legendWaterVal.textContent = `${waterPct}%`;

        const avgPct = Math.round((stepsPct + caloriesPct + waterPct) / 3);
        if (ringsPercentageLabel) {
            ringsPercentageLabel.textContent = `${avgPct}%`;
        }
    };

    // Update Water Intake
    const updateWaterVisuals = async (amountToAdd = 0) => {
        if (amountToAdd > 0) {
            try {
                const res = await apiFetch('/water/add', {
                    method: 'POST',
                    body: JSON.stringify({ amount: amountToAdd })
                });
                if (res.ok) {
                    const data = await res.json();
                    healthData.water = data.water_intake;
                }
            } catch (err) {
                console.error('Failed to log water intake:', err);
                showToast('Failed to log hydration to server.', 'error');
                return;
            }
        }

        const pct = Math.min(100, Math.round((healthData.water / healthData.waterGoal) * 100));
        
        if (waterIntakeVal) waterIntakeVal.textContent = `${(healthData.water / 1000).toFixed(2)}L`;
        if (vesselPercentage) vesselPercentage.textContent = `${pct}%`;
        if (valWaterQuick) valWaterQuick.textContent = healthData.water;
        if (valWaterPct) valWaterPct.textContent = `${pct}%`;
        
        if (progressWaterBar) progressWaterBar.style.width = `${pct}%`;

        const translateY = 100 - pct;
        if (waterLevelWaves) {
            waterLevelWaves.style.transform = `translateY(${translateY}%)`;
        }

        updateRadialRings();

        if (pct >= 100 && amountToAdd > 0) {
            triggerConfetti();
        }
    };

    // Chart.js Helpers
    const getChartTextColors = (isDark) => {
        return isDark ? '#94A3B8' : '#475569';
    };

    const getChartGridColors = (isDark) => {
        return isDark ? 'rgba(255, 255, 255, 0.04)' : 'rgba(0, 0, 0, 0.04)';
    };

    const updateChartsTheme = (isDark) => {
        const textColor = getChartTextColors(isDark);
        const gridColor = getChartGridColors(isDark);

        if (weeklyChartInstance) {
            weeklyChartInstance.options.scales.x.grid.color = gridColor;
            weeklyChartInstance.options.scales.x.ticks.color = textColor;
            weeklyChartInstance.options.scales.y.grid.color = gridColor;
            weeklyChartInstance.options.scales.y.ticks.color = textColor;
            weeklyChartInstance.options.plugins.tooltip.backgroundColor = isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)';
            weeklyChartInstance.options.plugins.tooltip.titleColor = isDark ? '#fff' : '#000';
            weeklyChartInstance.options.plugins.tooltip.bodyColor = isDark ? '#94A3B8' : '#475569';
            weeklyChartInstance.options.plugins.tooltip.borderColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)';
            weeklyChartInstance.update();
        }
    };

    const initializeCharts = async () => {
        const isDark = document.body.classList.contains('dark-theme');
        const textColor = getChartTextColors(isDark);
        const gridColor = getChartGridColors(isDark);

        let labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        let scoreData = [82, 85, 78, 88, 91, 94, 90];
        let activityData = [70, 75, 68, 85, 80, 95, 88];

        try {
            const token = localStorage.getItem('pulsefit_token') || sessionStorage.getItem('pulsefit_token');
            if (token) {
                const res = await apiFetch('/analytics/weekly');
                if (res.ok) {
                    const data = await res.json();
                    labels = data.labels;
                    scoreData = data.health_score;
                    activityData = data.activity;
                }
            }
        } catch (e) {
            console.error('Failed to load weekly chart analytics:', e);
        }

        // A. Weekly Area Chart
        const ctxWeekly = document.getElementById('chart-weekly-progress');
        if (ctxWeekly) {
            const primaryGrad = ctxWeekly.getContext('2d').createLinearGradient(0, 0, 0, 200);
            primaryGrad.addColorStop(0, 'rgba(37, 99, 235, 0.3)');
            primaryGrad.addColorStop(1, 'rgba(37, 99, 235, 0)');

            const accentGrad = ctxWeekly.getContext('2d').createLinearGradient(0, 0, 0, 200);
            accentGrad.addColorStop(0, 'rgba(0, 229, 255, 0.3)');
            accentGrad.addColorStop(1, 'rgba(0, 229, 255, 0)');

            weeklyChartInstance = new Chart(ctxWeekly, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Overall Score',
                            data: scoreData,
                            borderColor: '#2563EB',
                            borderWidth: 3,
                            backgroundColor: primaryGrad,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointBackgroundColor: '#2563EB',
                            pointHoverRadius: 6,
                        },
                        {
                            label: 'Activity level',
                            data: activityData,
                            borderColor: '#00E5FF',
                            borderWidth: 3,
                            backgroundColor: accentGrad,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointBackgroundColor: '#00E5FF',
                            pointHoverRadius: 6,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                            titleColor: isDark ? '#fff' : '#000',
                            bodyColor: isDark ? '#94A3B8' : '#475569',
                            borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
                            borderWidth: 1,
                            cornerRadius: 12,
                            padding: 12,
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: gridColor },
                            ticks: {
                                color: textColor,
                                font: { family: 'Plus Jakarta Sans', weight: 600 }
                            }
                        },
                        y: {
                            grid: { color: gridColor },
                            ticks: {
                                color: textColor,
                                font: { family: 'Plus Jakarta Sans', weight: 600 }
                            },
                            min: 0,
                            max: 100
                        }
                    }
                }
            });
        }

        // B. Heart Rate Mini Live-Fluctuating Area Chart
        const ctxHeart = document.getElementById('chart-heart-mini');
        if (ctxHeart) {
            const heartGrad = ctxHeart.getContext('2d').createLinearGradient(0, 0, 0, 80);
            heartGrad.addColorStop(0, 'rgba(239, 68, 68, 0.25)');
            heartGrad.addColorStop(1, 'rgba(239, 68, 68, 0)');

            heartChartInstance = new Chart(ctxHeart, {
                type: 'line',
                data: {
                    labels: ['', '', '', '', '', '', '', '', '', ''],
                    datasets: [{
                        data: [72, 74, 71, 73, 75, 72, 70, 72, 73, 72],
                        borderColor: '#EF4444',
                        borderWidth: 2,
                        backgroundColor: heartGrad,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: false }
                    },
                    scales: {
                        x: { display: false },
                        y: { display: false }
                    }
                }
            });
        }
    };


    // 5. Hook Event Listeners
    
    // Smooth scrolling & tab highlighting
    window.addEventListener('scroll', () => {
        let currentSection = '';
        const sections = document.querySelectorAll('section');
        const scrollPosition = window.scrollY + 150;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                currentSection = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSection}`) {
                link.classList.add('active');
            }
        });
    });

    // Card Specific Radial Highlight
    const cards = document.querySelectorAll('.glass-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--glow-x', `${x}px`);
            card.style.setProperty('--glow-y', `${y}px`);
        });
    });

    // Button Ripple Effects
    document.querySelectorAll('.btn-ripple').forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            this.appendChild(ripple);
            setTimeout(() => { ripple.remove(); }, 600);
        });
    });

    // BMI range sliders
    if (heightSlider && weightSlider) {
        heightSlider.addEventListener('input', () => calculateBMI(false));
        weightSlider.addEventListener('input', () => calculateBMI(false));
        
        heightSlider.addEventListener('change', () => calculateBMI(true));
        weightSlider.addEventListener('change', () => calculateBMI(true));
    }

    // Water quick-add buttons
    quickAddButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const amount = parseInt(btn.getAttribute('data-amount'));
            updateWaterVisuals(amount);
        });
    });

    // Reset settings button (local / api reset)
    if (btnResetData) {
        btnResetData.addEventListener('click', async () => {
            const confirmReset = confirm("Are you sure you want to reset all tracker logs? This will erase today's biometrics.");
            if (confirmReset) {
                try {
                    const res = await apiFetch('/health', {
                        method: 'POST',
                        body: JSON.stringify({
                            water_intake: 0,
                            steps: 0,
                            calories: 0,
                            sleep_hours: 0.0,
                            sleep_score: 0,
                            heart_rate: 72
                        })
                    });
                    if (res.ok) {
                        showToast('Biometrics reset successfully.', 'success');
                        loadDashboardData();
                    }
                } catch (e) {
                    showToast('Failed to reset logs.', 'error');
                }
            }
        });
    }

    // Add interactive click logging on Cards (Steps, Calories, Sleep)
    const cardSteps = document.getElementById('card-steps');
    if (cardSteps) {
        cardSteps.style.cursor = 'pointer';
        cardSteps.addEventListener('click', async (e) => {
            // Avoid triggering when clicking buttons/progress inside if any
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'A') return;
            const stepsInput = prompt("Log steps walked today:", healthData.steps);
            if (stepsInput !== null) {
                const stepsCount = parseInt(stepsInput);
                if (isNaN(stepsCount) || stepsCount < 0) {
                    showToast('Please enter a valid positive number.', 'error');
                    return;
                }
                try {
                    const res = await apiFetch('/steps', {
                        method: 'POST',
                        body: JSON.stringify({ steps: stepsCount })
                    });
                    if (res.ok) {
                        showToast('Steps logged successfully!', 'success');
                        healthData.steps = stepsCount;
                        updateUIElements();
                    }
                } catch (err) {
                    showToast('Failed to save steps.', 'error');
                }
            }
        });
    }

    const cardCalories = document.getElementById('card-calories');
    if (cardCalories) {
        cardCalories.style.cursor = 'pointer';
        cardCalories.addEventListener('click', async (e) => {
            const calInput = prompt("Log calories burned today (kcal):", healthData.calories);
            if (calInput !== null) {
                const calCount = parseInt(calInput);
                if (isNaN(calCount) || calCount < 0) {
                    showToast('Please enter a valid positive calorie count.', 'error');
                    return;
                }
                try {
                    const res = await apiFetch('/calories', {
                        method: 'POST',
                        body: JSON.stringify({ calories: calCount })
                    });
                    if (res.ok) {
                        showToast('Calories logged successfully!', 'success');
                        healthData.calories = calCount;
                        updateUIElements();
                    }
                } catch (err) {
                    showToast('Failed to save calories.', 'error');
                }
            }
        });
    }

    const cardSleep = document.getElementById('card-sleep');
    if (cardSleep) {
        cardSleep.style.cursor = 'pointer';
        cardSleep.addEventListener('click', async () => {
            const hoursInput = prompt("Log sleep duration today (hours):", healthData.sleepHours);
            if (hoursInput !== null) {
                const hours = parseFloat(hoursInput);
                if (isNaN(hours) || hours < 0 || hours > 24) {
                    showToast('Please enter valid sleep hours (0-24).', 'error');
                    return;
                }
                const scoreInput = prompt("Log sleep quality score (0-100%):", healthData.sleepScore);
                if (scoreInput !== null) {
                    const score = parseInt(scoreInput);
                    if (isNaN(score) || score < 0 || score > 100) {
                        showToast('Please enter a valid quality score (0-100).', 'error');
                        return;
                    }
                    try {
                        const res = await apiFetch('/sleep', {
                            method: 'POST',
                            body: JSON.stringify({ hours: hours, score: score })
                        });
                        if (res.ok) {
                            showToast('Sleep metrics logged successfully!', 'success');
                            healthData.sleepHours = hours;
                            healthData.sleepScore = score;
                            updateUIElements();
                        }
                    } catch (err) {
                        showToast('Failed to save sleep metrics.', 'error');
                    }
                }
            }
        });
    }

    // 6. Initial Run & Setups
    
    // Load dashboard metrics
    loadDashboardData();

    // Trigger Lucide SVG replacements
    if (window.lucide) lucide.createIcons();

    // Render Chart.js items
    initializeCharts();

    // Set intervals for resting heart rate micro-fluctuations
    setInterval(() => {
        const deviation = Math.floor(Math.random() * 5) - 2;
        let currentBpm = healthData.heartRate + deviation;
        currentBpm = Math.max(65, Math.min(85, currentBpm));

        if (valHeart) valHeart.textContent = currentBpm;

        if (heartChartInstance) {
            const data = heartChartInstance.data.datasets[0].data;
            data.shift();
            data.push(currentBpm);
            heartChartInstance.update('none'); // Update smoothly
        }
    }, 2500);
});
