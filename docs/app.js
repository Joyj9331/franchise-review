const GITHUB_CSV_URL = "https://raw.githubusercontent.com/Joyj9331/dalbitgo-review/main/%EA%B0%80%EB%A7%B9%EC%A0%90_%EB%A6%AC%EB%B7%B0%EC%88%98%EC%A7%91%EA%B2%B0%EA%B3%BC_%EB%88%84%EC%A0%81.csv";
let allData = [];

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    setupFilter();
});

async function loadData() {
    try {
        const response = await fetch(GITHUB_CSV_URL);
        const csvText = await response.text();
        
        Papa.parse(csvText, {
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
                allData = results.data;
                updateDashboard(allData);
                document.getElementById('lastUpdate').innerText = `최종 데이터 동기화: ${new Date().toLocaleString()}`;
            }
        });
    } catch (error) {
        console.error("데이터 로드 실패:", error);
        document.getElementById('lastUpdate').innerText = "⚠️ 데이터 로드 실패 (GitHub 주소 확인 필요)";
    }
}

function updateDashboard(data) {
    const totalCount = data.length;
    const posReviews = data.filter(r => r['감정분석'] === '긍정');
    const negReviews = data.filter(r => r['감정분석'] === '부정');
    const neuReviews = data.filter(r => r['감정분석'] === '중립');
    
    const posRate = ((posReviews.length / totalCount) * 100).toFixed(1);
    const storeNames = [...new Set(data.map(r => r['매장명']))];

    document.getElementById('totalReviews').innerText = totalCount.toLocaleString();
    document.getElementById('posRate').innerText = `${posRate}%`;
    document.getElementById('criticalCount').innerText = negReviews.length.toLocaleString();
    document.getElementById('storeCount').innerText = storeNames.length.toLocaleString();

    renderSentimentChart(posReviews.length, negReviews.length, neuReviews.length);
    renderTrendChart(data);
    renderStoreRanking(data);
    renderReviewFeed(data);
}

function renderSentimentChart(pos, neg, neu) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut', 
        data: {
            labels: ['긍정', '부정', '중립'],
            datasets: [{
                data: [pos, neg, neu],
                backgroundColor: ['#22c55e', '#ef4444', '#64748b'],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8' } }
            },
            cutout: '70%'
        }
    });
}

function renderTrendChart(data) {
    const monthlyData = {};
    data.forEach(r => {
        const month = r['작성일'].substring(0, 7); 
        monthlyData[month] = (monthlyData[month] || 0) + 1;
    });

    const labels = Object.keys(monthlyData).sort().slice(-6);
    const counts = labels.map(l => monthlyData[l]);

    const ctx = document.getElementById('trendChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '리뷰 발생량',
                data: counts,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            }
        }
    });
}

function renderStoreRanking(data) {
    const storeStats = {};
    data.forEach(r => {
        const store = r['매장명'];
        if (!storeStats[store]) storeStats[store] = { count: 0, pos: 0 };
        storeStats[store].count++;
        if (r['감정분석'] === '긍정') storeStats[store].pos++;
    });

    const sortedStores = Object.entries(storeStats)
        .sort((a, b) => b[1].count - a[1].count)
        .slice(0, 15);

    const container = document.getElementById('storeList');
    container.innerHTML = sortedStores.map(([name, stat], idx) => `
        <div class="flex items-center justify-between p-3 bg-slate-800/40 rounded-xl border border-slate-700 hover:border-blue-500 transition-colors cursor-pointer">
            <div class="flex items-center gap-3">
                <span class="text-xs font-bold text-slate-500 w-4">${idx + 1}</span>
                <span class="font-medium text-sm">${name}</span>
            </div>
            <div class="text-right">
                <p class="text-xs font-bold">${stat.count}건</p>
                <div class="w-16 h-1 bg-slate-700 rounded-full mt-1 overflow-hidden">
                    <div class="h-full bg-green-500" style="width: ${(stat.pos/stat.count*100)}%"></div>
                </div>
            </div>
        </div>
    `).join('');
}

function renderReviewFeed(data, filter = 'all') {
    const container = document.getElementById('reviewFeed');
    let displayData = [...data].sort((a, b) => new Date(b['작성일']) - new Date(a['작성일']));
    
    if (filter !== 'all') {
        displayData = displayData.filter(r => r['감정분석'] === filter);
    }

    container.innerHTML = displayData.slice(0, 50).map(r => `
        <div class="p-4 bg-slate-800/20 rounded-xl border ${r['감정분석'] === '부정' ? 'border-red-900/30 bg-red-900/5' : 'border-slate-800'}">
            <div class="flex justify-between items-start mb-2">
                <div>
                    <span class="text-xs font-bold text-blue-400">${r['매장명']}</span>
                    <span class="text-[10px] text-slate-500 ml-2">${r['작성일']}</span>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${getSentimentClass(r['감정분석'])}">
                    ${r['감정분석']}
                </span>
            </div>
            <p class="text-slate-300 leading-relaxed">${r['리뷰내용']}</p>
        </div>
    `).join('');
}

function getSentimentClass(sentiment) {
    if (sentiment === '긍정') return 'bg-green-900/40 text-green-400';
    if (sentiment === '부정') return 'bg-red-900/60 text-red-400';
    return 'bg-slate-700 text-slate-300';
}

function setupFilter() {
    const filter = document.getElementById('reviewFilter');
    if (filter) {
        filter.addEventListener('change', (e) => {
            renderReviewFeed(allData, e.target.value);
        });
    }
                       }
