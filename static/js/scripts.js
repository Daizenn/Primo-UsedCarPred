document.getElementById('predictor-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = $(this).serialize();

    $.ajax({
        url: '/predict',
        type: 'POST',
        data: formData,
        success: function(response) {
            if (response.predicted_price) {
                document.getElementById('result').innerHTML = `Predicted Price: ${response.predicted_price}`;
            } else {
                document.getElementById('result').innerHTML = 'An error occurred during prediction.';
            }
        },
        error: function() {
            document.getElementById('result').innerHTML = 'An error occurred during prediction.';
        }
    });
});

function updateKilometerValue(value) {
    document.getElementById('kilometerValue').innerText = value;
}

function updateMesinValue(value) {
    document.getElementById('mesinValue').innerText = value;
}

// Initial load values
document.addEventListener('DOMContentLoaded', function() {
    updateKilometerValue(document.getElementById('rangeSlider').value);
    updateMesinValue(document.getElementById('rangeSlider2').value);
});

document.addEventListener('DOMContentLoaded', function() {
    Papa.parse("/data/clean_data.csv", {
        download: true,
        header: true,
        complete: function(results) {
            const data = results.data;

            // Ambil elemen filter
            const yearFilter = document.getElementById('yearFilter');
            const typeFilter = document.getElementById('typeFilter');

            // Tambahkan opsi filter tahun dan jenis mobil
            const years = [...new Set(data.map(item => item.tahun_kendaraan))];
            const types = [...new Set(data.map(item => item.jenis_mobil))];

            years.forEach(year => {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                yearFilter.appendChild(option);
            });

            types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                typeFilter.appendChild(option);
            });

            // Fungsi untuk memperbarui chart berdasarkan filter
            function updateChart() {
                const yearValue = yearFilter.value;
                const typeValue = typeFilter.value;

                const filteredData = data.filter(item => {
                    const yearMatches = yearValue ? item.tahun_kendaraan === yearValue : true;
                    const typeMatches = typeValue ? item.jenis_mobil === typeValue : true;
                    return yearMatches && typeMatches;
                });

                const brandGroups = filteredData.reduce((acc, item) => {
                    const brand = item.brand;
                    const price = parseFloat(item.harga);
                    if (!acc[brand]) {
                        acc[brand] = [];
                    }
                    acc[brand].push(price);
                    return acc;
                }, {});

                // Calculate average price per brand
                const labels = Object.keys(brandGroups);
                const prices = labels.map(brand => {
                    const sum = brandGroups[brand].reduce((acc, price) => acc + price, 0);
                    const avg = sum / brandGroups[brand].length;
                    return avg;
                });

                // Update Bar Chart
                barChart.data.labels = labels;
                barChart.data.datasets[0].data = prices;
                barChart.data.datasets[0].backgroundColor = labels.map(() => `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.2)`);
                barChart.data.datasets[0].borderColor = labels.map(() => `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`);
                barChart.update();
            }

            // Initialize Bar Chart
            const barCtx = document.getElementById('barChart').getContext('2d');
            const barData = {
                labels: [],
                datasets: [{
                    label: 'Rata-rata Harga Mobil Bekas',
                    data: [],
                    backgroundColor: [],
                    borderColor: [],
                    borderWidth: 1
                }]
            };
            const barChart = new Chart(barCtx, {
                type: 'bar',
                data: barData,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            enabled: true,
                            mode: 'index',
                            intersect: false,
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'Rp ' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });

            // Tambahkan event listener untuk filter
            yearFilter.addEventListener('change', updateChart);
            typeFilter.addEventListener('change', updateChart);

            // Muat data awal dan perbarui chart
            updateChart();

            // Initialize Pie Chart
            const typeGroups = data.reduce((acc, item) => {
                const type = item.jenis_mobil;
                if (!acc[type]) {
                    acc[type] = 0;
                }
                acc[type] += 1;
                return acc;
            }, {});
            const typeLabels = Object.keys(typeGroups);
            const typeCounts = typeLabels.map(type => typeGroups[type]);

            const pieCtx = document.getElementById('pieChart').getContext('2d');
            const pieData = {
                labels: typeLabels,
                datasets: [{
                    label: 'Proporsi Jenis Mobil Bekas',
                    data: typeCounts,
                    backgroundColor: typeLabels.map(() => `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.5)`),
                    borderColor: typeLabels.map(() => `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`),
                    borderWidth: 1
                }]
            };
            new Chart(pieCtx, {
                type: 'pie',
                data: pieData,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(tooltipItem) {
                                    const label = pieData.labels[tooltipItem.dataIndex];
                                    const value = pieData.datasets[0].data[tooltipItem.dataIndex];
                                    return label + ': ' + value.toLocaleString() + ' unit';
                                }
                            }
                        }
                    },
                    layout: {
                        padding: 20
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true
                    }
                }
            });

            // Initialize Line Chart with Brand Filter
            const brands = [...new Set(data.map(item => item.brand))];
            const brandSelect = document.getElementById('brandSelect');
            brands.forEach(brand => {
                const option = document.createElement('option');
                option.value = brand;
                option.textContent = brand;
                brandSelect.appendChild(option);
            });

            const lineCtx = document.getElementById('lineChart').getContext('2d');
            const lineChart = new Chart(lineCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Rata-rata Harga Mobil Bekas',
                        data: [],
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Tahun'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'Rp ' + value.toLocaleString();
                                }
                            },
                            title: {
                                display: true,
                                text: 'Harga'
                            }
                        }
                    }
                }
            });

            function updateLineChart(brand) {
                const filteredData = data.filter(item => item.brand === brand);
                const yearGroups = filteredData.reduce((acc, item) => {
                    const year = item.tahun_kendaraan;
                    const price = parseFloat(item.harga);
                    if (!acc[year]) {
                        acc[year] = [];
                    }
                    acc[year].push(price);
                    return acc;
                }, {});

                const years = Object.keys(yearGroups);
                const averagePrices = years.map(year => {
                    const sum = yearGroups[year].reduce((acc, price) => acc + price, 0);
                    return sum / yearGroups[year].length;
                });

                lineChart.data.labels = years;
                lineChart.data.datasets[0].data = averagePrices;
                lineChart.update();
            }

            updateLineChart(brands[0]);

            brandSelect.addEventListener('change', function() {
                updateLineChart(this.value);
            });
        }
    });
});
