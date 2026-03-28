// 달빛에구운고등어 마케팅 대시보드 (v2.0) 통합 로직
const GITHUB_REVIEW_CSV = "https://raw.githubusercontent.com/Joyj9331/dalbitgo-review/main/%EA%B0%80%EB%A7%B9%EC%A0%90_%EB%A6%AC%EB%B7%B0%EC%88%98%EC%A7%91%EA%B2%B0%EA%B3%BC_%EB%88%84%EC%A0%81.csv";
const GITHUB_SEO_CSV = "https://raw.githubusercontent.com/Joyj9331/dalbitgo-review/main/data/processed/seo_analysis_result.csv";
let reviewData = [];
let seoData = [];
document.addEventListener('DOMContentLoaded', () => {
    loadReviewData();
    loadSeoData();
    setupFilter();
});
function switchTab(tab) {
    const reviewTab = document.getElementById('reviewTab');
    const seoTab = document.getElementById('seoTab');
    const btnReview = document.getElementById('btnReview');
    const btnSeo = document.getElementById('btnSeo');
    if (tab === 'review') {
        reviewTab.classList.remove('hidden');
        seoTab.classList.add('hidden');
        btnReview.classList.add('bg-blue-600', 'text-white');
        btnReview.classList.remove('text-slate-400');
        btnSeo.classList.remove('bg-blue-600', 'text-white');
        btnSeo.classList.add('text-slate-400');
    } else {
        reviewTab.classList.add('hidden');
        seoTab.classList.remove('hidden');
        btnSeo.classList.add('bg-blue-600', 'text-white');
        btnSeo.classList.remove('text-slate-400');
        btnReview.classList.remove('bg-blue-600', 'text-white');
        btnReview.classList.add('text-slate-400');
    }
}
async function loadReviewData() {
    try {
        const response = await fetch(GITHUB_REVIEW_CSV);
        const csvText = await response.text();
        Papa.parse(csvText, {
            header: true, skipEmptyLines: true,
            complete: (res) => {
                reviewData = res.data;
                updateReviewDashboard(reviewData);
                document.getElementById('lastUpdate').innerText = `최종 동기화: ${new Date().toLocaleString()}`;
            }
        });
    } catch (e) {
        console.error("Review 로드 실패", e);
    }
}
async function loadSeoData() {
    try {
        const response = await fetch(GITHUB_SEO_CSV);
        if (!response.ok) throw new Error("SEO data not found");
        const csvText = await response.text();
        Papa.parse(csvText, {
            header: true, skipEmptyLines: true,
            complete: (res) => {
                seoData = res.data;
                updateSeoDashboard(seoData);
            }
        });
    } catch (e) {
        console.warn("SEO 데이터 미발견", e);
        document.getElementById('seoList').innerHTML = '<div class="text-center py-20 text-slate-500">SEO 데이터가 아직 업로드되지 않았습니다.</div>';
    }
}
function updateReviewDashboard(data) {
    const totalCount = data.length;
    const posReviews = data.filter(r => r['감정분석'] === '긍정');
    const negReviews = data.filter(r => r['감정분석'] === '부정');
    const neuReviews = data.filter(r => r['감정분석'] === '중립');
    document.getElementById('totalReviews').innerText = totalCount.toLocaleString();
    document.getElementById('posRate').innerText = `${((posReviews.length / totalCount) * 100).toFixed(1)}%`;
    document.getElementById('criticalCount').innerText = negReviews.length.toLocaleString();
    document.getElementById('storeCount').innerText = [...new Set(data.map(r => r['매장명']))].length.toLocaleString();
    renderSentimentChart(posReviews.length, negReviews.length, neuReviews.length);
    renderTrendChart(data);
    renderStoreRanking(data);
    renderReviewFeed(data);
}
function updateSeoDashboard(data) {
    const avgScore = data.reduce((acc, curr) => acc + parseInt(curr.SEO점수), 0) / data.length;
    const optimized = data.filter(s => parseInt(s.SEO점수) >= 75).length;
    const low = data.filter(s => parseInt(s.SEO점수) < 50).length;
    document.getElementById('avgSeoScore').innerText = `${avgScore.toFixed(0)}점`;
    document.getElementById('optimizedCount').innerText = `${optimized}개`;
    document.getElementById('lowScoreCount').innerText = `${low}개`;
    const container = document.getElementById('seoList');
    container.innerHTML = data.map(s => `
        <div class="p-6 bg-slate-800/20 rounded-2xl border border-slate-700 hover:border-blue-500/50 transition-all">
            <div class="flex flex-col md:flex-row justify-between gap-6">
                <div class="md:w-1/3">
                    <div class="flex items-center gap-3 mb-4">
                        <span class="text-xl font-bold">${s.매장명}</span>
                        <span class="px-2 py-1 rounded-lg text-xs font-bold ${parseInt(s.SEO점수) >= 75 ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'}">
                            ${s.SEO점수}점
                        </span>
                    </div>
                    <div class="space-y-2">
                        <div class="flex justify-between text-sm"><span class="text-slate-500">지역 핵심 키워드</span><span class="text-blue-400 font-bold">${s.지역키워드 || '추출중'}</span></div>
                        <div class="text-xs text-slate-400 mt-2">${s.추천태그.split('|').map(t => `<span class="inline-block mr-2 mb-1">#${t}</span>`).join('')}</div>
                    </div>
                </div>
                <div class="md:w-2/3 border-t md:border-t-0 md:border-l border-slate-700 md:pl-6 pt-4 md:pt-0">
                    <h5 class="text-sm font-bold text-yellow-500 mb-2">✨ AI 추천 마케팅 문구</h5>
                    <p class="text-sm text-slate-300 italic bg-slate-900/50 p-4 rounded-xl">"${s.AI추천문구}"</p>
                    <button onclick="copyToClipboard('${s.AI추천문구}')" class="mt-4 text-[10px] text-slate-500 hover:text-white underline">문구 복사하기</button>
                </div>
            </div>
        </div>
    `).join('');
}
function renderSentimentChart(pos, neg, neu) {
    const canvas = document.getElementById('sentimentChart'); if (!canvas) return;
    const ctx = canvas.getContext('2d'); if (window.sChart) window.sChart.destroy();
    window.sChart = new Chart(ctx, { type: 'doughnut', data: { labels: ['긍정', '부정', '중립'], datasets: [{ data: [pos, neg, neu], backgroundColor: ['#22c55e', '#ef4444', '#64748b'], borderWidth: 0 }] }, options: { maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }, cutout: '70%' } });
}
function renderTrendChart(data) {
    const canvas = document.getElementById('trendChart'); if (!canvas) return;
    const monthlyData = {}; data.forEach(r => { const month = r['작성일'].substring(0, 7); monthlyData[month] = (monthlyData[month] || 0) + 1; });
    const labels = Object.keys(monthlyData).sort().slice(-6);
    const ctx = canvas.getContext('2d'); if (window.tChart) window.tChart.destroy();
    window.tChart = new Chart(ctx, { type: 'line', data: { labels: labels, datasets: [{ label: '리뷰', data: labels.map(l => monthlyData[l]), borderColor: '#6366f1', fill: true, tension: 0.4 }] }, options: { maintainAspectRatio: false, plugins: { legend: { display: false } } } });
}
function renderStoreRanking(data) {
    const stats = {}; data.forEach(r => { const s = r['매장명']; if (!stats[s]) stats[s] = { c: 0, p: 0 }; stats[s].c++; if (r['감정분석'] === '긍정') stats[s].p++; });
    const sorted = Object.entries(stats).sort((a,b)=>b[1].c-a[1].c).slice(0, 15);
    document.getElementById('storeList').innerHTML = sorted.map(([n,s],i)=>`<div class="flex items-center justify-between p-3 bg-slate-800/40 rounded-xl border border-slate-700"><span class="text-sm font-medium">${n}</span><span class="text-xs font-bold">${s.c}건</span></div>`).join('');
}
function renderReviewFeed(data, filter = 'all') {
    const container = document.getElementById('reviewFeed');
    let display = [...data].sort((a,b)=>new Date(b['작성일'])-new Date(a['작성일']));
    if (filter!=='all') display = display.filter(r=>r['감정분석']===filter);
    container.innerHTML = display.slice(0, 50).map(r=>`<div class="p-4 bg-slate-800/20 rounded-xl border border-slate-800 mb-4"><p class="text-slate-300 text-xs">${r['리뷰내용']}</p></div>`).join('');
}
function setupFilter() { const f = document.getElementById('reviewFilter'); if (f) f.addEventListener('change', (e) => renderReviewFeed(reviewData, e.target.value)); }
function copyToClipboard(text) { navigator.clipboard.writeText(text).then(() => alert("복사되었습니다!")); }
