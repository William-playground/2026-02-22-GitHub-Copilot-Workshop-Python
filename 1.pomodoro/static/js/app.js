// ポモドーロタイマー - フロントエンドロジック
"use strict";

// --- 状態 ---
let timerInterval = null;
let timeLeft = 25 * 60;
let isRunning = false;
let currentMinutes = 25;
let statsChart = null;
let currentChartType = "weekly";

// --- DOM要素 ---
const timerDisplay = document.getElementById("timer-display");
const startBtn = document.getElementById("start-btn");
const resetBtn = document.getElementById("reset-btn");
const modeButtons = document.querySelectorAll(".mode-btn");
const chartTabs = document.querySelectorAll(".chart-tab");
const badgesGrid = document.getElementById("badges-grid");
const notification = document.getElementById("badge-notification");

// --- タイマー ---
function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function updateDisplay() {
  timerDisplay.textContent = formatTime(timeLeft);
  document.title = `${formatTime(timeLeft)} - ポモドーロ`;
}

function startTimer() {
  if (isRunning) {
    clearInterval(timerInterval);
    isRunning = false;
    startBtn.textContent = "再開";
    return;
  }
  isRunning = true;
  startBtn.textContent = "一時停止";
  timerInterval = setInterval(() => {
    timeLeft--;
    updateDisplay();
    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      isRunning = false;
      startBtn.textContent = "開始";
      onTimerComplete();
    }
  }, 1000);
}

function resetTimer() {
  clearInterval(timerInterval);
  isRunning = false;
  timeLeft = currentMinutes * 60;
  startBtn.textContent = "開始";
  updateDisplay();
}

async function onTimerComplete() {
  // ポモドーロ完了時のみXP付与（休憩は除く）
  if (currentMinutes === 25) {
    try {
      const res = await fetch("/api/pomodoro/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ duration_minutes: currentMinutes }),
      });
      const data = await res.json();
      if (data.success) {
        updateXpDisplay(data.xp);
        updateStreakDisplay(data.streak);
        if (data.new_badges && data.new_badges.length > 0) {
          showBadgeNotifications(data.new_badges);
        }
        await loadStats();
        await loadChart(currentChartType);
      }
    } catch (e) {
      console.error("完了API呼び出しエラー:", e);
    }
  }
  new Audio().play().catch(() => {}); // サウンド不可の場合は無視
}

// --- モード切替 ---
modeButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    modeButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentMinutes = parseInt(btn.dataset.minutes, 10);
    resetTimer();
  });
});

startBtn.addEventListener("click", startTimer);
resetBtn.addEventListener("click", resetTimer);

// --- XP表示 ---
function updateXpDisplay(xp) {
  document.getElementById("level-label").textContent = `Lv.${xp.level}`;
  document.getElementById("xp-bar-fill").style.width = `${xp.percentage}%`;
  document.getElementById("xp-label").textContent =
    `${xp.xp_progress} / ${xp.xp_needed} XP`;
}

// --- ストリーク表示 ---
function updateStreakDisplay(streak) {
  document.getElementById("streak-count").textContent = streak;
}

// --- 統計取得・表示 ---
async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    document.getElementById("stat-total").textContent = data.total_sessions;
    document.getElementById("stat-week").textContent = data.sessions_this_week;
    document.getElementById("stat-month").textContent = data.sessions_this_month;
    updateXpDisplay(data.xp);
    updateStreakDisplay(data.streak);

    // 今日のセッション数を週間データから取得
    const weeklyRes = await fetch("/api/stats/weekly");
    const weeklyData = await weeklyRes.json();
    const today = new Date().toISOString().split("T")[0];
    const todayEntry = weeklyData.weekly.find((d) => d.date === today);
    document.getElementById("stat-today").textContent =
      todayEntry ? todayEntry.count : 0;

    renderBadges(data.badges);
  } catch (e) {
    console.error("統計取得エラー:", e);
  }
}

// --- バッジ表示 ---
function renderBadges(badges) {
  badgesGrid.innerHTML = "";
  badges.forEach((badge) => {
    const div = document.createElement("div");
    div.className = `badge-item ${badge.earned ? "earned" : "locked"}`;
    div.innerHTML = `
      <div class="badge-icon">${badge.icon}</div>
      <div class="badge-name">${badge.name}</div>
      <div class="badge-desc">${badge.description}</div>
    `;
    if (badge.earned && badge.earned_at) {
      const d = new Date(badge.earned_at);
      div.title = `獲得日: ${d.toLocaleDateString("ja-JP")}`;
    }
    badgesGrid.appendChild(div);
  });
}

// --- バッジ通知 ---
function showBadgeNotifications(badges) {
  let delay = 0;
  badges.forEach((badge) => {
    if (!badge) return;
    setTimeout(() => showSingleNotification(badge), delay);
    delay += 3500;
  });
}

function showSingleNotification(badge) {
  document.getElementById("notif-icon").textContent = badge.icon;
  document.getElementById("notif-name").textContent = badge.name;
  notification.style.display = "block";
  setTimeout(() => {
    notification.style.display = "none";
  }, 3000);
}

// --- グラフ ---
async function loadChart(type) {
  const url = type === "weekly" ? "/api/stats/weekly" : "/api/stats/monthly";
  try {
    const res = await fetch(url);
    const data = await res.json();

    const entries = type === "weekly" ? data.weekly : data.monthly;
    const labels = entries.map((e) => (type === "weekly" ? e.date.slice(5) : e.label));
    const counts = entries.map((e) => e.count);

    if (statsChart) {
      statsChart.destroy();
    }

    const ctx = document.getElementById("stats-chart").getContext("2d");
    statsChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "ポモドーロ回数",
            data: counts,
            backgroundColor: "rgba(52, 152, 219, 0.7)",
            borderColor: "rgba(52, 152, 219, 1)",
            borderWidth: 1,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              color: "#a0a0b0",
            },
            grid: { color: "rgba(255,255,255,0.05)" },
          },
          x: {
            ticks: { color: "#a0a0b0" },
            grid: { display: false },
          },
        },
      },
    });
  } catch (e) {
    console.error("グラフ取得エラー:", e);
  }
}

chartTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    chartTabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    currentChartType = tab.dataset.chart;
    loadChart(currentChartType);
  });
});

// --- 初期化 ---
(async function init() {
  updateDisplay();
  await loadStats();
  await loadChart("weekly");
})();
